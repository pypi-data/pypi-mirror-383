"""Validation functions. They return True of False based on the validation of the
input. The validation is based on the RapidPro documentation. 
The validators that include lib_ in the name, are specific to this library and are
not part of the restrictions imposed by RapidPro. For example, you cannot process
a group with the name "1group" in this library but you can in RapidPro.
"""
# -*- coding: utf-8 -*-
import logging


def validate_field_name(field_name):
    """
    Validate the field name is a valid RapidPro field name.
    A field name can only contain letters, numbers and hyphens.
    A field name cannot start with a number.
    Max length is 36 chars.

    Args:
        field_name (str): field name to validate
    Returns:
        bool: True if the field name is valid, False otherwise
    """
    if len(field_name) == 0:
        logging.debug("Field name %s is empty", field_name)
        return False
    if len(field_name) > 36:
        logging.debug("Field name %s is too long", field_name)
        return False
    if not field_name[0].isalpha():
        logging.debug("Field name %s cannot start with a number", field_name)
        return False
    for c in field_name:
        if not (c.isalnum() or c == "-"):
            logging.debug("Field name %s contains invalid character %s", field_name, c)
            return False
    return True

# Note, it should be possible to use the same function for both flow and group names
# but for clarity, we keep them separate.

def validate_result_name(result_name):
    """
     Validates the result name is a valid RapidPro result name.
     A result name can only contain letters, numbers, hyphens and underscores.
     A result name cannot start with a number.
     Max length is 64 chars.
     Args:
         result_name (str): result name to validate
     Returns:
         bool: True if the result name is valid, False otherwise
    """
    if len(result_name) == 0:
        logging.debug("Result name %s is empty", result_name)
        return False
    if len(result_name) > 64:
        logging.debug("Result name %s is too long", result_name)
        return False
    if not result_name[0].isalpha():
        logging.debug("Result name %s cannot start with a number", result_name)
        return False
    for c in result_name:
        if not (c.isalnum() or c == "-" or c == "_"):
            logging.debug("Result name %s contains invalid character %s", result_name, c)
            return False
    return True


def validate_lib_flow_name(flow_name):
    """
    Validates the flow name is a valid library flow name.
    Whereas RapidPro allows you to create groups with any name, this library 
    imposes some restrictions.
    A flow name can only contain letters, numbers, hyphens and underscores.
    A flow name cannot start with a number.
    Max length is 64 chars.
    Args:
        flow_name (str): flow name to validate
    Returns:
        bool: True if the flow name is valid, False otherwise
    """
    if len(flow_name) == 0:
        logging.debug("Flow name %s is empty", flow_name)
        return False
    if len(flow_name) > 64:
        logging.debug("Flow name %s is too long", flow_name)
        return False
    if not flow_name[0].isalpha():
        logging.debug("Flow name %s cannot start with a number", flow_name)
        return False
    for c in flow_name: 
        if not (c.isalnum() or c == "-" or c == "_"):
            logging.debug("Flow name %s contains invalid character %s", flow_name, c)
            return False
    return True


def validate_lib_group_name(group_name):
    """
    Validates the group name is a valid group name within this library.
    Whereas RapidPro allows you to create groups with any name, this library
    imposes some restrictions.
    A group name can only contain letters, numbers, hyphens and underscores.
    A group name cannot start with a number.
    Max length is 64 chars.
    Args:
        group_name (str): group name to validate
    Returns:
        bool: True if the group name is valid, False otherwise
    """
    if len(group_name) == 0:
        logging.debug("Group name %s is empty", group_name)
        return False
    if len(group_name) > 64:
        logging.debug("Group name %s is too long", group_name)
        return False
    if not group_name[0].isalpha():
        logging.debug("Group name %s cannot start with a number", group_name)
        return False
    for c in group_name:
        if not (c.isalnum() or c == "-" or c == "_"):
            logging.debug("Group name %s contains invalid character %s", group_name, c)
            return False
    return True
