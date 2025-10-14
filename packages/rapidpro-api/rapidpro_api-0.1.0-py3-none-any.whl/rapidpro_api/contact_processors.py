
import logging
import copy
from .group_processors import is_in_groups
from .utils import anonymize_uuid
from datetime import datetime
import logging
from typing import Union


def get_contact_urn_type(contact_urn: str):
    """Contact URNs come from the contacts API as a list of strings such as [facebook:***, twitter:***] etc.
    This function receives a STRING and gets rid of the `:****` and returns a string with the URN type only.
    Args:
        contact_urn (str): A string with the URN type and value, such as facebook:********.
    Returns:
        str: A string with the URN type only. If a URN does not have : or the contact_urn is not a string raises ValueError exception.
    Example:
        contact_urn = "facebook:********"
        contact_urn_type = get_contact_urn_type(contact_urn)
        # contact_urn_type will be "facebook"
    See also:
        get_contact_urn_types(contact_urns)
    """
    # Check if is not a string
    if not isinstance(contact_urn, str):
        logging.error("Contact URN is not a string")
        raise ValueError("contact_urn is not a string")

    if ":" in contact_urn:
        return contact_urn.split(":")[0]
    else:
        logging.error("Contact URN '%s' does not have a :", contact_urn)
        raise ValueError("contact_urn is not a valid URN. Expected format is urn_type:urn_value. Example: facebook:********")
        

def get_contact_urn_types(contact_urns):
    """Contact URNs come from the contacts API as a list of strings such as [facebook:***, twitter:***] etc.
    This function gets rid of the :**** and returns a list of strings with the URN type only.
    Args:
        contact_urns (list): A list of strings with the URN type and value, such as [facebook:***, twitter:***].
    Returns:
        list: A list of strings with the URN type only. If a URN does not have : it returns None for that URN. If the contact_urns is not a list raises ValueError exception.
    Example:
        contact_urns = ["facebook:********", "twitter:**********"]
        contact_urn_types = contact_urn_types(contact_urns)
        # ["facebook", "twitter"]
    """

    # Validate the contact_urns is a list
    if not isinstance(contact_urns, list):
        logging.warning("Contact URNs is not a list, returning empty list")
        return []
    
    # Validate the contact_urns is not empty
    if not contact_urns:
        logging.debug("Contact URNs is empty, returning empty list")
        return []

    return [get_contact_urn_type(urn) for urn in contact_urns]


def filter_contact_fields(all_fields, fields_to_filter):
    """Filter the fields of a contact to only include the fields in the fields_to_filter list.
    Args:
        all_fields (dict): A dictionary with all the fields of the contact.
        fields_to_filter (list): A list of fields to filter.
    Returns:
        dict: A dictionary with only the fields in the fields_to_filter list.
    If the field is not in the all_fields dictionary, it will be added with a value of None.
    If the fields_to_filter is not a list, it will return an empty dictionary.
    If the all_fields is not a dictionary, it will return an empty dictionary and log a warning.
    Example:
        all_fields = {"field1": "value1", "field2": "value2", "field3": "value3"}
        fields_to_filter = ["field1", "field3"]
        filtered_fields = filter_contact_fields(all_fields, fields_to_filter)
        # filtered_fields will be {"field1": "value1", "field3": "value3"}
    """
    if not isinstance(fields_to_filter, list):
        return {}        

    if not isinstance(all_fields, dict):
        logging.warning("All fields is not a dictionary")
        return {}

    filtered_fields = {key: all_fields.get(key, None) for key in fields_to_filter}
    return filtered_fields



def get_age_group(born: int):
    """
    Determines the age group for a given age.
    Args:
        age (str): The age as a string. It should represent a non-negative integer.
    Returns:
        str: The age group as a string. Possible values are:
            - "None" if the input is invalid, empty, or represents a negative age.
            - "0-14" for ages between 0 and 14 (inclusive).
            - "15-19" for ages between 15 and 19 (inclusive).
            - "20-24" for ages between 20 and 24 (inclusive).
            - "25-30" for ages between 25 and 30 (inclusive).
            - "31-34" for ages between 31 and 34 (inclusive).
            - "35+" for ages 35 and above.
    """
    if not born:
        return "None"
    if not isinstance(born, int):
        #logging.warning("Born year '%s' is not an integer", born)
        return "None"
    if born < 0:
        #logging.warning("Born year '%s' is negative", born)
        return "None"
    # Calculate the age based on the current year
    try:
        age = datetime.now().year - born
    except ValueError:
        logging.warning("Born year '%s' is not a valid integer", born)
        return "None"
    if age < 0:
        return "None"
    elif 0 <= age <= 14:
        return "0-14"
    elif 15 <= age <= 19:
        return "15-19"
    elif 20 <= age <= 24:
        return "20-24"
    elif 25 <= age <= 30:
        return "25-30"
    elif 31 <= age <= 34:
        return "31-34"
    else:
        return "35+"
def parse_born(born: str) -> Union[int, None]:
    """
    Parse and normalize born values from string input to integer.
    This function takes a born string and attempts to convert it to a positive integer.
    Args:
        born (str): The born string to parse.
    Returns:
        int | -1 | None: The parsed born value as a positive integer, or None if the input is empty, -1, not a valid number, or not positive.
    Example:
        parse_born("1990")
        # => 1990
    """

    if not born:
        return None
    try:
        parsed_born = int(float(born))
        if parsed_born <= 1925 or parsed_born > datetime.now().year:
            return -1
        return parsed_born
    except ValueError:
        logging.warning("parse_born: Born value '%s' is not a valid number", born)
        return -1
    except OverflowError:
        logging.warning("parse_born: Born value '%s' is too large", born)
        return -1

def parse_born_as_str(born: str):
    """
    Parse and normalize born values from string input to string.
    This function takes a born string and attempts to convert it to a positive integer and then to string.
    Args:
        born (str): The born string to parse.
    Returns:
        str: The parsed born value as a positive integer in string format, or "None" if the input is empty, None, not a valid number, or not positive.
    Example:
        parse_born_as_str("1990")
        # => "1990"
    """
    parsed_born = parse_born(born)
    return str(parsed_born) if parsed_born is not None else "None"


def parse_gender(gender: str, male_list: list[str]=None, female_list: list[str]=None, extend_default_list:bool=True) -> str:
    """
    Parse and normalize gender values from string input .
    This function takes a gender string and normalizes it to standard values:
    'Female', 'Male', 'Other', or 'None', based on common words in different languages (en, es, fr).
    Args:
        gender (str): The gender string to parse.
        male_list (list, optional): A list of male terms in various languages. Defaults to a predefined list.
        female_list (list, optional): A list of female terms in various languages. Defaults to a predefined list.
        extend_default_list (bool, optional): If True, the provided lists will be appended to the default lists. If False, the provided lists will replace the default lists. Defaults to True.
    Returns:
        str: Normalized gender value:
            - 'Female' if the input matches female terms in various languages
            - 'Male' if the input matches male terms in various languages
            - 'Other' if the input doesn't match known gender terms
            - 'None' if the input is empty or None
    Note:
        The function recognizes gender terms [boy, male, girl, female] in English, Spanish, French, Arabic, Hindi, and Portuguese.
        The function is case-insensitive and will return 'None' for empty or None inputs.
    Example:
        parse_gender("hombre")
        # => "Male"
    """
    if not gender:
        return "None"
    
    the_female_list=["female", "girl", "mujer", "f", "niña", "femme", "fille", "امرأة", "فتاة", "महिला", "लड़की", "mulher", "menina", "gore"]
    the_male_list=["male","boy", "hombre", "m", "niño", "homme", "garçon", "رجل", "ولد", "पुरुष", "लड़का", "homem", "menino", "gabo"]
    
    if extend_default_list: 
        if male_list:
            the_male_list.extend(male_list) 
        if female_list:
            the_female_list.extend(female_list)
    else:
        if male_list:
            the_male_list = male_list
        if female_list:
            the_female_list = female_list
        
    
    #logging.debug("gender", gender.lower)

    if gender.lower() in the_female_list:
        return "Female"
    elif gender.lower() in the_male_list:
        return "Male"
    else:
        return "Invalid"


def process_contact(contact, fields: list = None, groups: list = None, metadata: dict = None):
    """
    Process a contact from RapidPro API and return a dictionary with the relevant information.

    Args:
        contact (dict): A contact item returned from the RapidPro API. 
        fields (list): A list of fields that will be extracted from the fields object of the contact as attributes of the processed contact.
        groups (list): A list of groups that will be extracted from the groups object of the contact as attributes of the processed contact. Assumes validated group names.
        metadata (dict): A dictionary of custom columns to include in the output. Metadata you can add to the contact.
    Returns:
        dict: A dictionary with the relevant information from the contact.

    Example:
        processed_contact = process_api_contact(contact, 
                 fields=["field1", "field2"], 
                 groups=["group1", "group2"], 
                 metadata={"metadata_col1": "value1"})
        
        # processed_contact will be a dictionary with the relevant information from the contact.
        print(processed_contact)
        # {
        #   "name": "John Doe",
        #   "uuid": "12345678-1234-1234-1234-123456789012",
        #   "status": "active",
        #   "created_on": "2023-01-01T00:00:00Z",
        #   "created_on_year": "2023",
        #   "created_on_month": "2023-01",
        #   "created_on_day": "2023-01-01",
        #   "last_seen_on": "2023-01-01T00:00:00Z",
        #   "last_seen_on_year": "2023",
        #   "last_seen_on_month": "2023-01",
        #   "last_seen_on_day": "2023-01-01",
        #   "modified_on": "2023-01-01T00:00:00Z",
        #   "metadata_col1": "value1",
        #   "field1": "value1",
        #   "field2": "value2",
        #   "group1": True,
        #   "group2": False,
        # }
        

    """

    # Validate the contact is a dictionary
    if not isinstance(contact, dict):
        logging.error("Contact is not a dictionary")
        raise ValueError("Contact is not a dictionary")

    # Validate the contact has a uuid
    if not contact.get("uuid"):
        logging.warning("Contact does not have a uuid")

    #logging.debug("Processing contact %s", anonymize_uuid(contact.get("uuid", "")))

    processed_contact = copy.deepcopy(contact)

    # TODO - More DRY
    try:
        created_on = datetime.fromisoformat(contact["created_on"])
        processed_contact["created_on_year"] = created_on.strftime("%Y")
        # Extract the yyyy-mm and yyyy-mm-dd field from the created_on field
        processed_contact["created_on_month"] = created_on.strftime("%Y-%m")
        processed_contact["created_on_day"] = created_on.strftime("%Y-%m-%d")
    except AttributeError:
        logging.warning("Contact does not have a created_on field")
    except (ValueError, TypeError):
        logging.warning("Contact does not have a valid created_on field")
    except Exception as e:
        logging.warning("Contact does not have a valid created_on field: %s", e)
    
    try:
        # last_seen_on can be null. In that case we use modified on 
        # also we set last_seen_on == modified_on
        if contact.get("last_seen_on", None) is None:
            last_seen_on = datetime.fromisoformat(contact.get("modified_on", None))
            processed_contact['last_seen_on'] = contact.get("modified_on", None)
        else:
            last_seen_on = datetime.fromisoformat(contact["last_seen_on"])

        processed_contact["last_seen_on_year"] = last_seen_on.strftime("%Y")
        # Extract the yyyy-mm and yyyy-mm-dd field from the last_seen_on field
        processed_contact["last_seen_on_month"] = last_seen_on.strftime("%Y-%m")
        processed_contact["last_seen_on_day"] = last_seen_on.strftime("%Y-%m-%d")
    except AttributeError:
        logging.warning("Contact does not have a last_seen_on field")
    except (ValueError, TypeError):
        logging.warning("Contact does not have a valid last_seen_on field - %s", contact.get("last_seen_on", ""))
    except Exception as e:
        logging.warning("Contact does not have a valid last_seen_on field: %s", e)
   

    # Add metadata_cols, key value pairs that will be added to the processed_contact
    if metadata:
        if not isinstance(metadata, dict):
            logging.error("Metadata columns is not a dictionary")
            raise ValueError("Metadata columns is not a dictionary")
        processed_contact.update(metadata)
    
    # Add the groups to the root object    
    processed_contact.update(is_in_groups(contact.get("groups", []), groups))

    # Add the fields to the root object
    processed_contact.update(filter_contact_fields(contact.get("fields", {}), fields))

    # Add the urn type to the root object
    try:
        processed_contact["urn_type"] = get_contact_urn_types(contact.get("urns",[]))[0]
    except IndexError:
        processed_contact["urn_type"] = None
        logging.debug("Contact %s has no URN. Set as None", contact.get("uuid", "<UUID not found>"))
    except ValueError:
        processed_contact["contact_urn_type"] = None
        logging.debug("Contact %s has no URN. Set as None", contact.get("uuid", "<UUID not found>"))
    
    return processed_contact

