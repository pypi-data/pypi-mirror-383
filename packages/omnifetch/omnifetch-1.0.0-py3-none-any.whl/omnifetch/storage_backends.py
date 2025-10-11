"""
Storage Backend Abstraction Layer

This module provides an abstraction layer for different storage backends,
making it easy to switch between local file system and cloud object storage.
"""

import os
import io
import pickle
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import pandas as pd
import logging
from pathlib import Path
from datetime import datetime


class StorageBackend(ABC):
    """Abstract base class for storage backends."""
    
    @abstractmethod
    def exists(self, path: str) -> bool:
        """Check if a file/object exists."""
        pass
    
    @abstractmethod
    def save(self, data, path: str, format: str = "parquet") -> None:
        """Save data to storage. Can be DataFrame or xarray Dataset."""
        pass
    
    @abstractmethod
    def load(self, path: str, format: str = "parquet"):
        """Load data from storage. Returns DataFrame or xarray Dataset."""
        pass
    
    @abstractmethod
    def delete(self, path: str) -> None:
        """Delete a file/object from storage."""
        pass
    
    @abstractmethod
    def list_files(self, prefix: str = "") -> list:
        """List all files/objects with optional prefix filter."""
        pass
    
    @abstractmethod
    def get_file_metadata(self, path: str) -> Optional[Dict[str, Any]]:
        """Get file metadata without downloading content.
        
        Returns:
            Dictionary with metadata:
            - last_modified: datetime of last modification
            - size: file size in bytes
            - etag: entity tag/checksum (if available)
            Returns None if file doesn't exist.
        """
        pass
    
    # Batch operations for efficient bulk storage
    def begin_batch(self) -> None:
        """Begin a batch operation context. Default implementation is no-op."""
        pass
    
    def add_to_batch(self, data, path: str, format: str = "parquet") -> None:
        """Add an operation to the current batch. Default implementation calls save immediately."""
        self.save(data, path, format)
    
    def commit_batch(self) -> dict:
        """Commit all batched operations. Default implementation is no-op."""
        return {"status": "success", "operations": 0}
    
    def rollback_batch(self) -> None:
        """Rollback all batched operations. Default implementation is no-op."""
        pass


class LocalStorageBackend(StorageBackend):
    """Local file system storage backend."""
    
    def __init__(self, base_path: str):
        """
        Initialize local storage backend.
        
        Args:
            base_path: Base directory for all file operations
        """
        self.base_path = Path(base_path)
        # Create base directory if it doesn't exist
        self.base_path.mkdir(parents=True, exist_ok=True)
    
    def _get_full_path(self, path: str) -> Path:
        """Get full path by combining base path with relative path."""
        return self.base_path / path
    
    def exists(self, path: str) -> bool:
        """Check if a file exists."""
        full_path = self._get_full_path(path)
        return full_path.exists()
    
    def save(self, data, path: str, format: str = "parquet") -> None:
        """Save data to local file system. Can be DataFrame or xarray Dataset."""
        full_path = self._get_full_path(path)
        
        # Create parent directories if they don't exist
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save based on format
        if format == "parquet":
            data.to_parquet(full_path, index=False)
        elif format == "csv":
            data.to_csv(full_path, index=False)
        elif format == "excel":
            data.to_excel(full_path, index=False)
        elif format == "netcdf":
            # For xarray Datasets
            data.to_netcdf(full_path)
        elif format == "pickle":
            # For any Python object
            with open(full_path, 'wb') as f:
                pickle.dump(data, f)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def load(self, path: str, format: str = "parquet") -> pd.DataFrame:
        """Load a DataFrame from local file system."""
        full_path = self._get_full_path(path)
        
        if not full_path.exists():
            raise FileNotFoundError(f"File not found: {full_path}")
        
        # Load based on format
        if format == "parquet":
            return pd.read_parquet(full_path)
        elif format == "csv":
            return pd.read_csv(full_path)
        elif format == "excel":
            return pd.read_excel(full_path)
        elif format == "netcdf":
            import xarray as xr
            return xr.open_dataset(full_path)
        elif format == "pickle":
            # Load any Python object
            with open(full_path, 'rb') as f:
                return pickle.load(f)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def delete(self, path: str) -> None:
        """Delete a file from local file system."""
        full_path = self._get_full_path(path)
        if full_path.exists():
            full_path.unlink()
    
    def list_files(self, prefix: str = "") -> list:
        """List all files with optional prefix filter."""
        search_path = self._get_full_path(prefix) if prefix else self.base_path
        
        if search_path.is_dir():
            # List all files recursively
            files = []
            for item in search_path.rglob("*"):
                if item.is_file():
                    # Get relative path from base_path
                    rel_path = item.relative_to(self.base_path)
                    files.append(str(rel_path))
            return sorted(files)
        else:
            # If it's a file pattern, use parent directory
            pattern = search_path.name
            parent = search_path.parent
            files = []
            for item in parent.glob(pattern):
                if item.is_file():
                    rel_path = item.relative_to(self.base_path)
                    files.append(str(rel_path))
            return sorted(files)
    
    def get_file_metadata(self, path: str) -> Optional[Dict[str, Any]]:
        """Get file metadata for local file."""
        full_path = self._get_full_path(path)
        
        if not full_path.exists():
            return None
        
        stat = full_path.stat()
        return {
            'last_modified': datetime.fromtimestamp(stat.st_mtime),
            'size': stat.st_size,
            'etag': None  # Not available for local files
        }


class IBMCOSBackend(StorageBackend):
    """IBM Cloud Object Storage backend with batch upload support."""
    
    def __init__(self, bucket_name: str, service_endpoint: str, 
                 api_key: str = None, instance_id: str = None,
                 access_key: str = None, secret_key: str = None):
        """
        Initialize IBM COS backend.
        
        Args:
            bucket_name: Name of the COS bucket
            service_endpoint: COS service endpoint URL
            api_key: IBM Cloud API key (for OAuth authentication)
            instance_id: COS instance ID (CRN) (for OAuth authentication)
            access_key: Access key (for HMAC authentication)
            secret_key: Secret key (for HMAC authentication)
        """
        try:
            import ibm_boto3
            from ibm_botocore.client import Config
        except ImportError:
            raise ImportError(
                "IBM COS SDK not installed. Install with: pip install ibm-cos-sdk"
            )
        
        self.bucket_name = bucket_name
        self.service_endpoint = service_endpoint
        self.access_key = access_key
        self.secret_key = secret_key

        # Use HMAC authentication if access_key and secret_key are provided
        if access_key and secret_key:
            self.cos = ibm_boto3.client(
                's3',
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
                config=Config(signature_version='s3v4'),
                endpoint_url=service_endpoint
            )
        # Otherwise use OAuth authentication
        elif api_key and instance_id:
            self.cos = ibm_boto3.client(
                's3',
                ibm_api_key_id=api_key,
                ibm_service_instance_id=instance_id,
                config=Config(signature_version='oauth'),
                endpoint_url=service_endpoint
            )
        else:
            raise ValueError(
                "Either (access_key, secret_key) or (api_key, instance_id) must be provided"
            )

        # Batch operation state
        self._batch_operations = []
        self._batch_active = False
    
    def get_file_metadata(self, path: str) -> Optional[Dict[str, Any]]:
        """Get file metadata from IBM COS without downloading content."""
        try:
            response = self.cos.head_object(Bucket=self.bucket_name, Key=path)
            return {
                'last_modified': response['LastModified'],
                'size': response['ContentLength'],
                'etag': response.get('ETag', '').strip('"')  # Remove quotes from ETag
            }
        except Exception:
            return None
    
    def exists(self, path: str) -> bool:
        """Check if an object exists in COS."""
        try:
            self.cos.head_object(Bucket=self.bucket_name, Key=path)
            return True
        except:
            return False
    
    def save(self, data, path: str, format: str = "parquet") -> None:
        """Save data to IBM COS. Can be DataFrame or xarray Dataset."""
        # Convert DataFrame to bytes
        buffer = io.BytesIO()
        
        if format == "parquet":
            data.to_parquet(buffer, index=False)
            content_type = "application/octet-stream"
        elif format == "csv":
            data.to_csv(buffer, index=False)
            content_type = "text/csv"
        elif format == "excel":
            data.to_excel(buffer, index=False)
            content_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        elif format == "netcdf":
            # For xarray Datasets
            # Note: to_netcdf() closes the buffer, so we create a temporary file instead
            import tempfile
            with tempfile.NamedTemporaryFile() as tmp_file:
                data.to_netcdf(tmp_file.name)
                tmp_file.seek(0)
                buffer_content = tmp_file.read()
            content_type = "application/octet-stream"
        elif format == "pickle":
            # For any Python object
            pickle.dump(data, buffer)
            content_type = "application/octet-stream"
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        # Upload to COS
        if format == "netcdf":
            # For NetCDF, use the content we got before buffer was closed
            self.cos.put_object(
                Bucket=self.bucket_name,
                Key=path,
                Body=buffer_content,
                ContentType=content_type
            )
        else:
            # For other formats, buffer is still open
            buffer.seek(0)
            self.cos.put_object(
                Bucket=self.bucket_name,
                Key=path,
                Body=buffer.read(),
                ContentType=content_type
            )
    
    def load(self, path: str, format: str = "parquet") -> pd.DataFrame:
        """Load a DataFrame from IBM COS."""
        # Download from COS
        response = self.cos.get_object(Bucket=self.bucket_name, Key=path)
        body = response['Body'].read()
        buffer = io.BytesIO(body)
        
        # Load based on format
        if format == "parquet":
            return pd.read_parquet(buffer)
        elif format == "csv":
            return pd.read_csv(buffer)
        elif format == "excel":
            return pd.read_excel(buffer)
        elif format == "netcdf":
            import xarray as xr
            return xr.open_dataset(buffer)
        elif format == "pickle":
            # Load any Python object
            buffer.seek(0)
            return pickle.load(buffer)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def delete(self, path: str) -> None:
        """Delete an object from IBM COS."""
        self.cos.delete_object(Bucket=self.bucket_name, Key=path)
    
    def list_files(self, prefix: str = "") -> list:
        """List all objects with optional prefix filter."""
        files = []
        
        # Use paginator for large buckets
        paginator = self.cos.get_paginator('list_objects_v2')
        page_iterator = paginator.paginate(
            Bucket=self.bucket_name,
            Prefix=prefix
        )
        
        for page in page_iterator:
            if 'Contents' in page:
                for obj in page['Contents']:
                    files.append(obj['Key'])
        
        return sorted(files)
    
    def begin_batch(self) -> None:
        """Begin a batch operation context for IBM COS."""
        self._batch_operations = []
        self._batch_active = True
    
    def add_to_batch(self, data, path: str, format: str = "parquet") -> None:
        """Add an operation to the current batch instead of executing immediately."""
        if not self._batch_active:
            # If no batch is active, execute immediately
            self.save(data, path, format)
            return
        
        # Store operation for later batch execution
        self._batch_operations.append({
            "data": data,
            "path": path,
            "format": format
        })
    
    def commit_batch(self) -> dict:
        """Commit all batched operations efficiently using bulk upload."""
        if not self._batch_active:
            return {"status": "no_batch_active", "operations": 0}
        
        try:
            # Execute all batched operations
            successful_operations = 0
            failed_operations = []
            total_operations = len(self._batch_operations)
            
            for i, operation in enumerate(self._batch_operations):
                try:
                    self.save(
                        operation["data"], 
                        operation["path"], 
                        operation["format"]
                    )
                    successful_operations += 1
                except Exception as e:
                    failed_operations.append({
                        "operation_index": i,
                        "path": operation["path"],
                        "error": str(e)
                    })
            
            # Reset batch state
            self._batch_operations = []
            self._batch_active = False
            
            result = {
                "status": "success" if len(failed_operations) == 0 else "partial",
                "operations_attempted": total_operations,
                "operations_successful": successful_operations,
                "operations_failed": len(failed_operations),
                "failed_operations": failed_operations
            }
            
            return result
            
        except Exception as e:
            # Reset batch state on error
            self._batch_operations = []
            self._batch_active = False
            raise Exception(f"Batch commit failed: {str(e)}")
    
    def rollback_batch(self) -> None:
        """Rollback all batched operations (clear the batch queue)."""
        self._batch_operations = []
        self._batch_active = False

    def query_remote_parquet(self, sql_query: str, file_aliases: Dict[str, str]) -> pd.DataFrame:
        """
        Execute a SQL query on one or more remote Parquet files without downloading them.
        Uses DuckDB with HTTP range requests to only fetch required data.

        Supports JOINs across multiple remote Parquet files.

        Args:
            sql_query: SQL query with file aliases as placeholders.
                      Example: "SELECT * FROM {psem_data} WHERE fecha >= '2025-01-01'"
                      Example JOIN: "SELECT a.*, b.costo FROM {psem_data} a JOIN {costos} b ON a.id = b.id"
            file_aliases: Dictionary mapping alias names to S3 Parquet paths.
                         Example: {'psem_data': 'path/to/psem.parquet', 'costos': 'path/to/costos.parquet'}

        Returns:
            pandas.DataFrame with query results

        Raises:
            ImportError: If DuckDB is not installed
            ValueError: If HMAC credentials are not available or file is not Parquet format
        """
        try:
            import duckdb
        except ImportError:
            raise ImportError(
                "DuckDB not installed. Install with: pip install duckdb"
            )

        # DuckDB requires HMAC credentials (access key / secret key)
        if not self.access_key or not self.secret_key:
            raise ValueError(
                "Remote query requires HMAC credentials (access_key/secret_key). "
                "OAuth authentication is not supported for DuckDB remote queries."
            )

        # Create DuckDB connection
        con = duckdb.connect()

        # Configure S3/COS connection
        endpoint_host = self.service_endpoint.replace('https://', '').replace('http://', '')

        con.execute("INSTALL httpfs;")
        con.execute("LOAD httpfs;")
        con.execute(f"SET s3_endpoint='{endpoint_host}';")
        con.execute(f"SET s3_access_key_id='{self.access_key}';")
        con.execute(f"SET s3_secret_access_key='{self.secret_key}';")
        con.execute("SET s3_url_style='path';")

        # Replace file aliases with actual S3 paths (Parquet only)
        final_query = sql_query
        for alias, path in file_aliases.items():
            s3_path = f"s3://{self.bucket_name}/{path}"

            # Verify Parquet format
            if not path.endswith(('.parquet', '.pq')):
                raise ValueError(
                    f"Unsupported file format for '{alias}': {path}. "
                    f"Only Parquet (.parquet, .pq) is supported for remote queries. "
                    f"For other formats, use DataManager.get_data() instead."
                )

            # Parquet: direct path
            read_expr = f"'{s3_path}'"

            # Replace {alias} with read expression
            final_query = final_query.replace(f'{{{alias}}}', read_expr)

        logging.getLogger(__name__).info(
            f"Executing remote Parquet query on {len(file_aliases)} file(s): {final_query[:200]}..."
        )

        # Execute query and return DataFrame
        result_df = con.execute(final_query).fetchdf()
        con.close()

        return result_df


def get_storage_backend(config: Dict[str, Any]) -> StorageBackend:
    """
    Factory function to create appropriate storage backend based on configuration.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        StorageBackend instance
    """
    # Default to local storage if not specified
    storage_config = config.get("storage", {})
    backend_type = storage_config.get("backend", "local")
    
    if backend_type == "local":
        # Use local storage
        local_config = storage_config.get("local", {})
        base_path = local_config.get("base_path", "./data_repo")
        
        # Check for DATA_PATH environment variable override
        if "DATA_PATH" in os.environ:
            base_path = os.environ["DATA_PATH"]
        
        return LocalStorageBackend(base_path)
    
    elif backend_type == "ibm_cos":
        # Use IBM COS
        cos_config = storage_config.get("ibm_cos", {})
        
        # Check for HMAC credentials first
        access_key = os.environ.get(cos_config.get("access_key_env", "COS_ACCESS_KEY"))
        secret_key = os.environ.get(cos_config.get("secret_key_env", "COS_SECRET_KEY"))
        
        # Check for OAuth credentials
        api_key = os.environ.get(cos_config.get("api_key_env", "IBM_COS_API_KEY"))
        instance_id = os.environ.get(cos_config.get("instance_id_env", "IBM_COS_INSTANCE_ID"))
        
        if access_key and secret_key:
            # Use HMAC authentication
            return IBMCOSBackend(
                bucket_name=cos_config["bucket_name"],
                service_endpoint=cos_config["service_endpoint"],
                access_key=access_key,
                secret_key=secret_key
            )
        elif api_key and instance_id:
            # Use OAuth authentication
            return IBMCOSBackend(
                bucket_name=cos_config["bucket_name"],
                service_endpoint=cos_config["service_endpoint"],
                api_key=api_key,
                instance_id=instance_id
            )
        else:
            raise ValueError(
                "IBM COS credentials not found in environment variables. "
                "Please set either (COS_ACCESS_KEY and COS_SECRET_KEY) or "
                "(IBM_COS_API_KEY and IBM_COS_INSTANCE_ID)."
            )
    
    else:
        raise ValueError(f"Unknown storage backend: {backend_type}")