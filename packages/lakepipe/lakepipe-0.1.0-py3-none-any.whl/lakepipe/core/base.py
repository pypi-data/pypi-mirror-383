"""Base classes for LakePipe plugins."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Iterator
from pathlib import Path
from dataclasses import dataclass
from enum import Enum


class PluginType(Enum):
    """Types of plugins supported by LakePipe."""
    SOURCE = "source"
    STORAGE = "storage"
    TARGET = "target"
    VALIDATOR = "validator"


@dataclass
class TransferMetrics:
    """Metrics collected during data transfer."""
    rows_extracted: int = 0
    rows_loaded: int = 0
    rows_rejected: int = 0
    bytes_transferred: int = 0
    duration_seconds: float = 0.0
    throughput_rows_per_sec: float = 0.0

    @property
    def success_rate(self) -> float:
        """Calculate success rate."""
        if self.rows_extracted == 0:
            return 0.0
        return (self.rows_loaded / self.rows_extracted) * 100


@dataclass
class DataEstimate:
    """Estimated data size before extraction."""
    row_count: Optional[int] = None
    size_bytes: Optional[int] = None
    partition_count: Optional[int] = None

    @property
    def size_gb(self) -> Optional[float]:
        """Size in GB."""
        if self.size_bytes is None:
            return None
        return self.size_bytes / (1024 ** 3)


class BasePlugin(ABC):
    """Base class for all LakePipe plugins."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize plugin with configuration.

        Args:
            config: Plugin-specific configuration dictionary
        """
        self.config = config
        self._connection = None

    @abstractmethod
    def connect(self) -> None:
        """Establish connection to the data source/target."""
        pass

    @abstractmethod
    def disconnect(self) -> None:
        """Close connection and cleanup resources."""
        pass

    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()
        return False


class SourcePlugin(BasePlugin):
    """Base class for data source plugins."""

    @abstractmethod
    def extract(
        self,
        query: Optional[str] = None,
        partition: Optional[Dict[str, Any]] = None,
        output_path: Optional[Path] = None,
        **kwargs
    ) -> Iterator[Path]:
        """Extract data from source.

        Args:
            query: Optional SQL query or extraction expression
            partition: Optional partition filters
            output_path: Path to write extracted data
            **kwargs: Additional extraction parameters

        Yields:
            Path: Paths to extracted data files
        """
        pass

    @abstractmethod
    def estimate_size(
        self,
        query: Optional[str] = None,
        partition: Optional[Dict[str, Any]] = None
    ) -> DataEstimate:
        """Estimate data size before extraction.

        Args:
            query: Optional SQL query or extraction expression
            partition: Optional partition filters

        Returns:
            DataEstimate: Estimated row count and size
        """
        pass

    @abstractmethod
    def get_schema(self, table: str) -> Dict[str, Any]:
        """Get schema information for a table.

        Args:
            table: Table name

        Returns:
            Dictionary containing schema information
        """
        pass


class StoragePlugin(BasePlugin):
    """Base class for intermediate storage plugins (S3, GCS, etc.)."""

    @abstractmethod
    def upload(
        self,
        local_path: Path,
        remote_path: str,
        parallel: int = 1,
        **kwargs
    ) -> None:
        """Upload data to storage.

        Args:
            local_path: Local file or directory path
            remote_path: Remote path in storage
            parallel: Number of parallel upload threads
            **kwargs: Additional upload parameters
        """
        pass

    @abstractmethod
    def download(
        self,
        remote_path: str,
        local_path: Path,
        parallel: int = 1,
        **kwargs
    ) -> None:
        """Download data from storage.

        Args:
            remote_path: Remote path in storage
            local_path: Local destination path
            parallel: Number of parallel download threads
            **kwargs: Additional download parameters
        """
        pass

    @abstractmethod
    def list_files(self, remote_path: str) -> list[str]:
        """List files in storage path.

        Args:
            remote_path: Remote path to list

        Returns:
            List of file paths
        """
        pass

    @abstractmethod
    def delete(self, remote_path: str) -> None:
        """Delete files from storage.

        Args:
            remote_path: Remote path to delete
        """
        pass

    @abstractmethod
    def get_size(self, remote_path: str) -> int:
        """Get total size of files in path.

        Args:
            remote_path: Remote path

        Returns:
            Total size in bytes
        """
        pass


class TargetPlugin(BasePlugin):
    """Base class for data target plugins."""

    @abstractmethod
    def load(
        self,
        source_path: Path,
        table: str,
        mode: str = "append",
        **kwargs
    ) -> TransferMetrics:
        """Load data into target.

        Args:
            source_path: Path to source data files
            table: Target table name
            mode: Load mode ('append', 'overwrite', 'truncate')
            **kwargs: Additional load parameters

        Returns:
            TransferMetrics: Metrics from the load operation
        """
        pass

    @abstractmethod
    def validate_target(self, table: str) -> bool:
        """Validate that target table exists and is accessible.

        Args:
            table: Target table name

        Returns:
            True if target is valid
        """
        pass

    @abstractmethod
    def get_row_count(self, table: str) -> int:
        """Get row count from target table.

        Args:
            table: Target table name

        Returns:
            Row count
        """
        pass

    @abstractmethod
    def execute_sql(self, sql: str) -> Any:
        """Execute SQL statement on target.

        Args:
            sql: SQL statement

        Returns:
            Query result
        """
        pass


class ValidatorPlugin(BasePlugin):
    """Base class for validation plugins."""

    @abstractmethod
    def validate(
        self,
        source_metrics: TransferMetrics,
        target_metrics: TransferMetrics,
        **kwargs
    ) -> tuple[bool, str]:
        """Validate data transfer.

        Args:
            source_metrics: Metrics from source extraction
            target_metrics: Metrics from target load
            **kwargs: Additional validation parameters

        Returns:
            Tuple of (is_valid, message)
        """
        pass
