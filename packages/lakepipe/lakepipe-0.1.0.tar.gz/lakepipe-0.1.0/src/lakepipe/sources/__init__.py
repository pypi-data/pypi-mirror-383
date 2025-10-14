"""Source plugins for LakePipe."""

from typing import Dict, Any
from ..core.base import SourcePlugin


def get_source_plugin(plugin_type: str, config: Dict[str, Any]) -> SourcePlugin:
    """Factory function to get source plugin by type.

    Args:
        plugin_type: Type of source plugin (e.g., 'hive', 'postgres')
        config: Plugin configuration

    Returns:
        SourcePlugin instance

    Raises:
        ValueError: If plugin type is not supported
    """
    plugin_type = plugin_type.lower()

    if plugin_type == "hive":
        from .hive import HiveSource
        return HiveSource(config)
    elif plugin_type == "postgres":
        from .postgres import PostgresSource
        return PostgresSource(config)
    else:
        raise ValueError(f"Unsupported source plugin: {plugin_type}")


__all__ = ["get_source_plugin"]