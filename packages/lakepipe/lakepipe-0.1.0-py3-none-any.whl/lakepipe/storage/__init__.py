"""Storage plugins for LakePipe."""

from typing import Dict, Any
from ..core.base import StoragePlugin


def get_storage_plugin(plugin_type: str, config: Dict[str, Any]) -> StoragePlugin:
    """Factory function to get storage plugin by type.

    Args:
        plugin_type: Type of storage plugin (e.g., 's3', 'gcs', 'obs')
        config: Plugin configuration

    Returns:
        StoragePlugin instance

    Raises:
        ValueError: If plugin type is not supported
    """
    plugin_type = plugin_type.lower()

    if plugin_type in ["s3", "aws"]:
        from .s3 import S3Storage
        return S3Storage(config)
    elif plugin_type in ["gcs", "google"]:
        from .gcs import GCSStorage
        return GCSStorage(config)
    elif plugin_type in ["obs", "huawei"]:
        from .obs import OBSStorage
        return OBSStorage(config)
    elif plugin_type in ["azure", "azureblob"]:
        from .azure import AzureStorage
        return AzureStorage(config)
    else:
        raise ValueError(f"Unsupported storage plugin: {plugin_type}")


__all__ = ["get_storage_plugin"]