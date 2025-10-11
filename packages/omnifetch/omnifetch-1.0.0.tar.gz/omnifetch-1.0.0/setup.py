"""Setup configuration for omnifetch."""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text() if readme_file.exists() else ""

setup(
    name="omnifetch",
    version="1.0.0",
    description="Multi-source data retrieval with intelligent caching and storage backends",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Marco Bonoli",
    author_email="marco@deinnovatie.com",
    url="https://github.com/deinnovatie/omnifetch",
    packages=find_packages(exclude=["tests", "tests.*", "examples"]),
    install_requires=[
        "ibm-cos-sdk>=2.13.3",
        "filelock>=3.13.1",
        "pandas>=2.1.4",
        "xarray>=2023.12.0",
        "netCDF4>=1.6.5",
        "pyarrow>=14.0.1",
        "pyyaml>=6.0.1",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "black>=23.0.0",
            "ruff>=0.1.0",
            "mypy>=1.5.0",
        ],
        "docs": [
            "sphinx>=7.0.0",
            "sphinx-rtd-theme>=1.3.0",
        ],
    },
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering",
    ],
    keywords="data-management caching storage ibm-cos cloud-storage ttl multi-source",
)
