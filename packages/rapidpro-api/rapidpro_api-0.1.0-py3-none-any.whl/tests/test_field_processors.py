import pytest
from rapidpro_api.field_processors import process_field

def test_process_field_no_metadata():
  """
  Test process_field with no metadata.
  """
  field = {"key": "reporters", "name": "Reporters", "type": "text"}
  expected_result = {"key": "reporters", "name": "Reporters", "type": "text"}
  assert process_field(field) == expected_result

def test_process_field_with_empty_metadata():
  """
  Test process_field with empty metadata.
  """
  field = {"key": "reporters", "name": "Reporters", "type": "text"}
  metadata = {}
  expected_result = {"key": "reporters", "name": "Reporters", "type": "text"}
  assert process_field(field, metadata) == expected_result

def test_process_field_with_metadata():
  """
  Test process_field with metadata.
  """
  field = {"key": "reporters", "name": "Reporters", "type": "text"}
  metadata = {"workspace_code": "test_workspace", "country": "RW"}
  expected_result = {
    "key": "reporters",
    "name": "Reporters",
    "type": "text",
    "workspace_code": "test_workspace",
    "country": "RW"
  }
  assert process_field(field, metadata) == expected_result

def test_process_field_empty_field_with_metadata():
  """
  Test process_field with an empty field and metadata.
  """
  field = {}
  metadata = {"workspace_code": "test_workspace"}
  expected_result = {"workspace_code": "test_workspace"}
  assert process_field(field, metadata) == expected_result

def test_process_field_metadata_overwrites_field():
  """
  Test that metadata overwrites existing keys in the field.
  """
  field = {"key": "reporters", "name": "Reporters", "type": "text", "workspace_code": "old_workspace"}
  metadata = {"workspace_code": "new_workspace", "name": "New Reporters"}
  expected_result = {
    "key": "reporters",
    "name": "New Reporters",
    "type": "text",
    "workspace_code": "new_workspace"
  }
  assert process_field(field, metadata) == expected_result

def test_process_field_is_deep_copy():
  """
  Test that process_field performs a deep copy of the field.
  """
  field = {"key": "reporters", "name": "Reporters", "details": {"status": "active"}}
  metadata = {"workspace_code": "test_workspace"}
  
  processed_field = process_field(field, metadata)
  
  # Modify original field
  field["key"] = "new_key"
  field["details"]["status"] = "inactive"
  
  expected_result = {
    "key": "reporters",
    "name": "Reporters",
    "details": {"status": "active"},
    "workspace_code": "test_workspace"
  }
  
  assert processed_field == expected_result
  assert processed_field["details"] is not field["details"]

def test_process_field_with_none_metadata_explicitly():
  """
  Test process_field when metadata is explicitly None.
  """
  field = {"key": "age", "label": "Age"}
  expected_result = {"key": "age", "label": "Age"}
  assert process_field(field, metadata=None) == expected_result

def test_process_field_input_field_not_modified():
  """
  Test that the input field dictionary is not modified.
  """
  field_original = {"key": "reporters", "name": "Reporters", "type": "text"}
  field_copy_for_test = field_original.copy() # To compare against
  metadata = {"workspace_code": "test_workspace"}
  
  process_field(field_original, metadata)
  
  # Check that the original field dictionary remains unchanged
  assert field_original == field_copy_for_test