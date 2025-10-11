"""
Data Source Configuration Module

Handles parsing and validation of centralized data source definitions from config.yaml.
Provides file path resolution, TTL management, and validation rules.
"""

import re
from typing import Dict, Any, Optional, List
from dataclasses import dataclass


@dataclass
class RetryStrategy:
    """Retry strategy configuration for a data source."""
    max_retries: int = 3
    retry_delay: int = 5
    backoff_multiplier: float = 2.0


@dataclass
class DataSourceDefinition:
    """Definition of a data source with all its configuration."""
    name: str
    ttl_seconds: int
    backend: str
    file_patterns: Dict[str, str]
    validation: Optional[str] = None
    retry_strategy: Optional[RetryStrategy] = None


class DataSourceConfig:
    """
    Manages data source configurations and provides utilities for 
    file path resolution and TTL management.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize with configuration dictionary.
        
        Args:
            config: Full configuration dictionary from config.yaml
        """
        self.config = config
        self.data_policies = config.get('data_policies', {})
        self.data_sources = config.get('data_sources', {})
        self._parsed_sources: Dict[str, DataSourceDefinition] = {}
        
        # Parse and validate configuration
        self._parse_data_sources()
    
    def _parse_ttl(self, ttl_str: str) -> int:
        """
        Parse TTL string to seconds.
        
        Supports formats like: "30d", "24h", "60m", "3600s", "3600"
        
        Args:
            ttl_str: TTL string specification
            
        Returns:
            TTL in seconds
            
        Raises:
            ValueError: If TTL format is invalid
        """
        if isinstance(ttl_str, int):
            return ttl_str
        
        ttl_str = str(ttl_str).strip().lower()
        
        # Handle plain numbers (assume seconds)
        if ttl_str.isdigit():
            return int(ttl_str)
        
        # Parse time units
        time_units = {
            's': 1,
            'm': 60,
            'h': 3600,
            'd': 86400,
            'w': 604800
        }
        
        match = re.match(r'^(\d+)([smhdw])$', ttl_str)
        if not match:
            raise ValueError(f"Invalid TTL format: {ttl_str}. Use format like '30d', '24h', '60m', '3600s'")
        
        value, unit = match.groups()
        return int(value) * time_units[unit]
    
    def _parse_retry_strategy(self, retry_config: Optional[Dict[str, Any]]) -> RetryStrategy:
        """
        Parse retry strategy configuration.
        
        Args:
            retry_config: Retry configuration dictionary or None
            
        Returns:
            RetryStrategy instance
        """
        if not retry_config:
            # Use default from data_policies or built-in default
            default_retry = self.data_policies.get('default_retry_strategy', {})
            return RetryStrategy(
                max_retries=default_retry.get('max_retries', 3),
                retry_delay=default_retry.get('retry_delay', 5),
                backoff_multiplier=default_retry.get('backoff_multiplier', 2.0)
            )
        
        return RetryStrategy(
            max_retries=retry_config.get('max_retries', 3),
            retry_delay=retry_config.get('retry_delay', 5),
            backoff_multiplier=retry_config.get('backoff_multiplier', 2.0)
        )
    
    def _parse_data_sources(self) -> None:
        """Parse all data source definitions and validate them."""
        default_ttl = self.data_policies.get('default_ttl', '30d')
        default_backend = self.data_policies.get('default_backend', 'local')
        
        for source_name, source_config in self.data_sources.items():
            try:
                # Parse TTL
                ttl_str = source_config.get('ttl', default_ttl)
                ttl_seconds = self._parse_ttl(ttl_str)
                
                # Parse backend
                backend = source_config.get('backend', default_backend)
                
                # Parse file patterns
                file_patterns = source_config.get('file_patterns', {})
                if not file_patterns:
                    raise ValueError(f"Data source '{source_name}' must have file_patterns")
                
                # Parse validation
                validation = source_config.get('validation')
                
                # Parse retry strategy
                retry_strategy = self._parse_retry_strategy(
                    source_config.get('retry_strategy')
                )
                
                # Create data source definition
                definition = DataSourceDefinition(
                    name=source_name,
                    ttl_seconds=ttl_seconds,
                    backend=backend,
                    file_patterns=file_patterns,
                    validation=validation,
                    retry_strategy=retry_strategy
                )
                
                self._parsed_sources[source_name] = definition
                
            except Exception as e:
                raise ValueError(f"Error parsing data source '{source_name}': {str(e)}")
    
    def get_data_source(self, source_name: str) -> DataSourceDefinition:
        """
        Get data source definition by name.
        
        Args:
            source_name: Name of the data source
            
        Returns:
            DataSourceDefinition instance
            
        Raises:
            KeyError: If data source is not found
        """
        if source_name not in self._parsed_sources:
            raise KeyError(f"Data source '{source_name}' not found. Available sources: {list(self._parsed_sources.keys())}")
        
        return self._parsed_sources[source_name]
    
    def list_data_sources(self) -> List[str]:
        """
        Get list of all available data source names.
        
        Returns:
            List of data source names
        """
        return list(self._parsed_sources.keys())
    
    def resolve_file_path(self, source_name: str, file_type: str, **kwargs) -> str:
        """
        Resolve file path for a data source with parameter substitution.
        
        Args:
            source_name: Name of the data source
            file_type: Type of file within the data source
            **kwargs: Parameters for path substitution (e.g., area="south_america", year="2024")
            
        Returns:
            Resolved file path
            
        Raises:
            KeyError: If data source or file type not found
            ValueError: If required parameters are missing
        """
        source_def = self.get_data_source(source_name)
        
        if file_type not in source_def.file_patterns:
            available_types = list(source_def.file_patterns.keys())
            raise KeyError(f"File type '{file_type}' not found in data source '{source_name}'. Available types: {available_types}")
        
        file_pattern = source_def.file_patterns[file_type]
        
        # Replace placeholders with provided values
        resolved_path = file_pattern
        for key, value in kwargs.items():
            placeholder = f"{{{key}}}"
            resolved_path = resolved_path.replace(placeholder, str(value))
        
        # Check for remaining placeholders
        remaining_placeholders = re.findall(r'\{(\w+)\}', resolved_path)
        if remaining_placeholders:
            raise ValueError(
                f"Missing required parameters for file path resolution: {remaining_placeholders}. "
                f"Pattern: {file_pattern}, Provided: {list(kwargs.keys())}"
            )
        
        return resolved_path
    
    def get_file_types(self, source_name: str) -> List[str]:
        """
        Get available file types for a data source.
        
        Args:
            source_name: Name of the data source
            
        Returns:
            List of available file types
        """
        source_def = self.get_data_source(source_name)
        return list(source_def.file_patterns.keys())
    
    def get_ttl_seconds(self, source_name: str) -> int:
        """
        Get TTL in seconds for a data source.
        
        Args:
            source_name: Name of the data source
            
        Returns:
            TTL in seconds
        """
        source_def = self.get_data_source(source_name)
        return source_def.ttl_seconds
    
    def get_backend(self, source_name: str) -> str:
        """
        Get backend type for a data source.
        
        Args:
            source_name: Name of the data source
            
        Returns:
            Backend type ('local', 'ibm_cos', etc.)
        """
        source_def = self.get_data_source(source_name)
        return source_def.backend
    
    def get_validation_type(self, source_name: str) -> Optional[str]:
        """
        Get validation type for a data source.
        
        Args:
            source_name: Name of the data source
            
        Returns:
            Validation type or None if not specified
        """
        source_def = self.get_data_source(source_name)
        return source_def.validation
    
    def get_retry_strategy(self, source_name: str) -> RetryStrategy:
        """
        Get retry strategy for a data source.
        
        Args:
            source_name: Name of the data source
            
        Returns:
            RetryStrategy instance
        """
        source_def = self.get_data_source(source_name)
        return source_def.retry_strategy


def create_data_source_config(config: Dict[str, Any]) -> DataSourceConfig:
    """
    Factory function to create and validate DataSourceConfig.
    
    Args:
        config: Configuration dictionary from config.yaml
        
    Returns:
        DataSourceConfig instance
        
    Raises:
        ValueError: If configuration is invalid
    """
    try:
        ds_config = DataSourceConfig(config)
        return ds_config
    except Exception as e:
        raise ValueError(f"Data source configuration validation failed: {str(e)}")