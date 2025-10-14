import logging
from datetime import datetime, timezone
import polars as pl
from deltalake import DeltaTable
from rapidpro_api.contact_processors_pl import process_contacts_pl
from rapidpro_api.run_processors_pl import process_runs_pl
from rapidpro_api.contact_processors import parse_born, parse_gender, get_age_group


def get_last_processed_date(workspace, delta_path, column_name: str = 'modified_on'):
    """ Get the last processed date for a workspace from the Delta Lake table.
    If the table does not exist or the workspace is not found, return None.
    Args:
        workspace: The workspace object.
        delta_path: The path to the Delta Lake table.
    Returns: the last processed date as a datetime.date object. 
    Example:
        >>> get_last_processed_date(workspace, delta_path)
        datetime.date(2023, 12, 31)
    """
    
    logging.info("%s: Getting last processed date Delta table %s (col:%s)", workspace.code, delta_path, column_name)
    
    # Using polars read the delta table. In this case only the workspace.code and the last date in  modified_on column 
    try:
        dt = DeltaTable(delta_path)  # Validate the table is readable
        # check if the column_name exists in the delta table
        #logging.info("%s: Delta table %s schema: %s, %s", workspace.code, delta_path, dt.schema(), dt.schema().fields)
        column_exists = column_name in [field.name for field in dt.schema().fields]
        if not column_exists:
            raise ValueError(f"Column {column_name} does not exist in delta table {delta_path}")
        filtered_data = (
            pl.scan_delta(dt)
            .filter(pl.col("workspace_code") == workspace.code)
            .select(
                pl.col(column_name).max().alias("last_modified_on")
            )
            .collect()
        )
        if filtered_data.is_empty():
            logging.info("%s: No data found in delta table %s.", workspace.code, delta_path)
            return None
        
        last_modified_on = filtered_data["last_modified_on"][0]
        if last_modified_on is None:
            logging.info("%s: No last modified date found in delta table %s.", workspace.code, delta_path)
            return None
        
        logging.info("%s: * ** *** Last modified_on is %s (%s)", workspace.code, last_modified_on, type(last_modified_on))

        if isinstance(last_modified_on, datetime):
            # ensure last modified on is  in UTZ and the time is 23:59:59
            last_modified_on = last_modified_on.replace(hour=23, minute=59, second=59, microsecond=999999)
            # if last_modified_on is timezone naive, set it to UTC
            last_modified_on = last_modified_on.replace(tzinfo=timezone.utc)
            return last_modified_on
        if isinstance(last_modified_on, str):
            # last_modified_on is a string in the format "2014-10-03T01:42:31.253139Z". We need to convert it to a date object
            # Convert the string to isoformat and then to a date object
            return datetime.fromisoformat(last_modified_on.replace('Z', '+23:59:59'))
        raise ValueError(f"Unexpected type for last_modified_on: {type(last_modified_on)}")
    # if there is any issue then 
    except ValueError as ve:
        logging.error("%s: ValueError when accessing delta table %s: %s", workspace.code, delta_path, ve)
        raise ve
    except Exception as e:
        logging.info("%s: Delta table %s does not exist or is not readable: %s (%s)", workspace.code, delta_path, e, type(e))
        return None 



def get_metadata_field(metadata, field_name, default_value: str=None) -> str:
    """
    Get a field from the metadata dictionary, returning a default value if the field is not present or not a string.
    As convention field_name are expected to end with _field, e.g. state_field, district_field, ward_field, registration_date_field, born_field

    Args:
        metadata (dict): The metadata dictionary.
        field_name (str): The name of the field to retrieve.
        default_value (str): The default value to return if the field is not present or not a string. If None, will return the field_name without _field suffix if it ends with _field or the field_name as is.
    Returns:
        str: The value of the field from the metadata, or the default value.
    Example:
        metadata = {
            "state_field": "state",
            "gender": "",
            "born_": "born"
        }
        state_field = get_metadata_field(metadata, "state_field")
        # "state"  # no default, but ends with _field, so returns "state"
        district_field = get_metadata_field(metadata, "district_field", "distrito")
        # "distrito" # default used.
        ward_field = get_metadata_field(metadata, "ward")
        # "ward" - no default, so returns the field_name as is
    """
    value = metadata.get(field_name, default_value) if metadata else None
    if not value or not isinstance(value, str):
        if default_value is None:
            # use the field_name without _field suffix.
            if field_name.endswith('_field'):
                return field_name[:-6]
        return default_value
    return value
   
 
def remove_field_columns(df: pl.DataFrame) -> pl.DataFrame:
    """
    Remove columns that end with '_field' from the DataFrame.
    Under the u-report use case they are metadata cols, generally, 
    not useful for analysis.
    See workspaces module for more details.
    Args:
        df (pl.DataFrame): The input Polars DataFrame.
    Returns:
        pl.DataFrame: The DataFrame with '*_field' columns removed.
    """
    cols_to_drop = [col for col in df.columns if col.endswith('_field')]
    if cols_to_drop:
        df = df.drop(*cols_to_drop)
    return df

def remove_label_columns(df: pl.DataFrame) -> pl.DataFrame:
    """
    Remove columns that end with '_label' from the DataFrame.
    In U-Report use case *_label columns come from metadata and they're not useful for analysis.
    
    Args:
        df (pl.DataFrame): The input Polars DataFrame.
    Returns:
        pl.DataFrame: The DataFrame with '*_label' columns removed.
    """
    cols_to_drop = [col for col in df.columns if col.endswith('_label')]
    if cols_to_drop:
        df = df.drop(*cols_to_drop)
    return df

  

def process_ureport_contacts_pl(contacts, fields: list = None, groups:list = None, metadata:dict = None):
    """
    Process a batch of contacts that follows the ureport format provided by the RapidPro API. 
    Returns a polars DataFrame with the relevant information.
    This function extends the functionality of `process_contacts_pl` to include ureport-specific fields and processing.
    On top of `process_contact_pl`:
     - Includes parsed_gender and parsed_born fields.
     - Gets the "age_group" using the get_age_group function (based on the parsed_born).
     - Forces the inclusion of the "registration_date", "state", "district", and "ward", country fields based on the metadata provided (registration_field, state_field, district_field, ward_field...).
     - Removes some fields that are not relevant for the ureport dataset (fields, groups, flow, urns, name, created_on, last_seen_on)
     - Removes any columns that end with _field or _label
    Args:
        contacts (list): A contact list as returned from the RapidPro API. 
        fields (list): A list of fields that will be extracted from the fields object of the contact as attributes of the processed contact.
        groups (list): A list of groups that will be extracted from the groups object of the contact as attributes of the processed contact. Assumes validated group names.
        metadata (dict): A dictionary of custom columns to include in the output. Metadata you can add to the contact.
    Returns:
        pl.DataFrame: A polars dataframe with the relevant information from the contact.
    Example:
        processed_contact = process_ureport_contact(contact, 
                 fields=["field1", "field2"], 
                 groups=["group1", "group2"], 
                 metadata={"metadata_col1": "value1"})
        
        # processed_contact will be a dictionary with the relevant information from the contact.
        print(processed_contact)
        # {
        #   "name": "John Doe",
        #   "uuid": "12345678-1234-1234-1234-123456789012",
        #   "status": "active",
        #   "modified_on": "2023-01-01T00:00:00Z",
        #   "created_on_year": "2023",
        #   "created_on_month": "2023-01",
        #   "created_on_day": "2023-01-01",
        #   "last_seen_on_year": "2023",
        #   "last_seen_on_month": "2023-01",
        #   "last_seen_on_day": "2023-01-01",
        #   "metadata_col1": "value1",
        #   "field1": "value1",
        #   "field2": "value2",
        #   "age_group": "0-14",
        #.  "registration_date": "2023-01-01",
        #   "country": "Country A",
        #.  "state": "State A",
        #   "district": "District A",
        #   "ward": "Ward A",
        #   "born": "2000",
        #   "gender" : "Female",
        #   "group1": True,
        #   "group2": False,
        #.  "is_ureporter": True
        # }
    
    """
    
    # Get the metadata fields with defaults if not set
    registration_field = get_metadata_field(metadata, 'registration_date_field', 'registration_date')
    state_field = get_metadata_field(metadata, 'state_field', 'state')
    district_field = get_metadata_field(metadata, 'district_field', 'district')
    ward_field = get_metadata_field(metadata, 'ward_field', 'ward')
    born_field = get_metadata_field(metadata, 'born_field', 'born')
    gender_field = get_metadata_field(metadata, 'gender_field', 'gender')
    country_field = get_metadata_field(metadata, 'country_field', 'country')
    
    # get the ureporters_group
    ureporters_group = get_metadata_field(metadata, 'ureporters_group', 'U-Reporter')

    # merge fields with the ureport specific fields
    fields = fields or []
    fields.extend([registration_field, state_field, district_field, ward_field, born_field, gender_field])
    logging.debug("Fields after merging with ureport specific fields: %s", fields)

    # merge groups with the ureport specific fields
    groups = groups or []
    groups.extend([ureporters_group])

    # Baseline processing using the existing process_contact_pl function
    df = process_contacts_pl(contacts, fields=fields, groups=groups, metadata=metadata)

    if df.is_empty():
        logging.debug("No contacts to process, returning empty DataFrame.")
        return df
    # Standardize the column names for ureport specific fields
    df = df.rename({
        registration_field: "registration_date",
        state_field: "state",
        district_field: "district",
        ward_field: "ward",
        born_field: "born",
        gender_field: "gender",
        ureporters_group: "is_ureporter",
        country_field: "country"
    })
    logging.debug("Columns after process_contact_pl and renaming: %s", df.columns)

     # cast any of the columns that are null to utf8
    df = df.with_columns(
        pl.col('registration_date').cast(pl.Utf8),
        pl.col('state').cast(pl.Utf8),
        pl.col('district').cast(pl.Utf8),
        pl.col('ward').cast(pl.Utf8),
        pl.col('gender').cast(pl.Utf8),
        pl.col('born').cast(pl.Utf8),
        pl.col('is_ureporter').cast(pl.Boolean)
    )
    
    # Rename original columns to _raw versions
    df = df.rename({
        "born": "born_raw",
        "gender": "gender_raw"
    })
    # Apply parse_gender and parse_born to the DataFrame columns
    df = df.with_columns([
      pl.col("gender_raw").map_elements(parse_gender, return_dtype=pl.Utf8).alias("gender"),
      pl.col("born_raw").map_elements(parse_born, return_dtype=pl.Int64).alias("born"),
    ])
    # Add age_group column based on the parsed born
    df = df.with_columns([
      pl.col("born").map_elements(get_age_group, return_dtype=pl.Utf8).alias("age_group")
    ])
     # remove the fields and groups from the processed_contact
    # check if language is null 
    if 'language' in df.columns:
        df = df.with_columns(
            pl.col('language').fill_null('None').cast(pl.Utf8).alias('language')
        )
        # Remove anything that ends with _field or _label
    df = remove_field_columns(df)
    df = remove_label_columns(df)
    # remove some other columns that are not relevant for the ureport dataset
    pop = ['fields',
           'groups', 
           'flow', 
           'urns', 
           'name', 
           'created_on', 
           'last_seen_on'
    ]
    # check if the columns are in the DataFrame before dropping them
    pop = [col for col in pop if col in df.columns]
    df = df.drop(*pop)
    return df


def process_ureport_runs_pl(run_batch, metadata: dict = None):
    """
    Process a batch of runs that follows the ureport format provided by the RapidPro API.
    Returns a polars DataFrame with the relevant information.
    
    Args:
        run_batch (list): A list of runs as returned from the RapidPro API.
        metadata (dict): Optional metadata columns to add to each run.
        
    Returns:
        pl.DataFrame: A Polars DataFrame of processed runs.
    """
    if not run_batch or not isinstance(run_batch, list) or len(run_batch) == 0:
        return pl.DataFrame()

    # call process_runs_pl 
    df = process_runs_pl(run_batch, metadata=metadata)

    # Fill with 'None' string if any of the columns are null
    
    if df.is_empty():
        return df
    
    # Define arrays for column types
    utf8_columns = ['key', 'name', 'value', 'category', 'flow_uuid', 'flow_name', 'contact_uuid', 'exited_on', 'exit_type']
    bool_columns = ['responded']

    # Check if columns exist before applying the cast
    for col in utf8_columns:
        if col in df.columns:
            df = df.with_columns(pl.col(col).cast(pl.Utf8))

    for col in bool_columns:
        if col in df.columns:
            df = df.with_columns(pl.col(col).cast(pl.Boolean))
    
    remove_field_columns(df)
    remove_label_columns(df)
    # if not empty pop some columns that are not relevant for the ureport dataset
    pop = ["contact",
           "contact_name",
           "flow",
           "path", 
           "start",
           "ureporters_group"
           ]
    pop = [col for col in pop if col in df.columns]
    df = df.drop(*pop)
    return df