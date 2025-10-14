import polars as pl
from rapidpro_api.utils import flatten_pl_struct
from rapidpro_api.contact_processors import get_contact_urn_type
   


def process_runs_pl(run_batch: list, metadata: dict = None) -> pl.DataFrame:
    """
    Process a batch of runs using native Polars operations.
    Args:
        run_batch (list): A list of run dicts as returned by the RapidPro API.
        metadata (dict): Optional metadata columns to add to each run.
    Returns:
        pl.DataFrame: A Polars DataFrame of processed runs.
        
    """
    if not run_batch:
        return pl.DataFrame()

    # First of all, convert the values into a list of dicts:
    for run in run_batch:
        # If values is empty, we create a dummy entry to maintain structure
        values = run.get("values", {})

        if not values:
            run["run_responses"] = 0
            run["values"] = [{ 
                    "key": "empty_run",
                    "name": "**empty_run**",
                    "value": "",
                    "category": "",
                    "node": "",
                    "time": ""
            }
            ]
        # Convert values to a list of dicts if it's not already
        elif isinstance(values, dict):
            run["run_responses"] = len(values)
            value_array = []
            for key, value in values.items():
                value["key"] = key  # Add the key to the value dict
                value_array.append(value)
            run["values"] = value_array
    # Convert to Polars DataFrame
    df = pl.DataFrame(run_batch, infer_schema_length=None)
     # Apply flatten_pl_struct to flow and contact columns
    df = flatten_pl_struct(df, "flow")
    df = flatten_pl_struct(df, "contact")

    if "contact_urn" in df.columns:
        df = df.with_columns([
            pl.col("contact_urn").map_elements(
                lambda x: get_contact_urn_type(x) if x else None,
                return_dtype=pl.Utf8
            ).alias("urn_type")
        ])
    # Process created_on date components

    if "created_on" in df.columns:
        df = df.with_columns([
            pl.col("created_on").str.to_datetime().dt.year().cast(pl.Utf8).alias("created_on_year"),
            pl.col("created_on").str.to_datetime().dt.strftime("%Y-%m").alias("created_on_month"),
            pl.col("created_on").str.to_datetime().dt.strftime("%Y-%m-%d").alias("created_on_day")
        ])
    
    # exited_on can be null in all the cols which makes it a bit tricker to parse.
    if "exited_on" in df.columns:
        # ensure exited_on is string and not null
        df = df.with_columns(pl.col("exited_on").fill_null("").cast(pl.Utf8))
        # create date components, allowing for empty strings
        df = df.with_columns([
            pl.col("exited_on").str.to_datetime(format="%Y-%m-%dT%H:%M:%S%.fZ", strict=False).dt.year().cast(pl.Utf8).alias("exited_on_year"),
            pl.col("exited_on").str.to_datetime(format="%Y-%m-%dT%H:%M:%S%.fZ", strict=False).dt.strftime("%Y-%m").alias("exited_on_month"),
            pl.col("exited_on").str.to_datetime(format="%Y-%m-%dT%H:%M:%S%.fZ", strict=False).dt.strftime("%Y-%m-%d").alias("exited_on_day")
        ])

    
    # Explode and normalize the values column
    if "values" in df.columns:
        df = df.explode("values").unnest("values")
    
    # Add metadata columns if provided
    if metadata and isinstance(metadata, dict):
        for k, v in metadata.items():
            df = df.with_columns(pl.lit(v).alias(k))
  
    return df