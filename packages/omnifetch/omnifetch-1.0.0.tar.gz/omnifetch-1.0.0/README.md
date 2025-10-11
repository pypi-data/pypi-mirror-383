# omnifetch

**Multi-source data retrieval with intelligent caching and storage backends**

Fetch data from anywhere, any type - with automatic TTL-based caching, multiple storage backends, and smart synchronization.

## ✨ Features

- ✅ **Multi-source data retrieval** - Local files, IBM Cloud Object Storage, or custom backends
- ✅ **Intelligent TTL-based caching** - Automatic freshness management
- ✅ **Concurrent access protection** - File locking for safe multi-process usage
- ✅ **Batch operations** - Efficient bulk data retrieval
- ✅ **Retry strategies** - Configurable retry logic for reliability
- ✅ **Multiple data formats** - Parquet, CSV, NetCDF, pickle, and more
- ✅ **Session caching** - In-memory cache for single-run optimization
- ✅ **Flexible configuration** - YAML-based or programmatic setup

## 📦 Installation

### From GitHub

```bash
pip install git+https://github.com/deinnovatie/omnifetch.git
```

### Local development

```bash
git clone https://github.com/deinnovatie/omnifetch.git
cd omnifetch
pip install -e ".[dev]"
```

## 🚀 Quick Start

### Basic Usage

```python
from omnifetch import DataManager

# Initialize with configuration
config = {
    "storage": {
        "backend": "local",
        "local": {
            "base_path": "./data"
        }
    },
    "data_sources": {
        "my_dataset": {
            "backend": "local",
            "ttl_seconds": 3600,  # 1 hour
            "file_patterns": {
                "default": "datasets/my_data.parquet"
            }
        }
    }
}

manager = DataManager(config)

# Fetch data (automatically cached)
data = manager.get_data("my_dataset", "default")

# Force refresh from source
fresh_data = manager.get_data("my_dataset", "default", force_refresh=True)
```

### With IBM Cloud Object Storage

```python
import os
from omnifetch import DataManager

# Set environment variables
os.environ["COS_ENDPOINT"] = "https://s3.us-south.cloud-object-storage.appdomain.cloud"
os.environ["COS_ACCESS_KEY"] = "your-access-key"
os.environ["COS_SECRET_KEY"] = "your-secret-key"
os.environ["COS_BUCKET"] = "your-bucket-name"

config = {
    "storage": {
        "backend": "ibm_cos",
        "ibm_cos": {
            "bucket_name": os.environ["COS_BUCKET"],
            "service_endpoint": os.environ["COS_ENDPOINT"],
            "access_key_env": "COS_ACCESS_KEY",
            "secret_key_env": "COS_SECRET_KEY"
        },
        "local": {
            "base_path": "./cache"
        }
    },
    "data_sources": {
        "cloud_dataset": {
            "backend": "ibm_cos",
            "ttl_seconds": 86400,  # 24 hours
            "file_patterns": {
                "default": "datasets/cloud_data.parquet"
            }
        }
    }
}

manager = DataManager(config)
data = manager.get_data("cloud_dataset", "default")
```

### Using YAML Configuration Adapter

```python
from omnifetch.adapters import create_datamanager_config

# Load configuration from YAML file (e.g., R pipeline config)
config = create_datamanager_config(config_path="./config/data_sources.yml")

manager = DataManager(config)
data = manager.get_data("dataset_name", "default")
```

### Batch Operations

```python
from omnifetch import DataManager, FileSpec

manager = DataManager(config)

# Define multiple files to fetch
specs = [
    FileSpec("dataset_a", "default", {}),
    FileSpec("dataset_b", "default", {}),
    FileSpec("dataset_c", "regional", {"region": "us-east"}),
]

# Fetch all at once
results = manager.get_data_batch(specs)

for spec, data in zip(specs, results):
    print(f"Loaded {spec.data_source}: {data.shape}")
```

### Cache Management

```python
# Get cache statistics
stats = manager.get_cache_stats()
print(f"Total cached files: {stats['file_count']}")
print(f"Fresh files: {stats['fresh_count']}")
print(f"Stale files: {stats['stale_count']}")

# Clear session cache (in-memory only)
manager.clear_session_cache()
```

## 🗂️ Configuration

### Configuration Structure

```yaml
storage:
  backend: "ibm_cos"  # or "local"
  ibm_cos:
    bucket_name: "my-bucket"
    service_endpoint: "https://s3.region.cloud-object-storage.appdomain.cloud"
    access_key_env: "COS_ACCESS_KEY"
    secret_key_env: "COS_SECRET_KEY"
  local:
    base_path: "./cache"

data_sources:
  dataset_name:
    backend: "ibm_cos"  # Backend for this specific dataset
    ttl_seconds: 86400  # 24 hours (supports: "30d", "24h", "60m", "3600s", or integer)
    file_patterns:
      default: "path/to/file.parquet"
      regional: "path/to/{region}/file.parquet"  # With parameters
    validation:
      required_columns: ["id", "timestamp", "value"]
    retry_strategy:
      max_retries: 3
      retry_delay: 5
      backoff_multiplier: 2.0
```

### TTL Format

TTL can be specified in multiple formats:

- **Seconds**: `3600` or `"3600s"`
- **Minutes**: `"60m"`
- **Hours**: `"24h"`
- **Days**: `"30d"`
- **Weeks**: `"4w"`

### File Patterns with Parameters

```python
# Configuration
data_sources:
  regional_data:
    file_patterns:
      default: "data/{year}/{month}/{region}.parquet"

# Usage
data = manager.get_data(
    "regional_data",
    "default",
    year="2024",
    month="10",
    region="us-east"
)
# Fetches: data/2024/10/us-east.parquet
```

## 🔧 Supported Storage Backends

### Local Filesystem

```python
config = {
    "storage": {
        "backend": "local",
        "local": {
            "base_path": "./data_repository"
        }
    }
}
```

### IBM Cloud Object Storage (COS)

```python
config = {
    "storage": {
        "backend": "ibm_cos",
        "ibm_cos": {
            "bucket_name": "my-bucket",
            "service_endpoint": "https://s3.us-south.cloud-object-storage.appdomain.cloud",
            "access_key_env": "COS_ACCESS_KEY",
            "secret_key_env": "COS_SECRET_KEY"
        },
        "local": {
            "base_path": "./cache"  # Local cache for downloaded files
        }
    }
}
```

### Custom Backends

Extend `StorageBackend` to create your own:

```python
from omnifetch.storage_backends import StorageBackend

class MyCustomBackend(StorageBackend):
    def exists(self, path: str) -> bool:
        # Implementation
        pass

    def save(self, data, path: str, format: str = "parquet") -> None:
        # Implementation
        pass

    def load(self, path: str, format: str = "parquet"):
        # Implementation
        pass

    # ... implement other abstract methods
```

## 📊 Supported Data Formats

- **Parquet** - Columnar storage (via PyArrow)
- **CSV** - Comma-separated values (via Pandas)
- **NetCDF** - Multidimensional arrays (via xarray/netCDF4)
- **Pickle** - Python object serialization
- **JSON** - Structured data

Format is auto-detected from file extension or can be specified explicitly.

## 🔍 How It Works

### Data Retrieval Flow

```
1. Request data from DataManager
   ↓
2. Check session cache (in-memory)
   ↓ (miss)
3. Check local disk cache with TTL
   ↓ (miss or stale)
4. Download from remote backend (IBM COS, etc.)
   ↓
5. Save to local cache with metadata
   ↓
6. Load from cache and store in session
   ↓
7. Return data to caller
```

### Cache Architecture

```
┌─────────────────────────────────────┐
│     DataManager (Session Cache)     │  <- In-memory, per-run
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│   CacheManager (Disk Cache + TTL)   │  <- Persistent, with metadata
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  SyncManager (Backend Sync Logic)   │  <- Download/upload coordination
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│    StorageBackend (Local/IBM COS)   │  <- Actual data source
└─────────────────────────────────────┘
```

## 🧪 Testing

```bash
# Run tests
pytest

# With coverage
pytest --cov=omnifetch --cov-report=html

# Run specific test
pytest tests/test_data_manager.py::test_get_data_from_cache
```

## 📝 Examples

See the `examples/` directory for complete working examples:

- [basic_usage.py](examples/basic_usage.py) - Basic local file caching
- [ibm_cos_example.py](examples/ibm_cos_example.py) - IBM COS integration
- [yaml_config_example.py](examples/yaml_config_example.py) - YAML configuration
- [custom_backend_example.py](examples/custom_backend_example.py) - Custom storage backend

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

Originally developed as part of the SIMEG R Toolkit project for energy market simulations.

## 📧 Contact

Marco Bonoli - marco@deinnovatie.com

Project Link: [https://github.com/deinnovatie/omnifetch](https://github.com/deinnovatie/omnifetch)
