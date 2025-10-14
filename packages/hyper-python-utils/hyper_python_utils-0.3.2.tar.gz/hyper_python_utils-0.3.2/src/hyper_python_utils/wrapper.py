import uuid
import polars as pl
import pandas as pd
from typing import Literal, Union
from .query_manager import QueryManager


# Global QueryManager instance with fixed configuration
_query_manager = QueryManager(
    bucket="athena-query-results-for-hyper",
    result_prefix="query_results/",
    auto_cleanup=True
)


def query(database: str, query: str, option: Literal["pandas", "polars"] = "pandas") -> Union[pd.DataFrame, pl.DataFrame]:
    """
    Execute a simple Athena query and return results as a DataFrame.

    Args:
        database: Athena database name
        query: SQL query string (e.g., "SELECT * FROM my_table LIMIT 100")
        option: Output format - "pandas" (default) or "polars"

    Returns:
        pd.DataFrame or pl.DataFrame: Query results. Returns empty DataFrame if no results.

    Example:
        >>> import hyper_python_utils as hp
        >>> # Returns pandas DataFrame (default)
        >>> df = hp.query(database="my_database", query="SELECT * FROM my_table LIMIT 100")
        >>> # Returns polars DataFrame
        >>> df = hp.query(database="my_database", query="SELECT * FROM my_table LIMIT 100", option="polars")
    """
    return _query_manager.query(query=query, database=database, output_format=option)


def query_unload(database: str, query: str, option: Literal["pandas", "polars"] = "pandas") -> Union[pd.DataFrame, pl.DataFrame]:
    """
    Execute an Athena UNLOAD query and return results as a DataFrame.
    The UNLOAD operation writes results to S3 in Parquet format, then reads them back.

    Args:
        database: Athena database name
        query: SQL SELECT query (only the inner SELECT part, without UNLOAD TO syntax)
               Example: "SELECT * FROM my_table WHERE date > '2024-01-01'"
        option: Output format - "pandas" (default) or "polars"

    Returns:
        pd.DataFrame or pl.DataFrame: Query results loaded from the unloaded Parquet files

    Example:
        >>> import hyper_python_utils as hp
        >>> # Returns pandas DataFrame (default)
        >>> df = hp.query_unload(
        ...     database="my_database",
        ...     query="SELECT * FROM large_table WHERE date > '2024-01-01'"
        ... )
        >>> # Returns polars DataFrame
        >>> df = hp.query_unload(
        ...     database="my_database",
        ...     query="SELECT * FROM large_table WHERE date > '2024-01-01'",
        ...     option="polars"
        ... )

    Note:
        - The function automatically wraps your query with UNLOAD syntax
        - Unloads to: s3://athena-query-results-for-hyper/query_results_for_unload/{uuid}/
        - Uses Parquet format with GZIP compression (best performance and compression ratio)
        - Files are kept in S3 (not automatically deleted)
    """
    # Generate unique prefix for this UNLOAD operation
    unique_id = str(uuid.uuid4())[:8]
    unload_prefix = f"query_results_for_unload/{unique_id}/"
    s3_location = f"s3://athena-query-results-for-hyper/{unload_prefix}"

    # Construct UNLOAD query with Parquet + GZIP (best performance)
    unload_query = f"""
    UNLOAD ({query})
    TO '{s3_location}'
    WITH (format='PARQUET', compression='GZIP')
    """

    # Execute UNLOAD and get file locations
    unloaded_files = _query_manager.unload(query=unload_query, database=database)

    if not unloaded_files:
        print("[UNLOAD] No files were created (empty result set)")
        return pd.DataFrame() if option == "pandas" else pl.DataFrame()

    print(f"[UNLOAD] Created {len(unloaded_files)} file(s) at {s3_location}")

    # Debug: Print file list to help diagnose issues
    for file_path in unloaded_files:
        print(f"[UNLOAD] Reading file: {file_path}")

    # Read all unloaded Parquet files into a single DataFrame
    try:
        # Read with polars first (faster for large files)
        df_polars = pl.read_parquet(unloaded_files)
        print(f"[UNLOAD] Loaded {df_polars.height} rows from Parquet files")

        # Convert to pandas if requested
        df = df_polars.to_pandas() if option == "pandas" else df_polars

        return df
    except Exception as e:
        raise Exception(f"Failed to read unloaded Parquet files: {str(e)}")
