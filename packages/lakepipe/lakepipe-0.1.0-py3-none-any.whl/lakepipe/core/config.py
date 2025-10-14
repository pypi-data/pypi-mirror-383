"""Configuration parsing and validation for LakePipe."""

from typing import Any, Dict, Optional, List
from pathlib import Path
from pydantic import BaseModel, Field, field_validator
import yaml


class SourceConfig(BaseModel):
    """Source configuration."""
    type: str = Field(..., description="Source plugin type (e.g., 'hive', 'postgres')")
    database: Optional[str] = None
    table: Optional[str] = None
    query: Optional[str] = None
    partition_by: Optional[str] = None
    format: str = "parquet"
    config: Dict[str, Any] = Field(default_factory=dict, description="Plugin-specific config")

    @field_validator("type")
    @classmethod
    def validate_type(cls, v):
        """Validate source type."""
        if not v:
            raise ValueError("Source type is required")
        return v.lower()


class StorageConfig(BaseModel):
    """Storage configuration."""
    type: str = Field(..., description="Storage plugin type (e.g., 's3', 'gcs', 'obs')")
    bucket: str = Field(..., description="Storage bucket name")
    path: str = Field(default="/staging", description="Path within bucket")
    compression: Optional[str] = Field(default="snappy", description="Compression type")
    cleanup: bool = Field(default=True, description="Cleanup after successful load")
    parallel: int = Field(default=10, description="Parallel upload/download threads")
    config: Dict[str, Any] = Field(default_factory=dict, description="Plugin-specific config")

    @field_validator("type")
    @classmethod
    def validate_type(cls, v):
        """Validate storage type."""
        if not v:
            raise ValueError("Storage type is required")
        return v.lower()


class LoaderConfig(BaseModel):
    """Target loader configuration."""
    max_sessions: Optional[int] = Field(default=32, description="Max loader sessions")
    min_sessions: Optional[int] = Field(default=16, description="Min loader sessions")
    buffer_size: Optional[int] = Field(default=4096, description="Buffer size")
    error_limit: Optional[int] = Field(default=50000, description="Max errors before abort")
    docker_image: Optional[str] = None
    config: Dict[str, Any] = Field(default_factory=dict)


class TargetConfig(BaseModel):
    """Target configuration."""
    type: str = Field(..., description="Target plugin type (e.g., 'teradata', 'snowflake')")
    host: str
    database: str
    table: str
    user: Optional[str] = None
    password: Optional[str] = None
    loader: str = Field(default="jdbc", description="Loader type (e.g., 'tpt', 'jdbc')")
    loader_config: Optional[LoaderConfig] = None
    mode: str = Field(default="append", description="Load mode: append, overwrite, truncate")
    config: Dict[str, Any] = Field(default_factory=dict)

    @field_validator("type")
    @classmethod
    def validate_type(cls, v):
        """Validate target type."""
        if not v:
            raise ValueError("Target type is required")
        return v.lower()

    @field_validator("mode")
    @classmethod
    def validate_mode(cls, v):
        """Validate load mode."""
        valid_modes = ["append", "overwrite", "truncate"]
        if v.lower() not in valid_modes:
            raise ValueError(f"Mode must be one of: {valid_modes}")
        return v.lower()


class TransformationConfig(BaseModel):
    """Transformation configuration."""
    sql: Optional[str] = None
    function: Optional[str] = None
    config: Dict[str, Any] = Field(default_factory=dict)


class RowCountValidation(BaseModel):
    """Row count validation configuration."""
    enabled: bool = True
    max_variance: float = Field(default=0.01, description="Max allowed variance (0.01 = 1%)")


class DataQualityRule(BaseModel):
    """Data quality validation rule."""
    column: str
    not_null: bool = False
    min_value: Optional[Any] = None
    max_value: Optional[Any] = None
    min_date: Optional[str] = None
    max_date: Optional[str] = None
    regex: Optional[str] = None


class ValidationConfig(BaseModel):
    """Validation configuration."""
    row_count: Optional[RowCountValidation] = None
    data_quality: Optional[List[DataQualityRule]] = None
    custom: Optional[List[Dict[str, Any]]] = None


class NotificationConfig(BaseModel):
    """Notification configuration."""
    on_success: Optional[List[str]] = None
    on_failure: Optional[List[str]] = None


class PipelineConfig(BaseModel):
    """Main pipeline configuration."""
    version: str = Field(default="1.0")
    name: str
    description: Optional[str] = None
    source: SourceConfig
    storage: StorageConfig
    target: TargetConfig
    transformations: Optional[List[TransformationConfig]] = None
    validation: Optional[ValidationConfig] = None
    notifications: Optional[NotificationConfig] = None
    params: Dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def from_yaml(cls, yaml_path: Path) -> "PipelineConfig":
        """Load configuration from YAML file.

        Args:
            yaml_path: Path to YAML configuration file

        Returns:
            PipelineConfig instance

        Raises:
            FileNotFoundError: If YAML file doesn't exist
            ValueError: If YAML is invalid
        """
        if not yaml_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {yaml_path}")

        with open(yaml_path, 'r') as f:
            try:
                data = yaml.safe_load(f)
            except yaml.YAMLError as e:
                raise ValueError(f"Invalid YAML: {e}")

        return cls(**data)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PipelineConfig":
        """Load configuration from dictionary.

        Args:
            data: Configuration dictionary

        Returns:
            PipelineConfig instance
        """
        return cls(**data)

    def to_yaml(self, yaml_path: Path) -> None:
        """Save configuration to YAML file.

        Args:
            yaml_path: Path to save YAML file
        """
        with open(yaml_path, 'w') as f:
            yaml.safe_dump(
                self.model_dump(exclude_none=True),
                f,
                default_flow_style=False,
                sort_keys=False
            )

    def merge_params(self, runtime_params: Dict[str, Any]) -> None:
        """Merge runtime parameters with config params.

        Args:
            runtime_params: Runtime parameters to merge
        """
        self.params.update(runtime_params)
