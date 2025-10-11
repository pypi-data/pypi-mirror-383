"""
Cache Manager Module

Manages local filesystem cache with JSON metadata, TTL tracking, and file locking
for concurrent access protection.
"""

import json
import os
import logging
# import fcntl
import hashlib
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional, List
from contextlib import contextmanager
from dataclasses import dataclass, asdict
from filelock import FileLock

logger = logging.getLogger(__name__)


@dataclass
class CacheMetadata:
    """Metadata for a cached file."""
    created_at: str  # ISO format timestamp
    checksum: str
    size_bytes: int
    last_sync: Optional[str] = None  # ISO format timestamp
    sync_status: str = "local"  # "local", "synced", "pending", "failed"


class CacheManager:
    """
    Manages local filesystem cache with TTL tracking and metadata.
    
    Uses JSON files for metadata storage and file locking for concurrent access protection.
    All data is cached locally regardless of backend type.
    """
    
    def __init__(self, cache_base_path: str):
        """
        Initialize cache manager.
        
        Args:
            cache_base_path: Base directory for cache storage
        """
        self.cache_base_path = Path(cache_base_path)
        self.metadata_dir = self.cache_base_path / ".omnifetch_cache"
        self.metadata_file = self.metadata_dir / "metadata.json"
        self.locks_dir = self.metadata_dir / "locks"
        
        # Ensure directories exist
        self.cache_base_path.mkdir(parents=True, exist_ok=True)
        self.metadata_dir.mkdir(parents=True, exist_ok=True)
        self.locks_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize metadata if it doesn't exist or is corrupted
        if not self.metadata_file.exists():
            logger.warning("Metadata file missing, rebuilding from existing files...")
            self._rebuild_metadata_from_files()
        else:
            # Test if existing metadata is readable
            try:
                self._read_metadata()
            except json.JSONDecodeError:
                logger.warning("Metadata file corrupted, rebuilding from existing files...")
                self._rebuild_metadata_from_files()
    
    def _calculate_checksum(self, file_path: Path) -> str:
        """Calculate SHA256 checksum of a file."""
        hash_sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    
    def _get_lock_file_path(self, relative_path: str) -> Path:
        """Get lock file path for a given cache file."""
        # Replace path separators with underscores for lock file name
        lock_name = relative_path.replace("/", "_").replace("\\", "_") + ".lock"
        return self.locks_dir / lock_name
    
    # def _cleanup_stale_locks(self, max_age_seconds: int = 300) -> int:
    #     """
    #     Clean up stale lock files that are no longer held by active processes.
        
    #     Args:
    #         max_age_seconds: Maximum age in seconds before a lock is considered stale
            
    #     Returns:
    #         Number of stale locks cleaned up
    #     """
    #     import time
        
    #     if not self.locks_dir.exists():
    #         return 0
        
    #     current_time = time.time()
    #     cleaned_count = 0
        
    #     for lock_file in self.locks_dir.glob('*.lock'):
    #         try:
    #             stat = lock_file.stat()
    #             age = current_time - stat.st_mtime
                
    #             if age > max_age_seconds:
    #                 # Test if lock is actually held by trying to acquire it
    #                 with open(lock_file, 'r+') as f:
    #                     fcntl.flock(f.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    #                     # If we get here, lock is not held - safe to remove
    #                     fcntl.flock(f.fileno(), fcntl.LOCK_UN)
                    
    #                 lock_file.unlink()
    #                 cleaned_count += 1
                    
    #         except BlockingIOError:
    #             # Lock is actively held, keep it
    #             continue
    #         except (OSError, FileNotFoundError):
    #             # File was already removed or other OS error, ignore
    #             continue
    #         except Exception:
    #             # Any other error, be conservative and keep the lock
    #             continue
        
    #     return cleaned_count

    def _cleanup_stale_locks(self, max_age_seconds: int = 300) -> int:
        """
        Clean up stale lock files that are no longer held by active processes.
        
        Args:
            max_age_seconds: Maximum age in seconds before a lock is considered stale
            
        Returns:
            Number of stale locks cleaned up
        """
        import time
        from filelock import FileLock, Timeout
        
        if not self.locks_dir.exists():
            return 0
        
        current_time = time.time()
        cleaned_count = 0
        
        for lock_file in self.locks_dir.glob('*.lock'):
            try:
                stat = lock_file.stat()
                age = current_time - stat.st_mtime
                
                if age > max_age_seconds:
                    # Test if lock is actually held by trying to acquire it
                    try:
                        with FileLock(str(lock_file), timeout=0.1):
                            # If we get here, lock is not held - safe to remove
                            pass
                        
                        lock_file.unlink()
                        cleaned_count += 1
                        
                    except Timeout:
                        # Lock is actively held, keep it
                        continue
                        
            except (OSError, FileNotFoundError):
                # File was already removed or other OS error, ignore
                continue
            except Exception:
                # Any other error, be conservative and keep the lock
                continue
        
        return cleaned_count
        
    # @contextmanager
    # def _file_lock(self, relative_path: str):
    #     """
    #     Context manager for file locking to handle concurrent access.
        
    #     Args:
    #         relative_path: Relative path of the file to lock
    #     """
    #     # Periodically clean up stale locks (every 10th operation)
    #     import random
    #     if random.randint(1, 10) == 1:
    #         self._cleanup_stale_locks()
        
    #     lock_file_path = self._get_lock_file_path(relative_path)
        
    #     # Ensure lock file parent directory exists and create lock file
    #     lock_file_path.parent.mkdir(parents=True, exist_ok=True)
    #     lock_file_path.touch()
        
    #     with open(lock_file_path, 'w') as lock_file:
    #         try:
    #             # Acquire exclusive lock
    #             fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
    #             yield
    #         finally:
    #             # Release lock (automatically released when file closes)
    #             fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)
    #             # Clean up this lock file after use
    #             try:
    #                 lock_file_path.unlink()
    #             except (OSError, FileNotFoundError):
    #                 # File already removed or other error, ignore
    #                 pass
    
    from filelock import FileLock

    # En lugar de tu @contextmanager _file_lock():
    @contextmanager
    def _file_lock(self, relative_path: str):
        lock_file_path = self._get_lock_file_path(relative_path)
        lock = FileLock(str(lock_file_path))
        
        with lock:
            yield

    def _read_metadata(self) -> Dict[str, Any]:
        """Read metadata from JSON file with error handling."""
        try:
            with open(self.metadata_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            # If metadata is corrupted or missing, try to rebuild from existing files
            if isinstance(e, json.JSONDecodeError):
                logger.warning("Metadata file corrupted, rebuilding from existing files")
            
            return self._rebuild_metadata_from_files()
    
    def _write_metadata(self, metadata: Dict[str, Any]) -> None:
        """Write metadata to JSON file atomically."""
        # Write to temporary file first, then move (atomic operation)
        with tempfile.NamedTemporaryFile(
            mode='w', 
            dir=self.metadata_dir, 
            delete=False, 
            suffix='.tmp'
        ) as tmp_file:
            json.dump(metadata, tmp_file, indent=2)
            tmp_file_path = tmp_file.name
        
        # Atomic move with Windows compatibility
        try:
            # On Windows, target file must be removed first
            if os.path.exists(self.metadata_file):
                os.remove(self.metadata_file)
            os.rename(tmp_file_path, self.metadata_file)
        except Exception:
            # Clean up temp file if rename failed
            if os.path.exists(tmp_file_path):
                os.remove(tmp_file_path)
            raise
    
    def _rebuild_metadata_from_files(self) -> Dict[str, Any]:
        """
        Rebuild metadata by scanning existing files in cache.
        Used when metadata file is corrupted or missing.
        """
        import glob
        from pathlib import Path
        
        metadata = {
            "cache_version": "1.0",
            "files": {}
        }
        
        # Scan all files in cache directory (excluding .ragpicker_cache)
        cache_pattern = str(self.cache_base_path / "**" / "*")
        
        for file_path in glob.glob(cache_pattern, recursive=True):
            path_obj = Path(file_path)
            
            # Skip directories and cache management files
            if (path_obj.is_dir() or 
                ".ragpicker_cache" in str(path_obj) or 
                path_obj.name.startswith('.')):
                continue
            
            # Get relative path from cache base
            try:
                relative_path = str(path_obj.relative_to(self.cache_base_path))
            except ValueError:
                continue  # File outside cache base
            
            # Create metadata entry with conservative defaults
            try:
                stat_info = path_obj.stat()
                checksum = self._calculate_checksum(path_obj)
                
                # Create metadata from file stats (TTL and backend come from current config)
                file_metadata = CacheMetadata(
                    created_at=datetime.fromtimestamp(stat_info.st_mtime, timezone.utc).isoformat(),
                    checksum=checksum,
                    size_bytes=stat_info.st_size,
                    sync_status="local"
                )
                
                metadata["files"][relative_path] = asdict(file_metadata)
                
            except Exception as e:
                logger.warning(f"Could not rebuild metadata for {relative_path}: {e}")
                continue
        
        logger.warning(f"Rebuilt metadata for {len(metadata['files'])} files with conservative 1-day TTL")
        logger.info("Original TTL values were lost. Data will refresh more frequently until next regular save.")
        
        # Save the rebuilt metadata
        self._write_metadata(metadata)
        
        return metadata
    
    def get_cache_file_path(self, relative_path: str) -> Path:
        """
        Get full cache file path for a relative path.
        
        Args:
            relative_path: Relative path within cache
            
        Returns:
            Full path to cache file
        """
        return self.cache_base_path / relative_path
    
    def file_exists(self, relative_path: str) -> bool:
        """
        Check if a file exists in cache.
        
        Args:
            relative_path: Relative path of the file
            
        Returns:
            True if file exists in cache
        """
        cache_file_path = self.get_cache_file_path(relative_path)
        return cache_file_path.exists()
    
    def is_data_fresh(self, relative_path: str, ttl_seconds: int = None) -> bool:
        """
        Check if cached data is fresh (within TTL).
        
        Args:
            relative_path: Relative path of the file
            ttl_seconds: TTL in seconds (from current config, not cached metadata)
            
        Returns:
            True if data is fresh, False if stale or not found
        """
        metadata = self._read_metadata()
        file_metadata = metadata.get("files", {}).get(relative_path)
        
        if not file_metadata:
            return False
        
        # Check if file still exists
        if not self.file_exists(relative_path):
            return False
        
        try:
            created_at = datetime.fromisoformat(file_metadata['created_at'])
            
            # Use TTL from current config, not cached metadata
            if ttl_seconds is None:
                # Fallback to cached TTL only if no current TTL provided
                ttl_seconds = file_metadata.get('ttl_seconds', 0)
            
            # Calculate age
            now = datetime.now(timezone.utc)
            if created_at.tzinfo is None:
                created_at = created_at.replace(tzinfo=timezone.utc)
            
            age_seconds = (now - created_at).total_seconds()
            return age_seconds < ttl_seconds
            
        except (KeyError, ValueError, TypeError):
            # If there's any issue with metadata, consider data stale
            return False
    
    def get_file_metadata(self, relative_path: str) -> Optional[CacheMetadata]:
        """
        Get metadata for a cached file.
        
        Args:
            relative_path: Relative path of the file
            
        Returns:
            CacheMetadata instance or None if not found
        """
        metadata = self._read_metadata()
        file_metadata = metadata.get("files", {}).get(relative_path)
        
        if not file_metadata:
            return None
        
        try:
            return CacheMetadata(**file_metadata)
        except (TypeError, ValueError):
            return None
    
    def save_file(self, data: Any, relative_path: str, format_type: str = "auto") -> None:
        """
        Save data to cache with metadata.
        
        Args:
            data: Data to save (DataFrame, xarray Dataset, etc.)
            relative_path: Relative path for the file
            format_type: Format type for saving ("auto", "parquet", "netcdf", etc.)
        """
        with self._file_lock(relative_path):
            cache_file_path = self.get_cache_file_path(relative_path)
            
            # Ensure parent directories exist
            cache_file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Determine format from file extension if auto
            if format_type == "auto":
                file_ext = cache_file_path.suffix.lower()
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
                    raise ValueError(f"Cannot determine format for file extension: {file_ext}")
            
            # Save data based on format
            if format_type == "netcdf":
                # For NetCDF, ensure data is loaded into memory to avoid file locking issues
                if hasattr(data, 'load'):
                    data = data.load()
                
                # Fix encoding issues with NetCDF by explicitly setting encoding
                if hasattr(data, 'data_vars'):
                    encoding = {}
                    # Clean data attributes to avoid encoding conflicts
                    data_cleaned = data.copy()
                    
                    # Set consistent encoding for all variables
                    for var_name in data.data_vars:
                        var = data[var_name]
                        # Use explicit encoding to avoid conflicts
                        var_encoding = {
                            'zlib': True,  # Enable compression
                            'complevel': 6,
                            'shuffle': True
                        }
                        
                        # Handle fill values properly - remove from attrs to avoid conflicts
                        if hasattr(var, 'attrs'):
                            var_attrs = var.attrs.copy()
                            if '_FillValue' in var_attrs:
                                var_encoding['_FillValue'] = var_attrs['_FillValue']
                                # Remove from attrs to prevent double-setting
                                del var_attrs['_FillValue']
                                data_cleaned[var_name].attrs = var_attrs
                            elif 'missing_value' in var_attrs:
                                var_encoding['_FillValue'] = var_attrs['missing_value']
                                # Remove missing_value to prevent conflicts
                                del var_attrs['missing_value']
                                data_cleaned[var_name].attrs = var_attrs
                        
                        encoding[var_name] = var_encoding
                    
                    # Use atomic write via temporary file to avoid permission issues
                    import tempfile
                    import os
                    
                    # Create temporary file in the same directory as target file
                    cache_dir = cache_file_path.parent
                    with tempfile.NamedTemporaryFile(
                        dir=cache_dir, 
                        suffix='.nc.tmp', 
                        delete=False
                    ) as tmp_file:
                        tmp_path = tmp_file.name
                    
                    try:
                        # Save to temporary file with explicit encoding
                        data_cleaned.to_netcdf(tmp_path, encoding=encoding)
                        # Atomic move to final location
                        os.rename(tmp_path, cache_file_path)
                    except Exception:
                        # Clean up temporary file if save failed
                        if os.path.exists(tmp_path):
                            os.unlink(tmp_path)
                        raise
                else:
                    # For non-Dataset objects, use atomic write as well
                    import tempfile
                    import os
                    
                    cache_dir = cache_file_path.parent
                    with tempfile.NamedTemporaryFile(
                        dir=cache_dir, 
                        suffix='.nc.tmp', 
                        delete=False
                    ) as tmp_file:
                        tmp_path = tmp_file.name
                    
                    try:
                        data.to_netcdf(tmp_path)
                        os.rename(tmp_path, cache_file_path)
                    except Exception:
                        if os.path.exists(tmp_path):
                            os.unlink(tmp_path)
                        raise
            elif format_type == "parquet":
                data.to_parquet(cache_file_path, index=False)
            elif format_type == "csv":
                data.to_csv(cache_file_path, index=False)
            elif format_type == "excel":
                data.to_excel(cache_file_path, index=False)
            elif format_type == "pickle":
                import pickle
                with open(cache_file_path, 'wb') as f:
                    pickle.dump(data, f)
            else:
                raise ValueError(f"Unsupported format type: {format_type}")
            
            # Calculate file metadata
            checksum = self._calculate_checksum(cache_file_path)
            size_bytes = cache_file_path.stat().st_size
            created_at = datetime.now(timezone.utc).isoformat()
            
            # Update metadata (no TTL or backend - these come from current config)
            cache_metadata = CacheMetadata(
                created_at=created_at,
                checksum=checksum,
                size_bytes=size_bytes,
                sync_status="local"
            )
            
            self._update_file_metadata(relative_path, cache_metadata)
    
    def load_file(self, relative_path: str, format_type: str = "auto") -> Any:
        """
        Load data from cache.
        
        Args:
            relative_path: Relative path of the file
            format_type: Format type for loading ("auto", "parquet", "netcdf", etc.)
            
        Returns:
            Loaded data (DataFrame, xarray Dataset, etc.)
            
        Raises:
            FileNotFoundError: If file doesn't exist in cache
        """
        cache_file_path = self.get_cache_file_path(relative_path)
        
        if not cache_file_path.exists():
            raise FileNotFoundError(f"File not found in cache: {relative_path}")
        
        # Determine format from file extension if auto
        if format_type == "auto":
            file_ext = cache_file_path.suffix.lower()
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
                raise ValueError(f"Cannot determine format for file extension: {file_ext}")
        
        # Load data based on format
        if format_type == "netcdf":
            import xarray as xr
            return xr.open_dataset(cache_file_path)
        elif format_type == "parquet":
            import pandas as pd
            return pd.read_parquet(cache_file_path)
        elif format_type == "csv":
            import pandas as pd
            return pd.read_csv(cache_file_path)
        elif format_type == "excel":
            import pandas as pd
            return pd.read_excel(cache_file_path)
        elif format_type == "pickle":
            import pickle
            with open(cache_file_path, 'rb') as f:
                return pickle.load(f)
        else:
            raise ValueError(f"Unsupported format type: {format_type}")
    
    def _update_file_metadata(self, relative_path: str, cache_metadata: CacheMetadata) -> None:
        """Update metadata for a specific file."""
        metadata = self._read_metadata()
        metadata["files"][relative_path] = asdict(cache_metadata)
        self._write_metadata(metadata)
    
    def update_sync_status(self, relative_path: str, sync_status: str, 
                          last_sync: Optional[str] = None) -> None:
        """
        Update sync status for a cached file.
        
        Args:
            relative_path: Relative path of the file
            sync_status: New sync status ("local", "synced", "pending", "failed")
            last_sync: ISO format timestamp of last sync (optional)
        """
        with self._file_lock(relative_path):
            metadata = self._read_metadata()
            file_metadata = metadata.get("files", {}).get(relative_path)
            
            if file_metadata:
                file_metadata["sync_status"] = sync_status
                if last_sync:
                    file_metadata["last_sync"] = last_sync
                
                self._write_metadata(metadata)
    
    def list_cached_files(self) -> List[str]:
        """
        List all files in cache.
        
        Returns:
            List of relative paths of cached files
        """
        metadata = self._read_metadata()
        return list(metadata.get("files", {}).keys())
    
    def list_stale_files(self) -> List[str]:
        """
        List all stale files in cache (beyond TTL).
        
        Returns:
            List of relative paths of stale files
        """
        stale_files = []
        for relative_path in self.list_cached_files():
            if not self.is_data_fresh(relative_path):
                stale_files.append(relative_path)
        return stale_files
    
    def remove_file(self, relative_path: str) -> None:
        """
        Remove a file from cache and its metadata.
        
        Args:
            relative_path: Relative path of the file to remove
        """
        with self._file_lock(relative_path):
            # Remove physical file
            cache_file_path = self.get_cache_file_path(relative_path)
            if cache_file_path.exists():
                cache_file_path.unlink()
            
            # Remove metadata
            metadata = self._read_metadata()
            if relative_path in metadata.get("files", {}):
                del metadata["files"][relative_path]
                self._write_metadata(metadata)
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        metadata = self._read_metadata()
        files = metadata.get("files", {})
        
        total_files = len(files)
        total_size = sum(f.get("size_bytes", 0) for f in files.values())
        
        fresh_files = sum(1 for path in files.keys() if self.is_data_fresh(path))
        stale_files = total_files - fresh_files
        
        backends = {}
        for file_meta in files.values():
            backend = file_meta.get("backend", "unknown")
            backends[backend] = backends.get(backend, 0) + 1
        
        return {
            "total_files": total_files,
            "fresh_files": fresh_files,
            "stale_files": stale_files,
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "backends": backends,
            "cache_base_path": str(self.cache_base_path)
        }
