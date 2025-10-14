import polars as pl
import logging
from datetime import datetime

def process_contacts_pl(contacts: list, fields: list = None, groups: list = None, metadata: dict = None) -> pl.DataFrame:
    """
    Process contacts from RapidPro API and return a DataFrame with the relevant information.

    Args:
        contacts_df (list): A list of contacts as returned from the RapidPro API.
        fields (list): A list of fields to extract from the fields object of each contact.
        groups (list): A list of groups to check membership for each contact.
        metadata (dict): A dictionary of custom columns to include in the output.

    Returns:
        pl.DataFrame: A DataFrame with the processed contacts information.
    """
    if not isinstance(contacts, list):
        logging.error("Expected contacts to be a list, got %s", type(contacts))
        raise ValueError("contacts must be a list")

    # Create a copy to avoid modifying the original
    processed_df = pl.DataFrame(contacts, infer_schema_length=None)

    if processed_df.is_empty():
        logging.warning("Contacts DataFrame is empty")
        return pl.DataFrame()

    # Ensure required columns are present
    
    # Process created_on date components
    if "created_on" in processed_df.columns:
        processed_df = processed_df.with_columns([
            pl.col("created_on").str.to_datetime().dt.year().cast(pl.Utf8).alias("created_on_year"),
            pl.col("created_on").str.to_datetime().dt.strftime("%Y-%m").alias("created_on_month"),
            pl.col("created_on").str.to_datetime().dt.strftime("%Y-%m-%d").alias("created_on_day")
        ])
    
    # Handle last_seen_on (use modified_on if last_seen_on is null)
    if "last_seen_on" in processed_df.columns:
        if "modified_on" in processed_df.columns:
            processed_df = processed_df.with_columns([
                pl.when(pl.col("last_seen_on").is_null())
                .then(pl.col("modified_on"))
                .otherwise(pl.col("last_seen_on"))
                .alias("last_seen_on")
            ])
            # Process last_seen_on date components
            processed_df = processed_df.with_columns([
                pl.col("last_seen_on").str.to_datetime().dt.year().cast(pl.Utf8).alias("last_seen_on_year"),
                pl.col("last_seen_on").str.to_datetime().dt.strftime("%Y-%m").alias("last_seen_on_month"),
                pl.col("last_seen_on").str.to_datetime().dt.strftime("%Y-%m-%d").alias("last_seen_on_day")
            ])
    
    # Add metadata columns
    if metadata and isinstance(metadata, dict):
        for key, value in metadata.items():
            processed_df = processed_df.with_columns(pl.lit(value).alias(key))
    
    # Ensure required columns are present
    required_columns = ["fields", "groups", "urns"]
    for col in required_columns:
        if col not in processed_df.columns:
            logging.warning(f"Column '{col}' not found in contacts DataFrame, adding as empty column")
            processed_df = processed_df.with_columns(pl.lit(None).alias(col))
    # Ensure fields, groups, and urns are present and initialized
    processed_df = processed_df.with_columns([
        pl.when(pl.col("fields").is_null()).then(pl.lit({})).otherwise(pl.col("fields")).alias("fields"),
        pl.when(pl.col("groups").is_null()).then(pl.lit([])).otherwise(pl.col("groups")).alias("groups"),
        pl.when(pl.col("urns").is_null()).then(pl.lit([])).otherwise(pl.col("urns")).alias("urns")
    ])
    # Ensure the columns are of the correct type

    # Extract fields from the nested "fields" column
    if fields and "fields" in processed_df.columns:
        for field_name in fields:
            processed_df = processed_df.with_columns([
                pl.col("fields").map_elements(lambda x: x.get(field_name, None) if isinstance(x, dict) else None,
                                              return_dtype=pl.Utf8)
                .alias(field_name)
            ])

    # Extract group membership
    if groups and "groups" in processed_df.columns:
        for group_name in groups:
            processed_df = processed_df.with_columns([
                pl.col("groups").map_elements(
                    lambda groups_list: bool(any(
                        isinstance(g, dict) and g.get("name") == group_name
                        for g in (groups_list if not None else [])
                    )),
                    return_dtype=pl.Boolean
                ).alias(group_name)
            ])
        
    # Extract URN type
    if "urns" in processed_df.columns:
        processed_df = processed_df.with_columns([
            pl.col("urns").map_elements(
                lambda urns: urns[0].split(":")[0] if len(urns) > 0 
                and isinstance(urns[0], str) and ":" in urns[0] else None,
                return_dtype=pl.Utf8
            ).alias("urn_type")
        ])
    
    return processed_df