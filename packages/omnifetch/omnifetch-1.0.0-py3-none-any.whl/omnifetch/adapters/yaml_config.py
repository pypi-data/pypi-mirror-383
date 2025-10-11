"""
R Config Adapter for DataManager

Converts SIMEG R Toolkit data_sources.yml format to DataManager configuration format.
"""

import os
import yaml
from typing import Dict, Any
from pathlib import Path


def load_r_config(config_path: str = None) -> Dict[str, Any]:
    """
    Load data_sources.yml from R pipeline configuration.

    Args:
        config_path: Path to data_sources.yml file. If None, uses CONFIG_PATH env var.

    Returns:
        Dictionary with R configuration
    """
    if config_path is None:
        config_dir = os.environ.get("CONFIG_PATH", "/app/config")
        config_path = os.path.join(config_dir, "data_sources.yml")

    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def convert_r_config_to_datamanager(r_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert R pipeline config format to DataManager format.

    R format:
        data_sources:
          dataset_name:
            type: "cos_cached" | "local"
            path: "path/to/file.parquet"
            ttl: 86400

    DataManager format:
        storage:
          backend: "ibm_cos" | "local"
          ibm_cos:
            bucket_name: "bucket"
            service_endpoint: "endpoint"
          local:
            base_path: "/path"
        data_sources:
          dataset_name:
            backend: "ibm_cos" | "local"
            ttl_seconds: 86400
            file_patterns:
              default: "path/to/file.parquet"
    """
    # Get storage backend configuration from environment
    storage_config = {
        "backend": "ibm_cos" if os.environ.get("COS_ENDPOINT") else "local",
        "ibm_cos": {
            "bucket_name": os.environ.get("COS_BUCKET", ""),
            "service_endpoint": os.environ.get("COS_ENDPOINT", ""),
            "access_key_env": "COS_ACCESS_KEY",
            "secret_key_env": "COS_SECRET_KEY"
        },
        "local": {
            "base_path": os.environ.get("LOCAL_FILES_CACHE", "/app/cache")
        }
    }

    # Convert data sources
    r_data_sources = r_config.get("data_sources", {})
    defaults = r_config.get("defaults", {})
    default_ttl = defaults.get("ttl", 14400)  # 4 hours default

    converted_data_sources = {}

    for source_name, source_config in r_data_sources.items():
        source_type = source_config.get("type", "local")
        source_path = source_config.get("path", "")
        source_ttl = source_config.get("ttl", default_ttl)

        # Determine backend
        if source_type == "cos_cached":
            backend = "ibm_cos"
        elif source_type == "local":
            backend = "local"
        else:
            backend = "local"  # Default fallback

        # Create DataManager format
        converted_data_sources[source_name] = {
            "backend": backend,
            "ttl_seconds": source_ttl,
            "file_patterns": {
                "default": source_path
            },
            "validation": {
                "required_columns": []
            },
            "retry_strategy": {
                "max_retries": 3,
                "retry_delay": 2,
                "backoff_multiplier": 2
            }
        }

    return {
        "storage": storage_config,
        "data_sources": converted_data_sources
    }


def create_datamanager_config(config_path: str = None) -> Dict[str, Any]:
    """
    Load R config and convert to DataManager format.

    Args:
        config_path: Path to data_sources.yml. If None, uses CONFIG_PATH env var.

    Returns:
        DataManager-compatible configuration dictionary
    """
    r_config = load_r_config(config_path)
    return convert_r_config_to_datamanager(r_config)
