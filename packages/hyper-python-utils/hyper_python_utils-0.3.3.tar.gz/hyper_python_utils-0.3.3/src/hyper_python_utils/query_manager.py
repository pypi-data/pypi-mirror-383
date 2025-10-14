import boto3
import time
import io
import re
import polars as pl
import pandas as pd
from typing import Literal, Union


class AthenaQueryError(Exception):
    pass


class EmptyResultError(Exception):
    pass


class QueryManager:
    def __init__(self, bucket: str, result_prefix: str = 'athena/query_results/', auto_cleanup: bool = True):
        self._bucket = bucket
        self._result_prefix = result_prefix
        self._s3_output = f's3://{bucket}/{result_prefix}'
        self._auto_cleanup = auto_cleanup
        self.athena = boto3.client('athena', region_name='ap-northeast-2')
        self.s3 = boto3.client('s3', region_name='ap-northeast-2')

    def execute(self, query: str, database: str) -> str:
        # Remove trailing semicolon if present
        query = query.strip().rstrip(';')

        response = self.athena.start_query_execution(
            QueryString=query,
            QueryExecutionContext={'Database': database},
            ResultConfiguration={'OutputLocation': self._s3_output}
        )
        return response['QueryExecutionId']

    def wait_for_completion(self, query_id: str, interval: int = 5, timeout: int = 300) -> str:
        start_time = time.time()
        while True:
            response = self.athena.get_query_execution(QueryExecutionId=query_id)
            status = response['QueryExecution']['Status']['State']
            if status == 'SUCCEEDED':
                elapsed_time = time.time() - start_time
                print(f"[Athena] Query succeeded ({elapsed_time:.2f}s)")
                break
            elif status in ['FAILED', 'CANCELLED']:
                reason = response['QueryExecution']['Status'].get('StateChangeReason', 'Unknown')
                raise AthenaQueryError(f"Query {status}: {reason}")
            elif (time.time() - start_time) > timeout:
                raise TimeoutError("Query timed out")
            time.sleep(interval)
        return response['QueryExecution']['ResultConfiguration']['OutputLocation']

    def get_result(self, query_id: str, auto_cleanup: bool = None, output_format: Literal["polars", "pandas"] = "polars") -> Union[pl.DataFrame, pd.DataFrame]:
        response = self.athena.get_query_execution(QueryExecutionId=query_id)
        result_location = response['QueryExecution']['ResultConfiguration']['OutputLocation']
        
        # Extract bucket and key from S3 URL
        match = re.match(r's3://([^/]+)/(.+)', result_location)
        if not match:
            raise ValueError(f"Invalid S3 result location: {result_location}")
        
        bucket, key = match.groups()
        
        # Download CSV result from S3
        try:
            obj = self.s3.get_object(Bucket=bucket, Key=key)
            csv_content = obj['Body'].read().decode('utf-8')
            
            # Read CSV with polars first
            df_polars = pl.read_csv(io.StringIO(csv_content))

            # Return empty DataFrame if no results (no exception)
            if df_polars.height == 0:
                print("[Athena] Query returned no results (empty DataFrame)")
                result_df = pd.DataFrame() if output_format == "pandas" else df_polars
            else:
                # Convert to pandas if requested
                result_df = df_polars.to_pandas() if output_format == "pandas" else df_polars

            # Auto cleanup if enabled (silent cleanup, no logs)
            cleanup_enabled = auto_cleanup if auto_cleanup is not None else self._auto_cleanup
            if cleanup_enabled:
                try:
                    self.s3.delete_object(Bucket=bucket, Key=key)
                    # Also delete metadata file if exists
                    metadata_key = key + '.metadata'
                    try:
                        self.s3.delete_object(Bucket=bucket, Key=metadata_key)
                    except:
                        pass  # Metadata file might not exist
                except Exception as cleanup_error:
                    pass  # Silent cleanup failure

            return result_df
        except Exception as e:
            raise AthenaQueryError(f"Failed to read query result: {str(e)}")

    def query(self, query: str, database: str, auto_cleanup: bool = None, output_format: Literal["polars", "pandas"] = "polars") -> Union[pl.DataFrame, pd.DataFrame]:
        query_id = self.execute(query, database)
        self.wait_for_completion(query_id)
        return self.get_result(query_id, auto_cleanup=auto_cleanup, output_format=output_format)

    def unload(self, query: str, database: str, unload_location: str = None) -> list[str]:
        query_id = self.execute(query, database)
        result_location = self.wait_for_completion(query_id)

        # Use provided unload_location or extract from result_location
        if unload_location:
            search_location = unload_location
        else:
            # Extract the base path for unloaded files (legacy behavior)
            match = re.match(r's3://([^/]+)/(.+)', result_location)
            if not match:
                raise ValueError(f"Invalid S3 result location: {result_location}")
            bucket, key_prefix = match.groups()
            base_prefix = key_prefix.rsplit('/', 1)[0] + '/'
            search_location = f's3://{bucket}/{base_prefix}'

        # Extract bucket and prefix from search location
        match = re.match(r's3://([^/]+)/(.+)', search_location.rstrip('/'))
        if not match:
            raise ValueError(f"Invalid S3 location: {search_location}")

        bucket, base_prefix = match.groups()
        if not base_prefix.endswith('/'):
            base_prefix += '/'

        print(f"[UNLOAD] Searching for files in: s3://{bucket}/{base_prefix}")

        paginator = self.s3.get_paginator('list_objects_v2')
        page_iterator = paginator.paginate(Bucket=bucket, Prefix=base_prefix)
        
        unloaded_files = []
        for page in page_iterator:
            for obj in page.get('Contents', []):
                key = obj['Key']
                # Only include Parquet files (with or without .gz compression)
                if key.endswith('.parquet') or key.endswith('.parquet.gz'):
                    unloaded_files.append(f's3://{bucket}/{key}')

        return unloaded_files

    def delete_query_results_by_prefix(self, s3_prefix_url: str):
        match = re.match(r's3://([^/]+)/(.+)', s3_prefix_url.rstrip('/'))
        if not match:
            raise ValueError("Invalid S3 URL format")

        bucket, prefix = match.groups()

        paginator = self.s3.get_paginator("list_objects_v2")
        page_iterator = paginator.paginate(Bucket=bucket, Prefix=prefix)

        deleted_any = False
        for page in page_iterator:
            for obj in page.get("Contents", []):
                key = obj["Key"]
                self.s3.delete_object(Bucket=bucket, Key=key)
                deleted_any = True

        if not deleted_any:
            print(f"[S3] No files found under prefix: {s3_prefix_url}")