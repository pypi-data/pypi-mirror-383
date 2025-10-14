# -*- coding: utf-8 -*-
"""
@file   group_processors.py
@brief  Group processors
@details
This module contains functions to process groups in RapidPro API format.
"""
import logging
import copy
from datetime import datetime

def is_in_groups(groups, groups_to_check):
    """
    For each group in the groups_check list checks if the contact is in the group.
   
    Args:
        groups (list): A list of groups in RapidPro API format, a dictionary with the group name and uuid. (e.g. [{"name": "group1", "uuid": "12345678-1234-1234-1234-123456789012"}]).
        groups_to_check (list): A list of groups to check if the contact is in (e.g. ["group1", "group2"]).
    Returns:
        dict : A dictionary with the group name as key and a boolean value as value. The value is True if the contact is in the group, False otherwise.
    Example:
        contact_groups = [{"name": "group1", "uuid": "12345678-1234-1234-1234-123456789011"}, {"name": "group2", "uuid": "12345678-1234-1234-1234-123456789012"}]
        groups_to_check = ["group1", "group3"]
        is_contact_in_groups(contact_groups, groups_to_check)
        # will return {"group1": True, "group3": False}
    """

    if groups_to_check is None:
        return {}

    if not isinstance(groups_to_check, list):
        logging.error("Contact groups is not a list")
        raise ValueError("groups_to_check is not a list")

    groups_checked = {}
    # get groups names
    groups_names = [group["name"] for group in groups]
    for group in groups_to_check:
        if group in groups_names:
            groups_checked[group] = True
        else:
            groups_checked[group] = False
    return groups_checked


def process_group(group, metadata:dict=None, ingestion_date:datetime=None):
    """
    Processes a group object. Merges with metadata.
    
    Args:
        group (dict): The group object to process.
        metadata (dict, optional): Additional metadata to merge with the group object.
        ingestion_date (datetime, optional): The date when the group was ingested. If provided, it will add fields for year, month, and day.
        
    Returns:
        dict: The processed group object.
    Example: 
        group ={
            "uuid": "5f05311e-8f81-4a67-a5b5-1501b6d6496a",
            "name": "Reporters",
            "query": null,
            "status": "ready",
            "system": false,
            "count": 315
        }
        metadata = {
            "workspace_code": "test_workspace"
        }
        processed_group = process_group(group, metadata)
        # will return {
            "uuid": "5f05311e-8f81-4a67-a5b5-1501b6d6496a",
            "name": "Reporters",
            "query": null,
            "status": "ready",
            "system": false,
            "count": 315,
            "workspace_code": "test_workspace"
            "ingestion_year": 2023,
            "ingestion_month": "2023-10",
            "ingestion_day": "2023-10-01"
        }
    """
    result = copy.deepcopy(group)

    # Add the ingestion date if provided
    if ingestion_date:
        result['ingestion_year'] = ingestion_date.year
        result['ingestion_month'] = ingestion_date.strftime('%Y-%m')
        result['ingestion_day'] = ingestion_date.strftime('%Y-%m-%d')
        result['ingestion_date'] = ingestion_date
    else:
        # If no ingestion date is provided, set default values
        result['ingestion_year'] = None
        result['ingestion_month'] = None
        result['ingestion_day'] = None
        result['ingestion_date'] = None

    # Merge with metadata
    if metadata:
        result.update(metadata)
    return result