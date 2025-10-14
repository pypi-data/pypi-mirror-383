# -*- coding: utf-8 -*-
import polars as pl

"""
Utility functions for processing RapidPro API.
"""
def anonymize_uuid(contact_uuid):
    """
    Contact uid 12341234--1234-1234-123412341234 has no URN.
    Anonymize a UUID by replacing the last 8 characters with 'XXXXXX'.
    
    Args:
        contact_uuid (str): The UUID to anonymize.
        
    Returns:
        str: The anonymized UUID.
    """
    if not isinstance(contact_uuid, str):
        return None

    if len(contact_uuid) < 12:
        return "************"

    annon = contact_uuid[:-12] + "************"
    annon = "********" + annon[8:]
    return annon


def flatten_pl_struct(df: pl.DataFrame, struct_col: str, struct_fields: list = None, prefix: str = None, prefix_separator: str = "_", remove_struct: bool = False ) -> pl.DataFrame:
    """
    Flatten a Polars struct column into individual columns and adds them to the DataFrame.
    Args:
        df (pl.DataFrame): The Polars DataFrame containing the struct column.
        struct_col (str): The name of the struct column to flatten.
        struct_fields (list, optional): A list of field names to flatten from the struct column. If None, all fields will be flattened.
        prefix (str, optional): A prefix to add to the new column names. If None, the struct column name will be used as the prefix.
        prefix_separator (str, optional): The separator to use between the prefix and the field names. Default is "_".
        remove_struct (bool, optional): If True, the original struct column will be removed from the DataFrame after flattening.
    Returns:
        pl.DataFrame: The DataFrame with the struct column flattened into individual columns.
    """
    if struct_col not in df.columns:
        return df

    # Get the fields of the struct column
    if struct_fields is None:
        # If struct_fields is not provided, get the fields from the DataFrame
        struct_fields = df[struct_col].struct.fields
    else:
        # If struct_fields is provided, use it directly
        if not isinstance(struct_fields, list):
            raise ValueError("struct_fields must be a list of field names.")
        # Now ensure that only the valid fields are used
        struct_fields = [field for field in struct_fields if field in df[struct_col].struct.fields]

    if prefix is None:
        prefix = struct_col

    # Create new columns for each field in the struct
    new_columns = [
        pl.col(struct_col).struct.field(field).alias(f"{prefix}{prefix_separator}{field}")
            for field in struct_fields
    ]

    # Add the new columns to the DataFrame
    df = df.with_columns(new_columns)

    if remove_struct:
        # Remove the original struct column if specified
        df = df.drop(struct_col)

    return df
