"""
omnifetch - Multi-source data retrieval with intelligent caching

Fetch data from anywhere, any type - with automatic TTL-based caching,
multiple storage backends, and smart synchronization.
"""

from .data_manager import DataManager, FileSpec
from .cache_manager import CacheManager
from .sync_manager import SyncManager
from .data_source_config import DataSourceConfig, create_data_source_config
from .adapters.yaml_config import create_datamanager_config

__version__ = "1.0.0"

__all__ = [
    "DataManager",
    "FileSpec",
    "CacheManager",
    "SyncManager",
    "DataSourceConfig",
    "create_data_source_config",
    "create_datamanager_config",
]