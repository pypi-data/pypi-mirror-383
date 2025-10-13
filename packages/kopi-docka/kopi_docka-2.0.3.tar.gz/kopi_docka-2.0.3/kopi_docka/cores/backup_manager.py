################################################################################
# KOPI-DOCKA
#
# @file:        backup_manager.py
# @module:      kopi_docka.cores
# @description: Orchestriert Cold-Backups: Stop -> Rezepte -> Volumes -> Start.
# @author:      Markus F. (TZERO78) & KI-Assistenten
# @repository:  https://github.com/TZERO78/kopi-docka
# @version:     1.0.0
#
# ------------------------------------------------------------------------------
# Copyright (c) 2025 Markus F. (TZERO78)
# MIT-Lizenz: siehe LICENSE oder https://opensource.org/licenses/MIT
# ==============================================================================
# Hinweise:
# - Alle Snapshots eines Laufs teilen sich dieselbe 'backup_id' (Pflicht-Tag)
# - Rezepte: Compose + docker inspect (ENV-Secrets redacted)
# - Volumes: tar-Stream mit Owner/ACLs/xattrs, deterministische mtimes
################################################################################
"""
Backup management module for Kopi-Docka.

Cold backup strategy:
1) Stop containers
2) Backup recipes (compose + inspect with secrets redacted)
3) Backup volumes (tar stream → Kopia)
4) Start containers
5) Optionally update disaster recovery bundle
"""

import json
import subprocess
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from ..helpers.logging import get_logger
from ..types import BackupUnit, ContainerInfo, VolumeInfo, BackupMetadata
from ..helpers.config import Config
from ..cores.repository_manager import KopiaRepository
from ..cores.kopia_policy_manager import KopiaPolicyManager
from ..helpers.constants import (
    CONTAINER_STOP_TIMEOUT,
    CONTAINER_START_TIMEOUT,
    RECIPE_BACKUP_DIR,
    VOLUME_BACKUP_DIR,
)

logger = get_logger(__name__)


class BackupManager:
    """Orchestrates cold backups for Docker units."""

    def __init__(self, config: Config):
        self.config = config
        self.repo = KopiaRepository(config)
        self.policy_manager = KopiaPolicyManager(self.repo)
        self.max_workers = config.parallel_workers

        self.stop_timeout = self.config.getint(
            "backup", "stop_timeout", CONTAINER_STOP_TIMEOUT
        )
        self.start_timeout = self.config.getint(
            "backup", "start_timeout", CONTAINER_START_TIMEOUT
        )

        self.exclude_patterns = self.config.getlist("backup", "exclude_patterns", [])

    def backup_unit(
        self, unit: BackupUnit, update_recovery_bundle: bool = None
    ) -> BackupMetadata:
        """
        Perform full cold backup of a unit.

        Returns:
            BackupMetadata
        """
        logger.info(
            f"Starting backup of unit: {unit.name}", extra={"unit_name": unit.name}
        )
        start_time = time.time()
        
        # Create a consistent backup_id for all snapshots in this run (required)
        backup_id = str(uuid.uuid4())
        
        metadata = BackupMetadata(
            unit_name=unit.name,
            timestamp=datetime.now(),
            duration_seconds=0,
            backup_id=backup_id,
        )

        try:
            # Apply retention policies up front
            self._ensure_policies(unit)

            # 1) Stop containers
            logger.info(
                f"Stopping {len(unit.containers)} containers...",
                extra={"unit_name": unit.name},
            )
            self._stop_containers(unit.containers)

            # 2) Recipes
            logger.info("Backing up recipes...", extra={"unit_name": unit.name})
            recipe_snapshot = self._backup_recipes(unit, backup_id)
            if recipe_snapshot:
                metadata.kopia_snapshot_ids.append(recipe_snapshot)

            # 3) Volumes (parallel)
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                futures = []
                for volume in unit.volumes:
                    futures.append(
                        (
                            volume.name,
                            executor.submit(
                                self._backup_volume, volume, unit, backup_id
                            ),
                        )
                    )

                task_timeout = max(0, self.config.getint("backup", "task_timeout", 0))
                for vol_name, fut in futures:
                    try:
                        snap_id = fut.result(timeout=task_timeout or None)
                        if snap_id:
                            metadata.kopia_snapshot_ids.append(snap_id)
                            metadata.volumes_backed_up += 1
                            logger.debug(
                                f"Completed volume backup: {vol_name}",
                                extra={"unit_name": unit.name, "volume": vol_name},
                            )
                        else:
                            metadata.errors.append(
                                f"Failed to backup volume: {vol_name}"
                            )
                            logger.warning(
                                f"No snapshot created for volume: {vol_name}",
                                extra={"unit_name": unit.name},
                            )
                    except Exception as e:
                        metadata.errors.append(
                            f"Error backing up volume {vol_name}: {str(e)}"
                        )
                        logger.error(
                            f"Exception during volume backup {vol_name}: {e}",
                            extra={"unit_name": unit.name},
                        )

        except Exception as e:
            metadata.errors.append(f"Backup failed: {str(e)}")
            logger.error(
                f"Critical error during backup: {e}", extra={"unit_name": unit.name}
            )

        finally:
            # 4) Always try to restart containers
            logger.info(
                f"Starting {len(unit.containers)} containers...",
                extra={"unit_name": unit.name},
            )
            self._start_containers(unit.containers)

        # Duration & success
        metadata.duration_seconds = time.time() - start_time
        metadata.success = len(metadata.errors) == 0

        # Save metadata JSON
        self._save_metadata(metadata)

        # 5) Optional DR bundle
        should_update_bundle = update_recovery_bundle
        if should_update_bundle is None:
            should_update_bundle = self.config.getboolean(
                "backup", "update_recovery_bundle", False
            )

        if should_update_bundle and metadata.success:
            logger.info(
                "Updating disaster recovery bundle...", extra={"operation": "dr_bundle"}
            )
            try:
                from ..cores.disaster_recovery_manager import DisasterRecoveryManager

                dr_manager = DisasterRecoveryManager(self.config)
                dr_manager.create_recovery_bundle()
            except Exception as e:
                logger.error(
                    f"Failed to update disaster recovery bundle: {e}",
                    extra={"operation": "dr_bundle"},
                )

        # Final log
        if metadata.errors:
            logger.warning(
                f"Backup of {unit.name} completed with errors in {metadata.duration_seconds:.2f}s",
                extra={
                    "unit_name": unit.name,
                    "duration": metadata.duration_seconds,
                    "errors": len(metadata.errors),
                },
            )
        else:
            logger.info(
                f"Backup of {unit.name} completed successfully in {metadata.duration_seconds:.2f}s",
                extra={"unit_name": unit.name, "duration": metadata.duration_seconds},
            )

        return metadata

    def _stop_containers(self, containers: List[ContainerInfo]):
        """Stop containers gracefully."""
        for c in containers:
            if c.is_running:
                try:
                    subprocess.run(
                        ["docker", "stop", "-t", str(self.stop_timeout), c.id],
                        check=True,
                        capture_output=True,
                    )
                    logger.debug(
                        f"Stopped container: {c.name}", extra={"container": c.name}
                    )
                except subprocess.CalledProcessError as e:
                    logger.error(
                        f"Failed to stop container {c.name}: {e.stderr.decode()}",
                        extra={"container": c.name},
                    )

    def _start_containers(self, containers: List[ContainerInfo]):
        """Start containers in original order and wait (healthcheck if present)."""
        for c in containers:
            try:
                subprocess.run(
                    ["docker", "start", c.id], check=True, capture_output=True
                )
                logger.debug(
                    f"Started container: {c.name}", extra={"container": c.name}
                )
                self._wait_container_healthy(c, timeout=self.start_timeout)
            except subprocess.CalledProcessError as e:
                logger.error(
                    f"Failed to start container {c.name}: {e.stderr.decode()}",
                    extra={"container": c.name},
                )

    def _wait_container_healthy(self, container: ContainerInfo, timeout: int = 60):
        """If healthcheck exists, poll until healthy/unhealthy/timeout; else short sleep."""
        try:
            insp = subprocess.check_output(
                ["docker", "inspect", "-f", "{{json .State.Health}}", container.id],
                text=True,
            ).strip()
            if insp in ("null", "{}", ""):
                time.sleep(2)
                return

            start = time.time()
            while time.time() - start < timeout:
                status = subprocess.check_output(
                    [
                        "docker",
                        "inspect",
                        "-f",
                        "{{.State.Health.Status}}",
                        container.id,
                    ],
                    text=True,
                ).strip()
                if status == "healthy":
                    logger.debug(
                        f"Container {container.name} is healthy",
                        extra={"container": container.name},
                    )
                    return
                if status == "unhealthy":
                    logger.warning(
                        f"Container {container.name} is unhealthy",
                        extra={"container": container.name},
                    )
                    return
                time.sleep(2)

            logger.warning(
                f"Container {container.name} not healthy after {timeout}s",
                extra={"container": container.name},
            )
        except Exception as e:
            logger.debug(
                f"Health check failed for {container.name}: {e}",
                extra={"container": container.name},
            )
            time.sleep(2)

    def _backup_recipes(self, unit: BackupUnit, backup_id: str) -> Optional[str]:
        """Backup compose files and container inspect data (with secret redaction)."""
        try:
            import tempfile

            with tempfile.TemporaryDirectory() as tmpdir:
                tmpdir = Path(tmpdir)

                # Compose file
                if unit.compose_file and unit.compose_file.exists():
                    (tmpdir / "docker-compose.yml").write_text(
                        unit.compose_file.read_text()
                    )

                # Inspect (redact env secrets)
                import json as _json

                SENSITIVE = (
                    "PASS",
                    "SECRET",
                    "KEY",
                    "TOKEN",
                    "CREDENTIAL",
                    "API",
                    "AUTH",
                )
                for c in unit.containers:
                    raw = subprocess.run(
                        ["docker", "inspect", c.id],
                        capture_output=True,
                        text=True,
                        check=True,
                    ).stdout
                    data = _json.loads(raw)
                    if isinstance(data, list) and data:
                        cfg = data[0].get("Config", {})
                        if cfg and "Env" in cfg and isinstance(cfg["Env"], list):
                            red = []
                            for e in cfg["Env"]:
                                k, _, v = e.partition("=")
                                if any(s in k.upper() for s in SENSITIVE):
                                    red.append(f"{k}=***REDACTED***")
                                else:
                                    red.append(e)
                            data[0]["Config"]["Env"] = red
                    (tmpdir / f"{c.name}_inspect.json").write_text(
                        _json.dumps(data, indent=2)
                    )

                # Snapshot
                return self.repo.create_snapshot(
                    str(tmpdir),
                    tags={
                        "type": "recipe",
                        "unit": unit.name,
                        "backup_id": backup_id,
                        "timestamp": datetime.now().isoformat(),
                    },
                )
        except Exception as e:
            logger.error(
                f"Failed to backup recipes for {unit.name}: {e}",
                extra={"unit_name": unit.name},
            )
            return None

    def _backup_volume(
        self, volume: VolumeInfo, unit: BackupUnit, backup_id: str
    ) -> Optional[str]:
        """Backup a single volume via tar stream → Kopia."""
        try:
            logger.debug(
                f"Backing up volume: {volume.name}",
                extra={
                    "unit_name": unit.name,
                    "volume": volume.name,
                    "size_bytes": getattr(volume, "size_bytes", 0),
                },
            )

            tar_cmd = [
                "tar",
                "-cf",
                "-",
                "--numeric-owner",
                "--xattrs",
                "--acls",
                "--one-file-system",
                "--mtime=@0",
                "--clamp-mtime",
                "--sort=name",
            ]
            for pattern in self.exclude_patterns:
                tar_cmd.extend(["--exclude", pattern])
            tar_cmd.extend(["-C", volume.mountpoint, "."])

            tar_process = subprocess.Popen(
                tar_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )

            snap_id = self.repo.create_snapshot_from_stdin(
                tar_process.stdout,
                dest_virtual_path=f"{VOLUME_BACKUP_DIR}/{unit.name}/{volume.name}",  # ← FIX!
                tags={
                    "type": "volume",
                    "unit": unit.name,
                    "volume": volume.name,
                    "backup_id": backup_id,
                    "timestamp": datetime.now().isoformat(),
                    "size_bytes": str(getattr(volume, "size_bytes", 0) or "0"),
                },
            )

            tar_process.wait()
            if tar_process.stdout:
                tar_process.stdout.close()

            if tar_process.returncode != 0:
                stderr = tar_process.stderr.read().decode()
                logger.error(
                    f"Tar failed for volume {volume.name}: {stderr}",
                    extra={"unit_name": unit.name, "volume": volume.name},
                )
                return None

            return snap_id
        except Exception as e:
            logger.error(
                f"Failed to backup volume {volume.name}: {e}",
                extra={"unit_name": unit.name, "volume": volume.name},
            )
            return None

    def _save_metadata(self, metadata: BackupMetadata):
        """Persist backup metadata JSON."""
        metadata_dir = self.config.backup_base_path / "metadata"
        metadata_dir.mkdir(parents=True, exist_ok=True)
        filename = (
            f"{metadata.unit_name}_{metadata.timestamp.strftime('%Y%m%d_%H%M%S')}.json"
        )
        with open(metadata_dir / filename, "w") as f:
            json.dump(metadata.to_dict(), f, indent=2)
        logger.debug(
            f"Saved metadata to {metadata_dir / filename}",
            extra={"unit_name": metadata.unit_name},
        )

    def _ensure_policies(self, unit: BackupUnit):
        """Set Kopia retention policies for this unit (volumes + recipes)."""
        targets = [
            f"{VOLUME_BACKUP_DIR}/{unit.name}",
            f"{RECIPE_BACKUP_DIR}/{unit.name}",
        ]

        for target in targets:
            try:
                self.policy_manager.set_retention_for_target(
                    target,
                    keep_daily=self.config.getint("retention", "daily", 7),
                    keep_weekly=self.config.getint("retention", "weekly", 4),
                    keep_monthly=self.config.getint("retention", "monthly", 12),
                    # keep_yearly intentionally omitted (Kopia 0.21 doesn't support it)
                )
                logger.debug(
                    f"Applied Kopia retention policy on {target}",
                    extra={"unit_name": unit.name, "target": target},
                )
            except Exception as e:
                logger.warning(
                    f"Could not apply Kopia policy on {target}: {e}",
                    extra={"unit_name": unit.name, "target": target},
                )
