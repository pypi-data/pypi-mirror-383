"""Huawei OBS storage plugin for LakePipe."""

import subprocess
from typing import Dict, Any
from pathlib import Path

from ..core.base import StoragePlugin
from ..utils.logger import get_logger

logger = get_logger(__name__)


class OBSStorage(StoragePlugin):
    """Huawei OBS storage using obsutil CLI."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize OBS storage.

        Args:
            config: Configuration dictionary with:
                - bucket: OBS bucket name
                - path: Path within bucket
                - parallel: Number of parallel uploads/downloads
                - config: Additional obsutil configuration
        """
        super().__init__(config)
        self.bucket = config.get("bucket")
        self.path = config.get("path", "/staging")
        self.parallel = config.get("parallel", 10)
        self.obsutil_config = config.get("config", {})

    def connect(self) -> None:
        """Verify obsutil is available."""
        try:
            result = subprocess.run(
                ["obsutil", "version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode != 0:
                raise RuntimeError("obsutil not available or not configured")
            logger.debug("Connected to OBS via obsutil")
        except FileNotFoundError:
            raise RuntimeError(
                "obsutil command not found. Please install Huawei OBS CLI: "
                "https://support.huaweicloud.com/intl/en-us/utiltg-obs/obs_11_0001.html"
            )

    def disconnect(self) -> None:
        """Disconnect from OBS."""
        pass  # No persistent connection for obsutil

    def _build_obs_path(self, remote_path: str) -> str:
        """Build full OBS path.

        Args:
            remote_path: Remote path

        Returns:
            Full OBS URL
        """
        path = remote_path.lstrip("/")
        return f"obs://{self.bucket}/{path}"

    def upload(
        self,
        local_path: Path,
        remote_path: str,
        parallel: int = 1,
        **kwargs
    ) -> None:
        """Upload data to OBS.

        Args:
            local_path: Local file or directory path
            remote_path: Remote path in OBS
            parallel: Number of parallel upload threads
            **kwargs: Additional upload parameters
        """
        obs_path = self._build_obs_path(remote_path)
        parallel_jobs = parallel or self.parallel

        logger.info(f"Uploading {local_path} to {obs_path} (parallel={parallel_jobs})")

        cmd = [
            "obsutil", "cp",
            str(local_path),
            obs_path,
            "-r",  # Recursive
            "-f",  # Force overwrite
            "-j", str(parallel_jobs),  # Parallel jobs
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=7200  # 2 hour timeout
        )

        if result.returncode != 0:
            raise RuntimeError(f"OBS upload failed: {result.stderr}")

        logger.info(f"✓ Uploaded to {obs_path}")

    def download(
        self,
        remote_path: str,
        local_path: Path,
        parallel: int = 1,
        **kwargs
    ) -> None:
        """Download data from OBS.

        Args:
            remote_path: Remote path in OBS
            local_path: Local destination path
            parallel: Number of parallel download threads
            **kwargs: Additional download parameters
        """
        obs_path = self._build_obs_path(remote_path)
        parallel_jobs = parallel or self.parallel

        logger.info(f"Downloading {obs_path} to {local_path} (parallel={parallel_jobs})")

        local_path.mkdir(parents=True, exist_ok=True)

        cmd = [
            "obsutil", "cp",
            obs_path,
            str(local_path),
            "-r",  # Recursive
            "-f",  # Force overwrite
            "-j", str(parallel_jobs),  # Parallel jobs
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=7200  # 2 hour timeout
        )

        if result.returncode != 0:
            raise RuntimeError(f"OBS download failed: {result.stderr}")

        logger.info(f"✓ Downloaded to {local_path}")

    def list_files(self, remote_path: str) -> list[str]:
        """List files in OBS path.

        Args:
            remote_path: Remote path to list

        Returns:
            List of file paths
        """
        obs_path = self._build_obs_path(remote_path)

        cmd = [
            "obsutil", "ls",
            obs_path,
            "-d",  # Directory mode
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60
        )

        if result.returncode != 0:
            raise RuntimeError(f"OBS list failed: {result.stderr}")

        # Parse output
        files = []
        for line in result.stdout.splitlines():
            if line.strip() and not line.startswith("obs://"):
                files.append(line.strip())

        return files

    def delete(self, remote_path: str) -> None:
        """Delete files from OBS.

        Args:
            remote_path: Remote path to delete
        """
        obs_path = self._build_obs_path(remote_path)

        logger.info(f"Deleting {obs_path}")

        cmd = [
            "obsutil", "rm",
            obs_path,
            "-r",  # Recursive
            "-f",  # Force
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=600
        )

        if result.returncode != 0:
            logger.warning(f"OBS delete failed: {result.stderr}")
        else:
            logger.info(f"✓ Deleted {obs_path}")

    def get_size(self, remote_path: str) -> int:
        """Get total size of files in path.

        Args:
            remote_path: Remote path

        Returns:
            Total size in bytes
        """
        obs_path = self._build_obs_path(remote_path)

        cmd = [
            "obsutil", "du",
            obs_path,
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60
        )

        if result.returncode != 0:
            logger.warning(f"Could not get size: {result.stderr}")
            return 0

        # Parse output to get size
        # This is a simplified version
        try:
            size_line = result.stdout.strip().split()[-1]
            return int(size_line)
        except:
            return 0
