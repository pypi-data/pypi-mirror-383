"""
Data Manager Module

High-level interface for data operations with automatic caching, TTL management,
and backend synchronization. Provides clean API for pipeline code.
"""

import os
import logging
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass

from .cache_manager import CacheManager
from .sync_manager import SyncManager
from .data_source_config import DataSourceConfig, create_data_source_config
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


@dataclass
class FileSpec:
    """Specification for a file operation."""

    data_source: str
    file_type: str
    path_params: Dict[str, Any]


class DataManager:
    """
    High-level data manager that provides unified access to cached and remote data.

    Handles TTL checking, cache coordination, and backend synchronization automatically.
    Provides both individual and batch operations for optimal performance.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize data manager.

        Args:
            config: Full configuration dictionary from config.yaml
        """
        self.config = config

        # Initialize components
        self.data_source_config = create_data_source_config(config)

        # Determine cache base path
        cache_base_path = self._get_cache_base_path()
        self.cache_manager = CacheManager(cache_base_path)

        self.sync_manager = SyncManager(
            config, self.cache_manager, self.data_source_config
        )

        # Session-level cache to prevent redundant downloads within single pipeline run
        self._session_cache = {}

    def _get_cache_base_path(self) -> str:
        """Get cache base path from configuration."""
        # Check environment variable first
        if "DATA_PATH" in os.environ:
            return os.environ["DATA_PATH"]

        # Check storage configuration
        storage_config = self.config.get("storage", {})
        local_config = storage_config.get("local", {})
        base_path = local_config.get("base_path", "./data_repo")

        # Fallback to legacy repo_path
        if not base_path and "repo_path" in self.config:
            base_path = self.config["repo_path"]

        return base_path or "./data_repo"

    def get_data(
        self,
        data_source: str,
        file_type: str,
        force_refresh: bool = False,
        **path_params,
    ) -> Any:
        """
        Get data for a specific file, with automatic caching and sync.

        Args:
            data_source: Data source name
            file_type: File type within the data source
            force_refresh: Force refresh even if cached data is fresh
            **path_params: Parameters for file path resolution (e.g., area="south_america", year="2024")

        Returns:
            Loaded data (DataFrame, xarray Dataset, etc.)

        Raises:
            KeyError: If data source or file type not found
            FileNotFoundError: If file not found in cache or remote backend
        """
        logger.debug(f"get_data called: {data_source}/{file_type}, force_refresh={force_refresh}")
        
        # Create cache key for session cache
        cache_key = (data_source, file_type, tuple(sorted(path_params.items())))

        # Check session cache first (unless force_refresh is True)
        if not force_refresh and cache_key in self._session_cache:
            logger.debug("Found in session cache, returning cached data")
            return self._session_cache[cache_key]

        # Resolve file path
        relative_path = self.data_source_config.resolve_file_path(
            data_source, file_type, **path_params
        )
        logger.debug(f"Resolved path: {relative_path}")

        # Smart download decision - only download if really needed
        if not force_refresh:
            logger.debug("Checking if download is needed...")
            # Use smart download logic to check if we actually need to download
            if not self.is_download_needed(data_source, file_type, **path_params):
                logger.debug("Download not needed, loading from cache")
                # Load from local cache
                data = self.cache_manager.load_file(relative_path)
                # Store in session cache
                self._session_cache[cache_key] = data
                return data

        logger.debug("Download needed, calling sync_file...")
        # Need to sync from remote backend (either force_refresh=True or download is needed)
        sync_success = self.sync_manager.sync_file(
            data_source, file_type, relative_path, force_refresh, **path_params
        )
        logger.debug(f"Sync result: {sync_success}")

        if not sync_success:
            # Try to load stale data if available
            if self.cache_manager.file_exists(relative_path):
                data = self.cache_manager.load_file(relative_path)
                # Store in session cache
                self._session_cache[cache_key] = data
                return data
            else:
                raise FileNotFoundError(
                    f"File not found in cache or remote backend: {relative_path}"
                )

        # Load fresh data from cache
        data = self.cache_manager.load_file(relative_path)
        # Store in session cache
        self._session_cache[cache_key] = data
        return data

    def save_data(
        self, data_source: str, file_type: str, data: Any, **path_params
    ) -> str:
        """
        Save data with automatic caching and backend sync.

        Args:
            data_source: Data source name
            file_type: File type within the data source
            data: Data to save (DataFrame, xarray Dataset, etc.)
            **path_params: Parameters for file path resolution

        Returns:
            Relative path of saved file

        Raises:
            KeyError: If data source or file type not found
        """
        # Resolve file path
        relative_path = self.data_source_config.resolve_file_path(
            data_source, file_type, **path_params
        )

        # Get data source configuration
        source_def = self.data_source_config.get_data_source(data_source)

        # Save to local cache (TTL and backend come from current config, not stored in cache)
        self.cache_manager.save_file(data=data, relative_path=relative_path)

        # Sync to remote backend if needed
        if source_def.backend != "local":
            try:
                self.sync_manager.upload_file(data_source, relative_path)
            except Exception as e:
                # Upload failed, but file is saved locally
                # This ensures data is not lost even if backend is unavailable
                pass

        return relative_path

    def is_data_fresh(self, data_source: str, file_type: str, **path_params) -> bool:
        """
        Check if data is fresh (within TTL) in cache using current config TTL.

        Args:
            data_source: Data source name
            file_type: File type within the data source
            **path_params: Parameters for file path resolution

        Returns:
            True if data is fresh, False if stale or not found
        """
        try:
            relative_path = self.data_source_config.resolve_file_path(
                data_source, file_type, **path_params
            )

            # Get current TTL from config, not cached metadata
            data_source_info = self.data_source_config.get_data_source(data_source)
            ttl_seconds = data_source_info.ttl_seconds

            return self.cache_manager.is_data_fresh(relative_path, ttl_seconds)
        except (KeyError, ValueError):
            return False

    def data_exists(self, data_source: str, file_type: str, **path_params) -> bool:
        """
        Check if data exists in cache (regardless of freshness).

        Args:
            data_source: Data source name
            file_type: File type within the data source
            **path_params: Parameters for file path resolution

        Returns:
            True if data exists in cache
        """
        try:
            relative_path = self.data_source_config.resolve_file_path(
                data_source, file_type, **path_params
            )
            return self.cache_manager.file_exists(relative_path)
        except (KeyError, ValueError):
            return False

    def get_file_specs(
        self, data_source: str, file_types: List[str], **common_params
    ) -> List[FileSpec]:
        """
        Create file specifications for batch operations.

        Args:
            data_source: Data source name
            file_types: List of file types to include
            **common_params: Common parameters for all files

        Returns:
            List of FileSpec instances
        """
        file_specs = []
        for file_type in file_types:
            file_specs.append(
                FileSpec(
                    data_source=data_source,
                    file_type=file_type,
                    path_params=common_params.copy(),
                )
            )
        return file_specs

    def get_data_batch(
        self,
        file_specs: List[Union[FileSpec, Dict[str, Any]]],
        force_refresh: bool = False,
    ) -> List[Any]:
        """
        Get multiple files in batch for optimal performance.

        Args:
            file_specs: List of FileSpec instances or dictionaries with:
                - data_source: Data source name
                - file_type: File type
                - path_params: Parameters for path resolution (optional)
            force_refresh: Force refresh for all files

        Returns:
            List of loaded data in same order as file_specs

        Raises:
            Exception: If any file fails to load
        """
        # Normalize file specs
        normalized_specs = []
        for spec in file_specs:
            if isinstance(spec, dict):
                file_spec = FileSpec(
                    data_source=spec["data_source"],
                    file_type=spec["file_type"],
                    path_params=spec.get("path_params", {}),
                )
            else:
                file_spec = spec
            normalized_specs.append(file_spec)

        # Resolve all file paths
        file_paths = []
        download_specs = []

        for spec in normalized_specs:
            relative_path = self.data_source_config.resolve_file_path(
                spec.data_source, spec.file_type, **spec.path_params
            )
            file_paths.append(relative_path)

            # Check if file needs downloading
            needs_download = (
                force_refresh
                or not self.cache_manager.file_exists(relative_path)
                or not self.cache_manager.is_data_fresh(relative_path)
            )

            if needs_download:
                download_specs.append(
                    {
                        "source_name": spec.data_source,
                        "file_type": spec.file_type,
                        "relative_path": relative_path,
                        "path_params": spec.path_params,
                    }
                )

        # Batch download missing/stale files
        if download_specs:
            successful_downloads, failed_downloads = self.sync_manager.download_batch(
                download_specs
            )

        # Load all files from cache
        loaded_data = []
        for relative_path in file_paths:
            try:
                data = self.cache_manager.load_file(relative_path)
                loaded_data.append(data)
            except FileNotFoundError:
                raise FileNotFoundError(
                    f"File not available after sync attempt: {relative_path}"
                )

        return loaded_data

    def save_data_batch(
        self, file_specs: List[Union[FileSpec, Dict[str, Any]]], data_list: List[Any]
    ) -> List[str]:
        """
        Save multiple files in batch for optimal performance.

        Args:
            file_specs: List of FileSpec instances or dictionaries
            data_list: List of data to save (same order as file_specs)

        Returns:
            List of relative paths of saved files

        Raises:
            ValueError: If file_specs and data_list lengths don't match
        """
        if len(file_specs) != len(data_list):
            raise ValueError("file_specs and data_list must have same length")

        # Normalize file specs
        normalized_specs = []
        for spec in file_specs:
            if isinstance(spec, dict):
                file_spec = FileSpec(
                    data_source=spec["data_source"],
                    file_type=spec["file_type"],
                    path_params=spec.get("path_params", {}),
                )
            else:
                file_spec = spec
            normalized_specs.append(file_spec)

        # Save all files to cache
        saved_paths = []
        upload_specs = []

        for spec, data in zip(normalized_specs, data_list):
            # Resolve file path
            relative_path = self.data_source_config.resolve_file_path(
                spec.data_source, spec.file_type, **spec.path_params
            )

            # Get data source configuration
            source_def = self.data_source_config.get_data_source(spec.data_source)

            # Save to local cache (TTL and backend come from current config, not stored in cache)
            self.cache_manager.save_file(data=data, relative_path=relative_path)

            saved_paths.append(relative_path)

            # Prepare for batch upload if needed
            if source_def.backend != "local":
                upload_specs.append(
                    {"source_name": spec.data_source, "relative_path": relative_path}
                )

        # Batch upload to remote backends
        if upload_specs:
            try:
                successful_uploads, failed_uploads = self.sync_manager.upload_batch(
                    upload_specs
                )
            except Exception:
                # Upload failed, but files are saved locally
                pass

        return saved_paths

    def remove_data(self, data_source: str, file_type: str, **path_params) -> bool:
        """
        Remove data from cache and remote backend.

        Args:
            data_source: Data source name
            file_type: File type within the data source
            **path_params: Parameters for file path resolution

        Returns:
            True if removed successfully
        """
        try:
            relative_path = self.data_source_config.resolve_file_path(
                data_source, file_type, **path_params
            )

            # Remove from cache
            self.cache_manager.remove_file(relative_path)

            # TODO: Remove from remote backend (not implemented yet)
            # This would require adding delete methods to storage backends

            return True
        except Exception:
            return False

    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache statistics
        """
        return self.cache_manager.get_cache_stats()

    def list_data_sources(self) -> List[str]:
        """
        List all available data sources.

        Returns:
            List of data source names
        """
        return self.data_source_config.list_data_sources()

    def list_file_types(self, data_source: str) -> List[str]:
        """
        List available file types for a data source.

        Args:
            data_source: Data source name

        Returns:
            List of file types
        """
        return self.data_source_config.get_file_types(data_source)

    def get_data_source_info(self, data_source: str) -> Dict[str, Any]:
        """
        Get information about a data source.

        Args:
            data_source: Data source name

        Returns:
            Dictionary with data source information
        """
        source_def = self.data_source_config.get_data_source(data_source)
        return {
            "name": source_def.name,
            "ttl_seconds": source_def.ttl_seconds,
            "backend": source_def.backend,
            "file_types": list(source_def.file_patterns.keys()),
            "validation": source_def.validation,
            "retry_strategy": {
                "max_retries": source_def.retry_strategy.max_retries,
                "retry_delay": source_def.retry_strategy.retry_delay,
                "backoff_multiplier": source_def.retry_strategy.backoff_multiplier,
            },
        }

    def clear_session_cache(self) -> int:
        """
        Clear the session-level cache to free memory.

        Should be called at the end of pipeline runs to prevent memory leaks.

        Returns:
            Number of cached items that were cleared
        """
        cache_size = len(self._session_cache)
        self._session_cache.clear()
        return cache_size

    def is_download_needed(
        self, data_source: str, file_type: str, **path_params
    ) -> bool:
        """
        Smart download decision that checks remote metadata before downloading.

        This is the core of the optimization - instead of downloading stale files,
        we check if the remote file is actually newer than what we have locally.

        Args:
            data_source: Data source name
            file_type: File type within the data source
            **path_params: Parameters for file path resolution

        Returns:
            True if download is needed, False if local file is sufficient
        """
        logger.debug(f"is_download_needed called for {data_source}/{file_type}")
        try:
            # Resolve file path
            relative_path = self.data_source_config.resolve_file_path(
                data_source, file_type, **path_params
            )

            # If no local file exists, we need to download
            if not self.cache_manager.file_exists(relative_path):
                return True

            # Get current TTL from config
            data_source_info = self.data_source_config.get_data_source(data_source)
            ttl_seconds = data_source_info.ttl_seconds

            # If local file is fresh within TTL, no download needed
            if self.cache_manager.is_data_fresh(relative_path, ttl_seconds):
                return False

            # Local file is stale - check if remote is newer
            # Get backend for this data source
            try:
                backend = self.sync_manager._get_backend_for_source(data_source)
                if hasattr(backend, "get_file_metadata"):
                    remote_meta = backend.get_file_metadata(relative_path)
                    if remote_meta is None:
                        # Remote file doesn't exist, keep local file
                        return False

                    # Get local file metadata (fix for missing _get_full_path method)
                    import os

                    local_path_str = os.path.join(
                        self.cache_manager.cache_base_path, relative_path
                    )
                    if os.path.exists(local_path_str):
                        local_stat = os.stat(local_path_str)
                        local_modified = datetime.fromtimestamp(local_stat.st_mtime)

                        # Only download if remote is significantly newer (5 minute threshold)
                        threshold = timedelta(minutes=5)
                        remote_modified = remote_meta["last_modified"]

                        # Ensure remote_modified is timezone-naive for comparison
                        if (
                            hasattr(remote_modified, "replace")
                            and remote_modified.tzinfo is not None
                        ):
                            remote_modified = remote_modified.replace(tzinfo=None)

                        is_remote_newer = remote_modified > (local_modified + threshold)
                        return is_remote_newer
                    else:
                        # Local file disappeared, need to download
                        return True
                else:
                    # Backend doesn't support metadata operations, fallback to download
                    return True
            except Exception:
                # If metadata check fails, fallback to download to be safe
                return True

        except Exception:
            # If any error occurs, be conservative and download
            return True

    def get_session_cache_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the current session cache.

        Returns:
            Dictionary with session cache statistics
        """
        return {
            "cached_items": len(self._session_cache),
            "cache_keys": list(self._session_cache.keys()),
        }

    def query_remote_parquet(
        self,
        sql_query: str,
        file_sources: Union[str, List[str]] = None,
    ) -> Any:
        """
        Execute a SQL query on one or more remote Parquet files without downloading them.
        Uses DuckDB with HTTP range requests to only fetch required data.

        File aliases in the query are resolved from data_sources.yml configuration.
        Supports JOINs across multiple remote Parquet files.

        IMPORTANT: Only works efficiently with Parquet format. For CSV, Excel, NetCDF, or other
        formats, use get_data() which downloads the complete file.

        Args:
            sql_query: SQL query with data source names as placeholders.
                      Example: "SELECT * FROM {psem_data} WHERE fecha >= '2025-01-01'"
                      Example JOIN: "SELECT a.*, b.costo FROM {psem_data} a JOIN {costos_combustibles} b ON a.id = b.id"
            file_sources: Data source name(s) to use. Can be:
                         - None: Auto-detect from query placeholders
                         - String: Single data source name
                         - List: Multiple data source names

        Returns:
            pandas.DataFrame with query results

        Raises:
            KeyError: If data source not found in configuration
            ValueError: If backend doesn't support remote queries or file is not Parquet format
            ImportError: If DuckDB is not installed

        Examples:
            >>> # Single file query
            >>> df = dm.query_remote_parquet('''
            ...     SELECT central, fecha, SUM(potencia) as total
            ...     FROM {psem_data}
            ...     WHERE fecha >= '2025-01-01'
            ...     GROUP BY central, fecha
            ... ''')

            >>> # JOIN multiple Parquet files
            >>> df = dm.query_remote_parquet('''
            ...     SELECT
            ...         p.central,
            ...         p.fecha,
            ...         p.potencia,
            ...         c.costo_variable
            ...     FROM {psem_data} p
            ...     JOIN {costos_combustibles} c
            ...       ON p.central = c.central
            ...       AND p.fecha = c.fecha
            ...     WHERE p.fecha >= '2025-01-01'
            ... ''')
        """
        import re

        # Auto-detect file sources from query if not provided
        if file_sources is None:
            # Extract all {placeholder} patterns from query
            placeholders = re.findall(r'\{(\w+)\}', sql_query)
            file_sources = list(set(placeholders))  # Remove duplicates
        elif isinstance(file_sources, str):
            file_sources = [file_sources]

        if not file_sources:
            raise ValueError(
                "No file sources found. Either provide file_sources parameter or use {data_source_name} "
                "placeholders in your SQL query."
            )

        # Build file aliases mapping: {alias: s3_path}
        file_aliases = {}
        backend = None

        for source_name in file_sources:
            # Get data source configuration
            try:
                source_def = self.data_source_config.get_data_source(source_name)
            except KeyError:
                raise KeyError(
                    f"Data source '{source_name}' not found in data_sources.yml configuration. "
                    f"Available sources: {', '.join(self.data_source_config.list_data_sources())}"
                )

            # Verify backend supports remote queries
            if source_def.backend == "local":
                raise ValueError(
                    f"Remote query not supported for local data source '{source_name}'. "
                    f"Use get_data() to load the file instead."
                )

            # Get backend instance (use first source's backend for all)
            if backend is None:
                backend = self.sync_manager._get_backend_for_source(source_name)

            # Get file path from data source configuration
            # Check if source has 'path' attribute (simple format)
            source_config = self.data_source_config.data_sources.get(source_name, {})
            if 'path' in source_config:
                # Simple format: direct path
                relative_path = source_config['path']
            elif hasattr(source_def, 'file_patterns') and source_def.file_patterns:
                # Complex format: use first file pattern as default
                relative_path = list(source_def.file_patterns.values())[0]
            else:
                # Fallback: try to resolve with empty params
                try:
                    relative_path = self.data_source_config.resolve_file_path(
                        source_name, ''
                    )
                except:
                    raise ValueError(
                        f"Cannot resolve file path for data source '{source_name}'. "
                        f"Data source may require path parameters."
                    )

            # Verify Parquet format only
            if not relative_path.endswith(('.parquet', '.pq')):
                raise ValueError(
                    f"Remote query only supported for Parquet files (.parquet, .pq). "
                    f"Data source '{source_name}' has format: {relative_path}. "
                    f"For other formats (CSV, Excel, NetCDF), use get_data() instead."
                )

            file_aliases[source_name] = relative_path

        # Check if backend supports remote queries
        if not hasattr(backend, "query_remote_parquet"):
            raise ValueError(
                f"Backend '{source_def.backend}' does not support remote Parquet queries. "
                f"Use get_data() to download and load files instead."
            )

        # Execute remote query
        logger.info(
            f"Executing remote Parquet query on {len(file_aliases)} file(s): {list(file_aliases.keys())}"
        )

        return backend.query_remote_parquet(
            sql_query=sql_query, file_aliases=file_aliases
        )
