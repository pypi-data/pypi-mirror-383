"""Hive source plugin for LakePipe."""

import subprocess
from typing import Optional, Dict, Any, Iterator
from pathlib import Path
import tempfile

from ..core.base import SourcePlugin, DataEstimate
from ..utils.logger import get_logger

logger = get_logger(__name__)


class HiveSource(SourcePlugin):
    """Hive data source using beeline."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize Hive source.

        Args:
            config: Configuration dictionary with:
                - database: Hive database name
                - table: Hive table name
                - query: Optional custom SQL query
                - partition_by: Optional partition column
                - format: Export format (default: parquet)
                - beeline_url: Optional beeline JDBC URL
                - config: Additional Hive configuration
        """
        super().__init__(config)
        self.database = config.get("database")
        self.table = config.get("table")
        self.query = config.get("query")
        self.partition_by = config.get("partition_by")
        self.format = config.get("format", "parquet")
        self.beeline_url = config.get("beeline_url", "jdbc:hive2://localhost:10000")
        self.hive_config = config.get("config", {})

    def connect(self) -> None:
        """Establish connection to Hive (verify beeline availability)."""
        try:
            result = subprocess.run(
                ["beeline", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode != 0:
                raise RuntimeError("beeline not available or not working")
            logger.debug("Connected to Hive via beeline")
        except FileNotFoundError:
            raise RuntimeError("beeline command not found. Please install Hive client.")

    def disconnect(self) -> None:
        """Disconnect from Hive."""
        pass  # No persistent connection for beeline

    def _build_query(self, partition: Optional[Dict[str, Any]] = None) -> str:
        """Build SQL query for extraction.

        Args:
            partition: Partition filters

        Returns:
            SQL query string
        """
        if self.query:
            # Use custom query
            query = self.query
        else:
            # Build SELECT query
            query = f"SELECT * FROM {self.database}.{self.table}"

        # Add partition filter
        if partition and self.partition_by:
            partition_value = partition.get(self.partition_by)
            if partition_value:
                if "WHERE" in query.upper():
                    query += f" AND {self.partition_by} = '{partition_value}'"
                else:
                    query += f" WHERE {self.partition_by} = '{partition_value}'"

        return query

    def _execute_beeline(self, sql: str, output_format: str = "tsv2") -> str:
        """Execute beeline command.

        Args:
            sql: SQL query
            output_format: Beeline output format

        Returns:
            Command output
        """
        # Build beeline command
        cmd = [
            "beeline",
            "-u", self.beeline_url,
            "--silent=true",
            f"--outputformat={output_format}",
            "-e", sql
        ]

        logger.debug(f"Executing: {' '.join(cmd)}")

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=3600  # 1 hour timeout
        )

        if result.returncode != 0:
            raise RuntimeError(f"Beeline failed: {result.stderr}")

        return result.stdout

    def extract(
        self,
        query: Optional[str] = None,
        partition: Optional[Dict[str, Any]] = None,
        output_path: Optional[Path] = None,
        **kwargs
    ) -> Iterator[Path]:
        """Extract data from Hive.

        Args:
            query: Optional custom SQL query
            partition: Optional partition filters
            output_path: Path to write extracted data
            **kwargs: Additional extraction parameters

        Yields:
            Path: Paths to extracted data files
        """
        if not output_path:
            output_path = Path(tempfile.mkdtemp(prefix="lakepipe_hive_"))

        output_path.mkdir(parents=True, exist_ok=True)

        # Build extraction query
        if query:
            extraction_query = query
        else:
            extraction_query = self._build_query(partition)

        logger.info(f"Extracting data: {extraction_query[:100]}...")

        # Create external table for export
        export_table = f"{self.database}_export_{self.table}_{partition.get(self.partition_by, 'all')}"
        export_path = output_path / "data"

        # Build Hive export SQL
        export_sql = f"""
        SET hive.execution.engine=spark;
        SET hive.merge.mapfiles=true;
        SET hive.merge.mapredfiles=true;

        DROP TABLE IF EXISTS {export_table};

        CREATE EXTERNAL TABLE {export_table}
        STORED AS {self.format.upper()}
        LOCATION '{export_path}'
        AS {extraction_query};
        """

        # Execute export
        try:
            self._execute_beeline(export_sql)
            logger.info(f"Exported to {export_path}")

            # Find exported files
            exported_files = list(export_path.glob("*"))
            for file_path in exported_files:
                if file_path.is_file():
                    yield file_path

        except Exception as e:
            logger.error(f"Export failed: {e}")
            raise

    def estimate_size(
        self,
        query: Optional[str] = None,
        partition: Optional[Dict[str, Any]] = None
    ) -> DataEstimate:
        """Estimate data size before extraction.

        Args:
            query: Optional SQL query
            partition: Optional partition filters

        Returns:
            DataEstimate: Estimated row count and size
        """
        # Build count query
        if query:
            count_query = f"SELECT COUNT(*) FROM ({query}) t"
        else:
            base_query = self._build_query(partition)
            count_query = f"SELECT COUNT(*) FROM ({base_query}) t"

        # Execute count
        try:
            output = self._execute_beeline(count_query, output_format="tsv2")
            row_count = int(output.strip().split()[-1])

            return DataEstimate(row_count=row_count)

        except Exception as e:
            logger.warning(f"Could not estimate size: {e}")
            return DataEstimate()

    def get_schema(self, table: str) -> Dict[str, Any]:
        """Get schema information for a table.

        Args:
            table: Table name (database.table)

        Returns:
            Dictionary containing schema information
        """
        describe_sql = f"DESCRIBE FORMATTED {table}"

        try:
            output = self._execute_beeline(describe_sql)
            # Parse output to extract schema
            # This is a simplified version
            return {"raw_schema": output}

        except Exception as e:
            logger.error(f"Could not get schema: {e}")
            return {}
