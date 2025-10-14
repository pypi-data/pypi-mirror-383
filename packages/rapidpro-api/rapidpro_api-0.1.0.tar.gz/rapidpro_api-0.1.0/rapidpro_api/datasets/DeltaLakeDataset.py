from deltalake import DeltaTable, write_deltalake
import polars as pl
from typing import Optional, Dict, Any, List, Union
import logging

from rapidpro_api.workspaces import Workspace

class DeltaLakeDataset:
  """Delta Lake manager with partition support.
  This class provides methods to read and write Delta tables with partitioning support.
  """
  def __init__(
    self, 
    name: str,
    table_name: str,
    workspace: Workspace,
    base_folder: str = "./datasets",
    partition_cols: Optional[List[str]] = None,
    storage_options: Optional[Dict[str, Any]] = None

  ):
    """
    Initialize Delta Lake manager with partition support.
    The resulting delta table path will be:
    `<base_folder>/<name>/<table_name>`
    Example for the dataset named contacts and table_name processed:
    - Local: `./datasets/contacts/processed`
    - S3: `s3://my-bucket/contacts/processed`

    Args:
      name: Name of the dataset (contacts, flows, etc.)
      table_name: Name of the Delta table within the dataset (e.g., "processed", "aggregated")
      workspace: Workspace object (e.g., RapidPro workspace)
      base_folder: Path to Delta table. Defaults to "./datasets".
        Examples:
        - Local: "/tmp/my_table"
        - S3: "s3://my-bucket/my-table"
        - Azure: "az://container/my-table"
        - Google Cloud: "gs://bucket/my-table"
      partition_cols: List of column names to partition by. If None, defaults to workspace code.
        Example: ["workspace_code", "created_on_year", "created_on_month"]
      storage_options: Additional storage options (optional, overrides env vars)
        Example:
        - For S3: {"key": "my-access
        - For Azure: {"az_storage_account_name": "myaccount", "az_storage_account_key": "mykey"}
        - For Google Cloud: {"gcp_project": "my-project", "gcp_credentials": "/path/to/credentials.json"}
    """
    self.name = name
    self.workspace = workspace
    self.table_name = table_name
    self.base_folder = base_folder
    self.table_path = f"{base_folder}/{name}/{table_name}"
    self.partition_cols = partition_cols or [workspace.code]
    self.storage_options = storage_options
    self.table = None
    
     
  def get_table(self) -> Optional[DeltaTable]:
    """
    Get whole dataset Delta table
    Returns:
      DeltaTable: Delta table object or empty if table doesn't exist
    Raises:
      Exception: If table cannot be loaded
    """
    if self.table is None:
      try:
        if self.storage_options:
          self.table = DeltaTable(self.table_path, storage_options=self.storage_options)
        else:
          self.table = DeltaTable(self.table_path)
      except Exception as e:
        logging.error(f"Table {self.table_path} doesn't exist yet or error: {e}")
        return None
    return self.table
  
  def write_dataframe(
    self, 
    df: pl.DataFrame, 
    mode: str = "overwrite",
    partition_cols: Optional[List[str]] = None,
    predicate: str = None,
    **write_kwargs
  ):
    """
    Write DataFrame to Delta table with partition support.
    
    Args:
      df: Polars DataFrame to write
      mode: Write mode ('append', 'overwrite', 'error', 'ignore'). default is 'overwrite'.
        - 'append': Add to existing data
        - 'overwrite': Replace existing data
        - 'error': Raise error if data exists
        - 'ignore': Do nothing if data exists
      partition_cols: List of columns to partition by. If None, uses instance partition columns.
        Example: ["workspace_code", "created_on_year", "created_on_month"]
      partition_cols: Override instance partition columns
      **write_kwargs: Additional arguments for write_deltalake
    """
    partition_columns = partition_cols or self.partition_cols
    
    # Validate partition columns exist in DataFrame
    if partition_columns:
      missing_cols = [col for col in partition_columns if col not in df.columns]
      if missing_cols:
        raise ValueError(f"Partition columns {missing_cols} not found in DataFrame")
    
    # Prepare write arguments
    write_args = {
      "table_or_uri": self.table_path,
      "data": df,
      "mode": mode,
      "partition_by": partition_columns if partition_columns else None,
      "storage_options": self.storage_options,
      **write_kwargs
    }
          
    write_deltalake(**write_args)
    self.table = None  # Reset to reload
    
  def read_as_polars(
    self, 
    partition_filter: Optional[Union[List[tuple], Dict[str, Any]]] = None,
    columns: Optional[List[str]] = None
  ) -> pl.DataFrame:
    """
    Read Delta table as Polars DataFrame with partition filtering.

    Args:
      partition_filter: Filter partitions using various formats:
        - List of tuples: [("year", "=", "2023"), ("month", "in", ["01", "02"])]
        - Dict: {"year": "2023", "month": ["01", "02"]}
      columns: List of columns to read (None for all)

    Returns:
      pl.DataFrame: Filtered data
    """
    table = self.get_table()
    if not table:
      return pl.DataFrame()

    try:
      # Prepare filters
      filters = None
      if partition_filter:
        if isinstance(partition_filter, dict):
          filters = []
          for col, values in partition_filter.items():
            if isinstance(values, list):
              filters.append((col, "in", values))
            else:
              filters.append((col, "=", str(values)))
        else:
          filters = partition_filter

      # Try to use Polars' native DeltaLake scan if available (polars >=0.20.16)
      try:
        scan = pl.scan_deltalake(
          self.table_path,
          storage_options=self.storage_options,
          filters=filters,
          columns=columns,
        )
        return scan.collect()
      except Exception as e:
        logging.error(f"Polars native DeltaLake scan failed: {e}")

      # Fallback to pandas
      if filters:
        pandas_df = table.to_pandas(filters=filters, columns=columns)
      else:
        pandas_df = table.to_pandas(columns=columns)
      return pl.from_pandas(pandas_df)

    except Exception as e:
      logging.error(f"Error reading partitioned data: {e}")
      return pl.DataFrame()
    
  def list_partitions(self) -> List[Dict[str, str]]:
    """
    List all partitions in the Delta table.
    
    Returns:
      List of partition dictionaries
    """
    table = self.get_table()
    if not table:
      return []
      
    try:
      # Get partition columns
      if hasattr(table, 'metadata') and table.metadata():
        partition_cols = table.metadata().partition_columns
        if not partition_cols:
          return []
          
        # Read distinct partition values
        df = pl.from_pandas(table.to_pandas(columns=partition_cols))
        partitions = df.select(partition_cols).unique().to_dicts()
        return partitions
      else:
        return []
        
    except Exception as e:
      logging.error(f"Error listing partitions: {e}")
      return []
  
  def optimize_table(self, partition_filter: Optional[Dict[str, Any]] = None):
    """
    Optimize Delta table (compact small files).
    
    Args:
      partition_filter: Only optimize specific partitions
    """
    table = self.get_table()
    if not table:
      return
      
    try:
      if partition_filter:
        # Convert filter to proper format and optimize specific partitions
        filter_expr = " AND ".join([
          f"{k} = '{v}'" if isinstance(v, str) else f"{k} = {v}"
          for k, v in partition_filter.items()
        ])
        table.optimize.compact(partition_filters=filter_expr)
      else:
        table.optimize.compact()
        
    except Exception as e:
      logging.error(f"Error optimizing table: {e}")
  
  def vacuum_table(self, retention_hours: int = 168):
    """
    Vacuum Delta table (remove old files).
    
    Args:
      retention_hours: Hours to retain (default 168 = 7 days)
    """
    table = self.get_table()
    if not table:
      return
      
    try:
      table.vacuum(retention_hours)
    except Exception as e:
      logging.error(f"Error vacuuming table: {e}")
  
  def get_partition_info(self) -> Dict[str, Any]:
    """
    Get information about table partitioning.
    
    Returns:
      Dict with partition information
    """
    table = self.get_table()
    if not table:
      return {}
      
    try:
      metadata = table.metadata()
      return {
        "partition_columns": metadata.partition_columns if metadata else [],
        "total_files": len(table.files()),
        "table_version": table.version(),
        "schema": table.schema().to_pyarrow() if hasattr(table.schema(), 'to_pyarrow') else str(table.schema())
      }
    except Exception as e:
      logging.error(f"Error getting partition info: {e}")
      return {}