"""
Sync Manager Module

Handles synchronization between local cache and remote storage backends.
Manages upload/download operations with retry logic and batch capabilities.
"""

import time
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path

from .cache_manager import CacheManager
from .data_source_config import DataSourceConfig, RetryStrategy
from .storage_backends import get_storage_backend, StorageBackend

logger = logging.getLogger(__name__)


class SyncManager:
    """
    Manages synchronization between local cache and remote storage backends.
    
    Handles uploads, downloads, retries, and batch operations to minimize
    API calls to remote backends.
    """
    
    def __init__(self, config: Dict[str, Any], cache_manager: CacheManager, 
                 data_source_config: DataSourceConfig):
        """
        Initialize sync manager.
        
        Args:
            config: Full configuration dictionary
            cache_manager: CacheManager instance
            data_source_config: DataSourceConfig instance
        """
        self.config = config
        self.cache_manager = cache_manager
        self.data_source_config = data_source_config
        self._backend_cache: Dict[str, StorageBackend] = {}
    
    def _get_backend(self, backend_type: str) -> StorageBackend:
        """
        Get storage backend instance with caching.
        
        Args:
            backend_type: Backend type ('local', 'ibm_cos', etc.)
            
        Returns:
            StorageBackend instance
        """
        if backend_type not in self._backend_cache:
            # Create backend configuration for this specific type
            backend_config = self.config.copy()
            backend_config['storage']['backend'] = backend_type
            self._backend_cache[backend_type] = get_storage_backend(backend_config)
        
        return self._backend_cache[backend_type]
    
    def _get_backend_for_source(self, data_source: str) -> StorageBackend:
        """
        Get storage backend for a specific data source.
        
        Args:
            data_source: Data source name
            
        Returns:
            StorageBackend instance for this data source
        """
        source_def = self.data_source_config.get_data_source(data_source)
        return self._get_backend(source_def.backend)
    
    def _retry_with_strategy(self, operation_func, retry_strategy: RetryStrategy, 
                           operation_name: str) -> Any:
        """
        Execute an operation with retry strategy.
        
        Args:
            operation_func: Function to execute
            retry_strategy: RetryStrategy configuration
            operation_name: Name of operation for logging
            
        Returns:
            Result of successful operation
            
        Raises:
            Exception: Last exception if all retries fail
        """
        llast_exception = None
    
        for attempt in range(retry_strategy.max_retries + 1):
            logger.debug(f"Retry attempt {attempt + 1}/{retry_strategy.max_retries + 1} for {operation_name}")
            try:
                return operation_func()
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed: {e}")
                last_exception = e
                
                if attempt < retry_strategy.max_retries:
                    # Calculate delay with exponential backoff
                    delay = retry_strategy.retry_delay * (retry_strategy.backoff_multiplier ** attempt)
                    logger.debug(f"Waiting {delay} seconds before retry...")
                    time.sleep(delay)
                else:
                    # Last attempt failed
                    break
        
        # All retries failed
        logger.error(f"All retries failed for {operation_name}")
        raise last_exception
    
    def download_file(self, source_name: str, file_type: str, relative_path: str, 
                     **path_params) -> bool:
        """
        Download a file from remote backend to local cache.
        
        Args:
            source_name: Data source name
            file_type: File type within the data source
            relative_path: Relative path for local cache
            **path_params: Parameters for path resolution
            
        Returns:
            True if download successful, False otherwise
        """
        source_def = self.data_source_config.get_data_source(source_name)
        
        # Skip download for local backend
        if source_def.backend == "local":
            return False
        
        try:
            backend = self._get_backend(source_def.backend)
            
            def download_operation():
                print(f"🔄 BACKEND READ: Checking {source_def.backend} for {relative_path}")
                
                # Check if file exists on remote backend
                if not backend.exists(relative_path):
                    print(f"❌ BACKEND READ: File not found on {source_def.backend}: {relative_path}")
                    raise FileNotFoundError(f"File not found on remote backend: {relative_path}")
                
                logger.debug(f"BACKEND READ: File exists on {source_def.backend}: {relative_path}")
                
                # Determine format from file extension
                file_ext = Path(relative_path).suffix.lower()
                if file_ext in ['.nc', '.netcdf']:
                    format_type = "netcdf"
                elif file_ext in ['.parquet', '.pq']:
                    format_type = "parquet"
                elif file_ext in ['.csv']:
                    format_type = "csv"
                elif file_ext in ['.xlsx', '.xls']:
                    format_type = "excel"
                elif file_ext in ['.pkl', '.pickle']:
                    format_type = "pickle"
                else:
                    raise ValueError(f"Unsupported file format: {file_ext}")
                
                # Load data from remote backend
                logger.debug(f"BACKEND READ: Downloading from {source_def.backend}: {relative_path}")
                data = backend.load(relative_path, format=format_type)
                logger.debug(f"BACKEND READ: Successfully downloaded from {source_def.backend}: {relative_path}")
                
                # Save to local cache
                self.cache_manager.save_file(
                    data=data,
                    relative_path=relative_path,
                    format_type=format_type
                )
                
                return True
            
            # Execute with retry strategy
            result = self._retry_with_strategy(
                download_operation, 
                source_def.retry_strategy, 
                f"download_{source_name}_{file_type}"
            )
            
            # Update sync status
            self.cache_manager.update_sync_status(
                relative_path, 
                "synced", 
                datetime.now(timezone.utc).isoformat()
            )
            
            return result
            
        except Exception as e:
            # Update sync status to failed
            self.cache_manager.update_sync_status(
                relative_path, 
                "failed", 
                datetime.now(timezone.utc).isoformat()
            )
            raise e
    
    def upload_file(self, source_name: str, relative_path: str) -> bool:
        """
        Upload a file from local cache to remote backend.
        
        Args:
            source_name: Data source name
            relative_path: Relative path of the file
            
        Returns:
            True if upload successful, False otherwise
        """
        source_def = self.data_source_config.get_data_source(source_name)
        
        # Skip upload for local backend
        if source_def.backend == "local":
            self.cache_manager.update_sync_status(relative_path, "local")
            return True
        
        try:
            # Load data from cache
            data = self.cache_manager.load_file(relative_path)
            
            # Get backend
            backend = self._get_backend(source_def.backend)
            
            def upload_operation():
                print(f"📤 BACKEND WRITE: Uploading to {source_def.backend}: {relative_path}")
                
                # Determine format from file extension
                file_ext = Path(relative_path).suffix.lower()
                if file_ext in ['.nc', '.netcdf']:
                    format_type = "netcdf"
                elif file_ext in ['.parquet', '.pq']:
                    format_type = "parquet"
                elif file_ext in ['.csv']:
                    format_type = "csv"
                elif file_ext in ['.xlsx', '.xls']:
                    format_type = "excel"
                elif file_ext in ['.pkl', '.pickle']:
                    format_type = "pickle"
                else:
                    raise ValueError(f"Unsupported file format: {file_ext}")
                
                # Save to remote backend
                backend.save(data, relative_path, format=format_type)
                logger.debug(f"BACKEND WRITE: Successfully uploaded to {source_def.backend}: {relative_path}")
                return True
            
            # Execute with retry strategy
            result = self._retry_with_strategy(
                upload_operation, 
                source_def.retry_strategy, 
                f"upload_{source_name}"
            )
            
            # Update sync status
            self.cache_manager.update_sync_status(
                relative_path, 
                "synced", 
                datetime.now(timezone.utc).isoformat()
            )
            
            return result
            
        except Exception as e:
            # Update sync status to failed
            self.cache_manager.update_sync_status(
                relative_path, 
                "failed", 
                datetime.now(timezone.utc).isoformat()
            )
            raise e
    
    def download_batch(self, file_specs: List[Dict[str, Any]]) -> Tuple[List[str], List[str]]:
        """
        Download multiple files in batch.
        
        Args:
            file_specs: List of file specifications, each containing:
                - source_name: Data source name
                - file_type: File type
                - relative_path: Relative path for cache
                - path_params: Parameters for path resolution
                
        Returns:
            Tuple of (successful_paths, failed_paths)
        """
        successful_paths = []
        failed_paths = []
        
        for file_spec in file_specs:
            try:
                source_name = file_spec['source_name']
                file_type = file_spec['file_type']
                relative_path = file_spec['relative_path']
                path_params = file_spec.get('path_params', {})
                
                success = self.download_file(
                    source_name, file_type, relative_path, **path_params
                )
                
                if success:
                    successful_paths.append(relative_path)
                else:
                    failed_paths.append(relative_path)
                    
            except Exception:
                failed_paths.append(file_spec.get('relative_path', 'unknown'))
        
        return successful_paths, failed_paths
    
    def upload_batch(self, upload_specs: List[Dict[str, str]]) -> Tuple[List[str], List[str]]:
        """
        Upload multiple files in batch.
        
        Args:
            upload_specs: List of upload specifications, each containing:
                - source_name: Data source name
                - relative_path: Relative path of the file
                
        Returns:
            Tuple of (successful_paths, failed_paths)
        """
        successful_paths = []
        failed_paths = []
        
        # Group uploads by backend type for potential optimization
        backend_groups = {}
        for spec in upload_specs:
            source_name = spec['source_name']
            source_def = self.data_source_config.get_data_source(source_name)
            backend_type = source_def.backend
            
            if backend_type not in backend_groups:
                backend_groups[backend_type] = []
            backend_groups[backend_type].append(spec)
        
        # Process each backend group
        for backend_type, specs in backend_groups.items():
            if backend_type == "local":
                # No upload needed for local backend
                for spec in specs:
                    self.cache_manager.update_sync_status(spec['relative_path'], "local")
                    successful_paths.append(spec['relative_path'])
                continue
            
            # Upload files for this backend
            for spec in specs:
                try:
                    success = self.upload_file(spec['source_name'], spec['relative_path'])
                    if success:
                        successful_paths.append(spec['relative_path'])
                    else:
                        failed_paths.append(spec['relative_path'])
                except Exception:
                    failed_paths.append(spec['relative_path'])
        
        return successful_paths, failed_paths
    
    def sync_file(self, source_name: str, file_type: str, relative_path: str, 
                  force_download: bool = False, **path_params) -> bool:
        """
        Ensure a file is available in local cache, downloading if necessary.
        
        Args:
            source_name: Data source name
            file_type: File type within the data source
            relative_path: Relative path for local cache
            force_download: Force download even if cached data is fresh
            **path_params: Parameters for path resolution
            
        Returns:
            True if file is available in cache, False otherwise
        """
        # Check if file exists and is fresh in cache
        if not force_download and self.cache_manager.file_exists(relative_path):
            # Get current TTL from config for proper freshness check
            source_def = self.data_source_config.get_data_source(source_name)
            ttl_seconds = source_def.ttl_seconds
            
            if self.cache_manager.is_data_fresh(relative_path, ttl_seconds):
                return True
        
        # Need to download from remote backend
        try:
            return self.download_file(source_name, file_type, relative_path, **path_params)
        except FileNotFoundError:
            # File doesn't exist on remote backend
            return False
        except Exception:
            # Download failed, but file might exist in cache (even if stale)
            return self.cache_manager.file_exists(relative_path)
    
    def get_sync_status(self, relative_path: str) -> Optional[str]:
        """
        Get sync status for a cached file.
        
        Args:
            relative_path: Relative path of the file
            
        Returns:
            Sync status or None if file not found
        """
        metadata = self.cache_manager.get_file_metadata(relative_path)
        return metadata.sync_status if metadata else None
    
    def list_unsynced_files(self) -> List[str]:
        """
        List files that need to be uploaded to remote backends.
        
        Returns:
            List of relative paths of unsynced files
        """
        unsynced_files = []
        
        for relative_path in self.cache_manager.list_cached_files():
            metadata = self.cache_manager.get_file_metadata(relative_path)
            if metadata and metadata.sync_status in ["local", "pending", "failed"]:
                # Check if backend requires sync
                source_name = self._guess_source_name_from_path(relative_path)
                if source_name:
                    try:
                        source_def = self.data_source_config.get_data_source(source_name)
                        if source_def.backend != "local":
                            unsynced_files.append(relative_path)
                    except KeyError:
                        # Unknown source, skip
                        pass
        
        return unsynced_files
    
    def _guess_source_name_from_path(self, relative_path: str) -> Optional[str]:
        """
        Try to guess source name from file path by checking patterns.
        
        Args:
            relative_path: Relative path of the file
            
        Returns:
            Source name or None if cannot determine
        """
        # This is a simple heuristic - could be improved
        for source_name in self.data_source_config.list_data_sources():
            source_def = self.data_source_config.get_data_source(source_name)
            for file_type, pattern in source_def.file_patterns.items():
                # Convert pattern to regex-like matching
                pattern_parts = pattern.split('/')
                path_parts = relative_path.split('/')
                
                if len(pattern_parts) == len(path_parts):
                    # Simple check if path structure matches
                    if pattern_parts[0] == path_parts[0]:  # First directory matches
                        return source_name
        
        return None