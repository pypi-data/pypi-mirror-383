"""Teradata target plugin for LakePipe."""

import subprocess
import tempfile
from typing import Dict, Any, Optional
from pathlib import Path
from datetime import datetime

from ..core.base import TargetPlugin, TransferMetrics
from ..utils.logger import get_logger

logger = get_logger(__name__)


class TeradataTarget(TargetPlugin):
    """Teradata target using TPT (Teradata Parallel Transporter) or BTEQ."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize Teradata target.

        Args:
            config: Configuration dictionary with:
                - host: Teradata host
                - database: Target database
                - table: Target table
                - user: Username
                - password: Password
                - loader: Loader type ('tpt' or 'jdbc')
                - loader_config: Loader-specific configuration
                - mode: Load mode ('append', 'overwrite', 'truncate')
        """
        super().__init__(config)
        self.host = config.get("host")
        self.database = config.get("database")
        self.table = config.get("table")
        self.user = config.get("user")
        self.password = config.get("password")
        self.loader = config.get("loader", "tpt")
        self.mode = config.get("mode", "append")

        # Loader config
        loader_config = config.get("loader_config") or {}
        self.max_sessions = loader_config.get("max_sessions", 32)
        self.min_sessions = loader_config.get("min_sessions", 16)
        self.buffer_size = loader_config.get("buffer_size", 4096)
        self.error_limit = loader_config.get("error_limit", 50000)
        self.docker_image = loader_config.get("docker_image", "teradata/tpt:17.20.42.00")

    def connect(self) -> None:
        """Verify connection to Teradata."""
        logger.debug(f"Verifying Teradata connection to {self.host}")

        # Check if Docker is available (required for TPT)
        if self.loader == "tpt":
            try:
                result = subprocess.run(
                    ["docker", "--version"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode != 0:
                    raise RuntimeError("Docker not available")
            except FileNotFoundError:
                raise RuntimeError(
                    "Docker not found. TPT loader requires Docker. "
                    "Install Docker or use loader='jdbc'"
                )

    def disconnect(self) -> None:
        """Disconnect from Teradata."""
        pass

    def _prepare_table(self) -> None:
        """Prepare target table based on load mode."""
        if self.mode in ["overwrite", "truncate"]:
            logger.info(f"Truncating table {self.database}.{self.table}")

            bteq_sql = f"""
.LOGON {self.host}/{self.user},{self.password}

-- Release any MLOAD locks
.IF ERRORCODE <> 0 THEN .GOTO TRUNCATE_TABLE;
RELEASE MLOAD {self.database}.{self.table};

.LABEL TRUNCATE_TABLE
-- Truncate the table
DELETE FROM {self.database}.{self.table} ALL;

.IF ERRORCODE <> 0 THEN .QUIT 12;

.LOGOFF
.QUIT 0
"""

            self._execute_bteq(bteq_sql)

    def _execute_bteq(self, sql: str) -> str:
        """Execute BTEQ command via Docker.

        Args:
            sql: BTEQ SQL script

        Returns:
            Command output
        """
        # Create temporary script file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.bteq', delete=False) as f:
            f.write(sql)
            script_path = Path(f.name)

        try:
            cmd = [
                "docker", "run", "--rm", "-i",
                "-e", "accept_license=Y",
                "--network=host",
                "--entrypoint", "bteq",
                self.docker_image
            ]

            result = subprocess.run(
                cmd,
                input=sql,
                capture_output=True,
                text=True,
                timeout=600
            )

            if result.returncode != 0:
                raise RuntimeError(f"BTEQ failed: {result.stderr}")

            return result.stdout

        finally:
            script_path.unlink(missing_ok=True)

    def _generate_tpt_script(
        self,
        source_path: Path,
        run_timestamp: str
    ) -> Path:
        """Generate TPT load script.

        Args:
            source_path: Path to source data files
            run_timestamp: Timestamp for unique naming

        Returns:
            Path to generated TPT script
        """
        script_path = source_path.parent / f"load_{run_timestamp}.tpt"

        tpt_script = f"""
DEFINE JOB LOAD_{run_timestamp}
DESCRIPTION 'LakePipe Load - {self.database}.{self.table}'
(
    DEFINE SCHEMA DATA_SCHEMA
    (
        -- Schema will be auto-detected from files
        -- This is a placeholder
        col1 VARCHAR(255)
    );

    DEFINE OPERATOR DDL_SETUP
    TYPE DDL
    ATTRIBUTES
    (
        VARCHAR TdpId = '{self.host}',
        VARCHAR UserName = '{self.user}',
        VARCHAR UserPassword = '{self.password}',
        VARCHAR ErrorList = '3807'
    );

    DEFINE OPERATOR FILE_READER
    TYPE DATACONNECTOR PRODUCER
    SCHEMA DATA_SCHEMA
    ATTRIBUTES
    (
        VARCHAR FileName = '{source_path}/*',
        VARCHAR Format = 'Delimited',
        VARCHAR TextDelimiter = '|',
        VARCHAR OpenMode = 'Read',
        INTEGER SkipRows = 0,
        VARCHAR ErrorMode = 'Skip',
        INTEGER BufferSize = {self.buffer_size}
    );

    DEFINE OPERATOR TD_LOADER
    TYPE LOAD
    SCHEMA *
    ATTRIBUTES
    (
        VARCHAR TdpId = '{self.host}',
        VARCHAR UserName = '{self.user}',
        VARCHAR UserPassword = '{self.password}',
        VARCHAR TargetTable = '{self.database}.{self.table}',
        VARCHAR LogTable = '{self.database}.load_log_{run_timestamp}',
        VARCHAR ErrorTable1 = '{self.database}.error1_{run_timestamp}',
        VARCHAR ErrorTable2 = '{self.database}.error2_{run_timestamp}',
        INTEGER MaxSessions = {self.max_sessions},
        INTEGER MinSessions = {self.min_sessions},
        INTEGER BufferSize = {self.buffer_size},
        INTEGER ErrorLimit = {self.error_limit}
    );

    STEP DROP_ERROR_TABLE1
    (
        APPLY ('DROP TABLE {self.database}.error1_{run_timestamp};')
        TO OPERATOR (DDL_SETUP);
    );

    STEP DROP_ERROR_TABLE2
    (
        APPLY ('DROP TABLE {self.database}.error2_{run_timestamp};')
        TO OPERATOR (DDL_SETUP);
    );

    STEP DROP_LOG_TABLE
    (
        APPLY ('DROP TABLE {self.database}.load_log_{run_timestamp};')
        TO OPERATOR (DDL_SETUP);
    );

    STEP LOAD_DATA
    (
        APPLY TO OPERATOR (TD_LOADER[{self.min_sessions}])
        SELECT * FROM OPERATOR (FILE_READER[8]);
    );
);
"""

        with open(script_path, 'w') as f:
            f.write(tpt_script)

        return script_path

    def _execute_tpt(self, script_path: Path, source_path: Path) -> TransferMetrics:
        """Execute TPT load via Docker.

        Args:
            script_path: Path to TPT script
            source_path: Path to source data

        Returns:
            TransferMetrics from load
        """
        run_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        logger.info(f"Executing TPT load with {self.max_sessions} sessions")

        cmd = [
            "docker", "run", "--rm",
            "-e", "accept_license=Y",
            "--memory=32g",
            "--cpus=16",
            "--shm-size=2g",
            "-v", f"{source_path.absolute()}:{source_path.absolute()}:ro",
            "-v", f"{script_path.parent.absolute()}:/scripts:ro",
            "--network=host",
            "--entrypoint", "tbuild",
            self.docker_image,
            "-f", f"/scripts/{script_path.name}",
            "-j", f"load_{run_timestamp}",
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=14400  # 4 hour timeout
        )

        if result.returncode != 0:
            raise RuntimeError(f"TPT load failed: {result.stderr}")

        # Parse TPT output for metrics
        metrics = TransferMetrics()

        # This is simplified - real parsing would extract actual metrics
        metrics.rows_loaded = self.get_row_count(f"{self.database}.{self.table}")

        logger.info(f"✓ TPT load completed: {metrics.rows_loaded:,} rows")

        return metrics

    def load(
        self,
        source_path: Path,
        table: str,
        mode: str = "append",
        **kwargs
    ) -> TransferMetrics:
        """Load data into Teradata.

        Args:
            source_path: Path to source data files
            table: Target table name
            mode: Load mode ('append', 'overwrite', 'truncate')
            **kwargs: Additional load parameters

        Returns:
            TransferMetrics: Metrics from the load operation
        """
        logger.info(f"Loading data to {self.database}.{table} (mode={mode})")

        # Prepare table
        self._prepare_table()

        # Load based on loader type
        if self.loader == "tpt":
            run_timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            script_path = self._generate_tpt_script(source_path, run_timestamp)
            metrics = self._execute_tpt(script_path, source_path)
        else:
            raise ValueError(f"Unsupported loader: {self.loader}")

        return metrics

    def validate_target(self, table: str) -> bool:
        """Validate that target table exists and is accessible.

        Args:
            table: Target table name

        Returns:
            True if target is valid
        """
        sql = f"""
.LOGON {self.host}/{self.user},{self.password}
SELECT 1 FROM {self.database}.{table} SAMPLE 1;
.LOGOFF
.QUIT
"""

        try:
            self._execute_bteq(sql)
            return True
        except:
            return False

    def get_row_count(self, table: str) -> int:
        """Get row count from target table.

        Args:
            table: Target table name

        Returns:
            Row count
        """
        sql = f"""
.LOGON {self.host}/{self.user},{self.password}
.SET WIDTH 255
.SET TITLEDASHES OFF
SELECT CAST(COUNT(*) AS BIGINT) FROM {table};
.LOGOFF
.QUIT
"""

        try:
            output = self._execute_bteq(sql)
            # Parse output to extract count
            for line in output.splitlines():
                line = line.strip()
                if line.isdigit():
                    return int(line)
            return 0
        except Exception as e:
            logger.error(f"Could not get row count: {e}")
            return 0

    def execute_sql(self, sql: str) -> Any:
        """Execute SQL statement on Teradata.

        Args:
            sql: SQL statement

        Returns:
            Query result
        """
        bteq_sql = f"""
.LOGON {self.host}/{self.user},{self.password}
{sql}
.LOGOFF
.QUIT
"""

        return self._execute_bteq(bteq_sql)
