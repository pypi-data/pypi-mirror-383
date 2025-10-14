"""Target plugins for LakePipe."""

from typing import Dict, Any
from ..core.base import TargetPlugin


def get_target_plugin(plugin_type: str, config: Dict[str, Any]) -> TargetPlugin:
    """Factory function to get target plugin by type.

    Args:
        plugin_type: Type of target plugin (e.g., 'teradata', 'snowflake')
        config: Plugin configuration

    Returns:
        TargetPlugin instance

    Raises:
        ValueError: If plugin type is not supported
    """
    plugin_type = plugin_type.lower()

    if plugin_type == "teradata":
        from .teradata import TeradataTarget
        return TeradataTarget(config)
    elif plugin_type == "snowflake":
        from .snowflake import SnowflakeTarget
        return SnowflakeTarget(config)
    elif plugin_type == "bigquery":
        from .bigquery import BigQueryTarget
        return BigQueryTarget(config)
    else:
        raise ValueError(f"Unsupported target plugin: {plugin_type}")


__all__ = ["get_target_plugin"]