# Hyper Python Utils

![Version](https://img.shields.io/badge/version-0.3.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-green.svg)
![PyPI](https://img.shields.io/pypi/v/hyper-python-utils.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

AWS S3 and Athena utilities for data processing with Pandas and Polars.

## Installation

```bash
pip install hyper-python-utils
```

## Features

- **Simple Query Functions (New in v0.2.0)**: Easy-to-use wrapper functions
  - `query()`: Execute Athena queries with minimal setup
  - `query_unload()`: High-performance queries for large datasets using UNLOAD
  - Support for both Pandas and Polars DataFrames
  - Automatic cleanup and optimized performance

- **FileHandler**: S3 file operations with Polars DataFrames
  - Upload/download CSV and Parquet files
  - Parallel loading of multiple files
  - Partitioned uploads by range or date
  - Support for compressed formats

- **QueryManager**: Advanced Athena query execution and management
  - Execute queries with result monitoring
  - Clean up query result files
  - Error handling and timeouts
  - Full control over query execution

## Quick Start

### Simple Query Functions (Recommended for Most Use Cases)

The easiest way to query Athena data:

```python
import hyper_python_utils as hp

# Execute a simple query (returns pandas DataFrame by default)
df = hp.query(
    database="my_database",
    query="SELECT * FROM my_table LIMIT 100"
)
print(df)
print(type(df))  # <class 'pandas.core.frame.DataFrame'>

# Get results as polars DataFrame
df = hp.query(
    database="my_database",
    query="SELECT * FROM my_table LIMIT 100",
    option="polars"
)
print(type(df))  # <class 'polars.dataframe.frame.DataFrame'>

# For large datasets, use UNLOAD (4x faster, optimized with Parquet + GZIP)
df = hp.query_unload(
    database="my_database",
    query="SELECT * FROM large_table WHERE date > '2024-01-01'"
)
# Returns pandas DataFrame by default, add option="polars" for Polars

# Queries with semicolons are automatically handled
df = hp.query(database="my_database", query="SELECT * FROM table;")  # Works fine!
```

**Key Features:**
- Pre-configured with optimal settings (bucket: `athena-query-results-for-hyper`)
- Automatic cleanup of temporary files
- No exceptions on empty results (returns empty DataFrame)
- Query execution time displayed in logs
- `query_unload()` uses Parquet + GZIP for 4x performance boost

**When to use which?**
- `query()`: Normal queries, small to medium datasets (< 1M rows)
- `query_unload()`: Large datasets (> 1M rows), when performance matters

### FileHandler Usage

```python
from hyper_python_utils import FileHandler
import polars as pl

# Initialize FileHandler
handler = FileHandler(bucket="my-s3-bucket", region="ap-northeast-2")

# Read a file from S3
df = handler.get_object("data/sample.parquet")

# Upload a DataFrame to S3
sample_df = pl.DataFrame({"col1": [1, 2, 3], "col2": ["a", "b", "c"]})
handler.upload_dataframe(sample_df, "output/result.parquet", "parquet")

# Upload with partitioning by range
handler.upload_dataframe_partitioned_by_range(
    df, "partitioned_data/", partition_size=50000
)

# Load all files from a prefix in parallel
combined_df = handler.load_all_objects_parallel("data/batch_*/", max_workers=4)
```

### QueryManager Usage (Advanced)

For advanced use cases requiring custom configuration:

```python
from hyper_python_utils import QueryManager
import polars as pl

# Initialize QueryManager with custom settings
query_manager = QueryManager(
    bucket="my-athena-results",
    result_prefix="custom/query_results/",
    auto_cleanup=True  # Default: True - automatically delete query result files after reading
)

# Method 1: Execute query and get DataFrame result directly
query = "SELECT * FROM my_table LIMIT 100"
df = query_manager.query(query, database="my_database")
print(df)  # Returns empty DataFrame if no results (no exception thrown)

# Choose output format (new in v0.2.0)
df_polars = query_manager.query(query, database="my_database", output_format="polars")
df_pandas = query_manager.query(query, database="my_database", output_format="pandas")

# Method 2: Manual query execution with result retrieval
query_id = query_manager.execute(query, database="my_database")
result_location = query_manager.wait_for_completion(query_id)
df = query_manager.get_result(query_id)  # Auto cleanup based on QueryManager setting

# Method 2b: Override auto cleanup for specific query
df_no_cleanup = query_manager.get_result(query_id, auto_cleanup=False)  # Keep result file

# Method 3: Execute UNLOAD query and get list of output files
unload_query = """
UNLOAD (SELECT * FROM my_large_table)
TO 's3://my-bucket/unloaded-data/'
WITH (format = 'PARQUET', compression = 'GZIP')
"""
output_files = query_manager.unload(unload_query, database="my_database")
print(f"Unloaded files: {output_files}")

# Manual cleanup of query results
query_manager.delete_query_results_by_prefix("s3://my-bucket/old-results/")

# Disable auto cleanup for all queries
query_manager_no_cleanup = QueryManager(
    bucket="my-athena-results",
    auto_cleanup=False
)
```

## Requirements

- Python >= 3.8
- boto3 >= 1.26.0
- polars >= 0.18.0
- pandas >= 1.5.0

## AWS Configuration

Make sure your AWS credentials are configured either through:
- AWS CLI (`aws configure`)
- Environment variables (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`)
- IAM roles (when running on EC2)

Required permissions:
- S3: `s3:GetObject`, `s3:PutObject`, `s3:ListBucket`, `s3:DeleteObject`
- Athena: `athena:StartQueryExecution`, `athena:GetQueryExecution`

## Changelog

### v0.3.0 (Latest)
- **New**: Added `query()` and `query_unload()` wrapper functions for simplified usage
- **New**: Support for both Pandas and Polars DataFrames (Pandas is default)
- **Improved**: UNLOAD queries now use Parquet + GZIP (4x performance improvement)
- **Improved**: Empty query results return empty DataFrame instead of throwing exception
- **Improved**: Query execution time now displayed in logs
- **Improved**: Automatic removal of trailing semicolons in queries
- **Improved**: Silent cleanup (removed unnecessary log messages)
- **Fixed**: UNLOAD cleanup timing issue resolved

### v0.1.2
- Initial stable release
- FileHandler for S3 operations
- QueryManager for Athena queries

## License

MIT License