"""Pipeline orchestration engine for LakePipe."""

from typing import Optional, Dict, Any
from pathlib import Path
from datetime import datetime
import time
import logging
from enum import Enum

from .config import PipelineConfig
from .base import (
    SourcePlugin, StoragePlugin, TargetPlugin, ValidatorPlugin,
    TransferMetrics, DataEstimate
)
from ..utils.logger import get_logger

logger = get_logger(__name__)


class PipelineStage(Enum):
    """Pipeline execution stages."""
    INIT = "init"
    PLAN = "plan"
    EXTRACT = "extract"
    STAGE = "stage"
    LOAD = "load"
    VALIDATE = "validate"
    CLEANUP = "cleanup"
    COMPLETE = "complete"
    FAILED = "failed"


class PipelineResult:
    """Result of pipeline execution."""

    def __init__(self):
        self.pipeline_id: Optional[str] = None
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.stage: PipelineStage = PipelineStage.INIT
        self.metrics: TransferMetrics = TransferMetrics()
        self.errors: list[str] = []
        self.success: bool = False

    @property
    def duration(self) -> float:
        """Total duration in seconds."""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "pipeline_id": self.pipeline_id,
            "success": self.success,
            "stage": self.stage.value,
            "duration_seconds": self.duration,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "metrics": {
                "rows_extracted": self.metrics.rows_extracted,
                "rows_loaded": self.metrics.rows_loaded,
                "rows_rejected": self.metrics.rows_rejected,
                "bytes_transferred": self.metrics.bytes_transferred,
                "success_rate": self.metrics.success_rate,
                "throughput_rows_per_sec": self.metrics.throughput_rows_per_sec,
            },
            "errors": self.errors,
        }


class Pipeline:
    """LakePipe pipeline orchestration."""

    def __init__(
        self,
        config: PipelineConfig,
        work_dir: Optional[Path] = None
    ):
        """Initialize pipeline.

        Args:
            config: Pipeline configuration
            work_dir: Working directory for intermediate files
        """
        self.config = config
        self.work_dir = work_dir or Path.cwd() / ".lakepipe" / "runs" / datetime.now().strftime("%Y%m%d_%H%M%S")
        self.work_dir.mkdir(parents=True, exist_ok=True)

        self.source: Optional[SourcePlugin] = None
        self.storage: Optional[StoragePlugin] = None
        self.target: Optional[TargetPlugin] = None
        self.validators: list[ValidatorPlugin] = []

        self.result = PipelineResult()
        self.result.pipeline_id = f"{config.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    def _load_plugins(self) -> None:
        """Load and initialize plugins based on configuration."""
        logger.info("Loading plugins...")

        # Import plugin factories
        from ..sources import get_source_plugin
        from ..storage import get_storage_plugin
        from ..targets import get_target_plugin

        # Initialize plugins
        self.source = get_source_plugin(
            self.config.source.type,
            self.config.source.model_dump()
        )

        self.storage = get_storage_plugin(
            self.config.storage.type,
            self.config.storage.model_dump()
        )

        self.target = get_target_plugin(
            self.config.target.type,
            self.config.target.model_dump()
        )

        logger.info(f"Loaded: source={self.config.source.type}, "
                   f"storage={self.config.storage.type}, "
                   f"target={self.config.target.type}")

    def plan(self) -> DataEstimate:
        """Plan pipeline execution and estimate data size.

        Returns:
            DataEstimate: Estimated data size
        """
        logger.info("📋 Planning pipeline execution...")
        self.result.stage = PipelineStage.PLAN

        if not self.source:
            self._load_plugins()

        with self.source:
            estimate = self.source.estimate_size(
                query=self.config.source.query,
                partition=self.config.params
            )

        logger.info(f"Estimated: {estimate.row_count:,} rows, "
                   f"{estimate.size_gb:.2f} GB" if estimate.size_gb else "size unknown")

        return estimate

    def extract(self) -> list[Path]:
        """Extract data from source.

        Returns:
            List of paths to extracted data files
        """
        logger.info("📤 Extracting data from source...")
        self.result.stage = PipelineStage.EXTRACT

        extract_dir = self.work_dir / "extract"
        extract_dir.mkdir(exist_ok=True)

        start_time = time.time()
        extracted_files = []

        with self.source:
            for file_path in self.source.extract(
                query=self.config.source.query,
                partition=self.config.params,
                output_path=extract_dir
            ):
                extracted_files.append(file_path)
                logger.debug(f"Extracted: {file_path}")

        duration = time.time() - start_time
        logger.info(f"✓ Extracted {len(extracted_files)} files in {duration:.1f}s")

        return extracted_files

    def stage(self, local_files: list[Path]) -> str:
        """Upload data to intermediate storage.

        Args:
            local_files: Local files to upload

        Returns:
            Remote storage path
        """
        logger.info("☁️  Staging data to storage...")
        self.result.stage = PipelineStage.STAGE

        remote_path = f"{self.config.storage.path}/{self.result.pipeline_id}"

        with self.storage:
            for local_file in local_files:
                self.storage.upload(
                    local_path=local_file,
                    remote_path=remote_path,
                    parallel=self.config.storage.parallel
                )

        logger.info(f"✓ Staged to {remote_path}")
        return remote_path

    def load(self, storage_path: str) -> TransferMetrics:
        """Load data into target.

        Args:
            storage_path: Path in storage to load from

        Returns:
            TransferMetrics from load operation
        """
        logger.info("📥 Loading data to target...")
        self.result.stage = PipelineStage.LOAD

        # Download from storage to local staging
        staging_dir = self.work_dir / "staging"
        staging_dir.mkdir(exist_ok=True)

        with self.storage:
            self.storage.download(
                remote_path=storage_path,
                local_path=staging_dir,
                parallel=self.config.storage.parallel
            )

        # Load into target
        with self.target:
            metrics = self.target.load(
                source_path=staging_dir,
                table=self.config.target.table,
                mode=self.config.target.mode
            )

        logger.info(f"✓ Loaded {metrics.rows_loaded:,} rows "
                   f"({metrics.throughput_rows_per_sec:.0f} rows/s)")

        return metrics

    def validate(self) -> bool:
        """Validate data transfer.

        Returns:
            True if validation passed
        """
        logger.info("✅ Validating transfer...")
        self.result.stage = PipelineStage.VALIDATE

        if not self.config.validation:
            logger.info("No validation configured, skipping")
            return True

        # Row count validation
        if self.config.validation.row_count and self.config.validation.row_count.enabled:
            with self.target:
                target_count = self.target.get_row_count(self.config.target.table)

            source_count = self.result.metrics.rows_extracted
            if source_count > 0:
                variance = abs(target_count - source_count) / source_count
                max_variance = self.config.validation.row_count.max_variance

                if variance > max_variance:
                    error = (f"Row count variance {variance:.4f} exceeds threshold {max_variance}. "
                            f"Source: {source_count:,}, Target: {target_count:,}")
                    logger.error(error)
                    self.result.errors.append(error)
                    return False

                logger.info(f"✓ Row count validation passed (variance: {variance:.4f})")

        return True

    def cleanup(self, storage_path: str) -> None:
        """Cleanup intermediate files.

        Args:
            storage_path: Storage path to cleanup
        """
        logger.info("🧹 Cleaning up...")
        self.result.stage = PipelineStage.CLEANUP

        if self.config.storage.cleanup:
            with self.storage:
                self.storage.delete(storage_path)
            logger.info(f"✓ Deleted {storage_path}")

    def run(self, runtime_params: Optional[Dict[str, Any]] = None) -> PipelineResult:
        """Execute the complete pipeline.

        Args:
            runtime_params: Runtime parameters to merge with config

        Returns:
            PipelineResult: Execution result
        """
        self.result.start_time = datetime.now()
        logger.info(f"🌊 LakePipe: {self.config.name}")
        logger.info("=" * 60)

        try:
            # Merge runtime parameters
            if runtime_params:
                self.config.merge_params(runtime_params)

            # Load plugins
            self._load_plugins()

            # Execute pipeline stages
            estimate = self.plan()
            self.result.metrics.rows_extracted = estimate.row_count or 0

            extracted_files = self.extract()
            storage_path = self.stage(extracted_files)
            metrics = self.load(storage_path)

            # Update metrics
            self.result.metrics.rows_loaded = metrics.rows_loaded
            self.result.metrics.rows_rejected = metrics.rows_rejected
            self.result.metrics.bytes_transferred = metrics.bytes_transferred

            # Validate
            if not self.validate():
                self.result.stage = PipelineStage.FAILED
                self.result.success = False
                logger.error("❌ Pipeline validation failed")
                return self.result

            # Cleanup
            self.cleanup(storage_path)

            # Success
            self.result.stage = PipelineStage.COMPLETE
            self.result.success = True
            self.result.end_time = datetime.now()

            logger.info("=" * 60)
            logger.info(f"✅ Pipeline completed in {self.result.duration:.1f}s")
            logger.info(f"Rows: {self.result.metrics.rows_loaded:,} loaded, "
                       f"{self.result.metrics.rows_rejected:,} rejected")

        except Exception as e:
            self.result.stage = PipelineStage.FAILED
            self.result.success = False
            self.result.end_time = datetime.now()
            error_msg = f"Pipeline failed: {str(e)}"
            self.result.errors.append(error_msg)
            logger.error(f"❌ {error_msg}", exc_info=True)

        return self.result
