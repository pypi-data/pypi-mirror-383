# -*- coding: utf-8 -*-
"""
This module processes message objects from RapidPro API.
It flattens nested fields, checks for labels, and merges metadata.
"""
import logging
from .contact_processors import get_contact_urn_type


def is_in_labels(message_labels, labels=None):
    """
    Checks if any of the specified labels are present in the message's labels.

    Args:
        message_labels (list of dict): A list of label dictionaries, each expected to have a "name" key.
        labels (list of str, optional): A list of label names to check for presence in message_labels.

    Returns:
        list of dict : with the label name as key and True if the label in `labels` is present in `message_labels`, False otherwise.
    Example:
        message_labels = [{"name": "Important"}, {"name": "Urgent"}]
        labels = ["Important", "Urgent", "NotInMessage"]
        is_in_labels(message_labels, labels)
        # will return {"Important": True, "Urgent": True, "NotInMessage": False}
    """
    if not labels:
        return {}
    message_label_names = {label.get("name") for label in message_labels or []}
    return {label: label in message_label_names for label in labels}


def flatten(obj, prefix):
    """
    Flattens a dictionary by prefixing its keys.
    This function takes a dictionary and a prefix string, and returns a new dictionary
    where each key is prefixed with the provided prefix followed by an underscore.
    Args:
        obj (dict): The dictionary to flatten.
        prefix (str): The prefix to add to each key.
    Returns:
        dict : A new dictionary with flattened keys.
    Example:
        flatten({"name": "Alice", "age": 30}, "user")
        # will return {"user_name": "Alice", "user_age": 30}
    """
    if not isinstance(obj, dict):
        return {}
    return {f"{prefix}_{k}": v for k, v in obj.items()}

def process_message(message, labels=None, metadata=None):
    """
    Processes a message object:
    - Flattens contact, channel, and flow fields.
    - Removes attachments, quick_replies, and labels.
    - Adds is_in_labels attribute.
    - Merges with metadata.
    - Adds is_broadcast attribute.
    Args:
        message (dict): The message object to process.
        metadata (dict, optional): Additional metadata to merge into the result.
        labels (list of str, optional): Labels to check against the message's labels.
    Returns:
        dict : Processed message with flattened fields and additional attributes.
    Example:
        message = {
            "id": 123,
            "contact": {"uuid": "d33e9ad5-5c35-414c-abd4-e7451c69ff1d", "name": "Bob McFlow"},
            "channel": {"uuid": "channel-uuid"},
            "flow": {"uuid": "flow-uuid"},
            "labels": [{"name": "Important", "uuid": "d33e9ad5-5c35-414c-abd4-e7451c69ff1d""}, 
                       {"name": "Urgent", "uuid": "d33e9ad5-5c35-414c-abd4-e7451c69ff1e"}],
            "text": "Hello, this is a test message.",
            "attachments": [{"content_type": "image/jpeg", "url": "http://example.com/image.jpg"}],
            "quick_replies": [{"title": "Reply", "payload": "reply_payload"}],
            "urn": "tel:+1234567890",
            "broadcast": 123
        }
        metadata = {"workspace_code": "test_workspace"}
        labels = ["Important", "Urgent", "NotInMessage"]
        processed_message = process_message(message, metadata, labels)
        # will return a processed message with flattened fields and additional attributes.
        
    """
    result = dict(message)  # shallow copy

    # Flatten fields
    for field in ("contact", "channel", "flow"):
        if field in result and isinstance(result[field], dict):
            # Flatten the field with the prefix
            result.update(flatten(result[field], field))
            result.pop(field, None)

    # Add is_in_labels
    if labels:
        result.update(is_in_labels(message.get("labels", None), labels))

    # Process urn if present
    # Add the urn type to the root object
    try:
        result["urn_type"] = get_contact_urn_type(result.get("urn",))[0]
    except ValueError:
        result["urn_type"] = None
        logging.debug("Message %s has no URN. Set as None", result.get("id", "<ID not found>"))
    # Remove attachments and quick_replies
    # Add is_broadcast
    result["is_broadcast"] = bool(message.get("broadcast"))
    # Merge with metadata
    if metadata:
        result.update(metadata)
    return result