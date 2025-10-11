"""Configuration adapters for omnifetch."""

from .yaml_config import (
    load_r_config,
    convert_r_config_to_datamanager,
    create_datamanager_config,
)

__all__ = [
    "load_r_config",
    "convert_r_config_to_datamanager",
    "create_datamanager_config",
]
