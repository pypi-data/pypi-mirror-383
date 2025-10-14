import pytest
from rapidpro_api.group_processors import is_in_groups
from rapidpro_api.group_processors import process_group


def test_is_in_groups_positive():
  # Test when groups_to_check are present in groups
  groups = [
    {"name": "group1", "uuid": "12345678-1234-1234-1234-123456789011"},
    {"name": "group2", "uuid": "12345678-1234-1234-1234-123456789012"}
  ]
  groups_to_check = ["group1", "group2"]
  expected_result = {"group1": True, "group2": True}
  assert is_in_groups(groups, groups_to_check) == expected_result


def test_is_in_groups_partial_match():
  # Test when only some groups_to_check are present in groups
  groups = [
    {"name": "group1", "uuid": "12345678-1234-1234-1234-123456789011"},
    {"name": "group2", "uuid": "12345678-1234-1234-1234-123456789012"}
  ]
  groups_to_check = ["group1", "group3"]
  expected_result = {"group1": True, "group3": False}
  assert is_in_groups(groups, groups_to_check) == expected_result


def test_is_in_groups_no_match():
  # Test when none of the groups_to_check are present in groups
  groups = [
    {"name": "group1", "uuid": "12345678-1234-1234-1234-123456789011"},
    {"name": "group2", "uuid": "12345678-1234-1234-1234-123456789012"}
  ]
  groups_to_check = ["group3", "group4"]
  expected_result = {"group3": False, "group4": False}
  assert is_in_groups(groups, groups_to_check) == expected_result


def test_is_in_groups_empty_groups_to_check():
  # Test when groups_to_check is an empty list
  groups = [
    {"name": "group1", "uuid": "12345678-1234-1234-1234-123456789011"},
    {"name": "group2", "uuid": "12345678-1234-1234-1234-123456789012"}
  ]
  groups_to_check = []
  expected_result = {}
  assert is_in_groups(groups, groups_to_check) == expected_result


def test_is_in_groups_none_groups_to_check():
  # Test when groups_to_check is None
  groups = [
    {"name": "group1", "uuid": "12345678-1234-1234-1234-123456789011"},
    {"name": "group2", "uuid": "12345678-1234-1234-1234-123456789012"}
  ]
  groups_to_check = None
  expected_result = {}
  assert is_in_groups(groups, groups_to_check) == expected_result


def test_is_in_groups_invalid_groups_to_check():
  # Test when groups_to_check is not a list
  groups = [
    {"name": "group1", "uuid": "12345678-1234-1234-1234-123456789011"},
    {"name": "group2", "uuid": "12345678-1234-1234-1234-123456789012"}
  ]
  groups_to_check = "group1"
  with pytest.raises(ValueError):
    is_in_groups(groups, groups_to_check)


def test_is_in_groups_empty_groups():
  # Test when groups is an empty list
  groups = []
  groups_to_check = ["group1", "group2"]
  expected_result = {"group1": False, "group2": False}
  assert is_in_groups(groups, groups_to_check) == expected_result


def test_process_group_with_metadata():
    # Test when metadata is provided
    group = {
      "uuid": "5f05311e-8f81-4a67-a5b5-1501b6d6496a",
      "name": "Reporters",
      "query": None,
      "status": "ready",
      "system": False,
      "count": 315
    }
    metadata = {
      "workspace_code": "test_workspace"
    }
    expected_result = {
      "uuid": "5f05311e-8f81-4a67-a5b5-1501b6d6496a",
      "name": "Reporters",
      "query": None,
      "status": "ready",
      "system": False,
      "count": 315,
      "workspace_code": "test_workspace",
      "ingestion_day": None,
      "ingestion_month": None,
      "ingestion_year": None,
      "ingestion_date": None,
    }
    assert process_group(group, metadata) == expected_result


def test_process_group_without_metadata():
    # Test when metadata is None
    group = {
      "uuid": "5f05311e-8f81-4a67-a5b5-1501b6d6496a",
      "name": "Reporters",
      "count": 315
    }
    expected_result = {
      "uuid": "5f05311e-8f81-4a67-a5b5-1501b6d6496a",
      "name": "Reporters",
      "count": 315,
      "ingestion_day": None,
      "ingestion_month": None,
      "ingestion_year": None,
      "ingestion_date": None,
    }
    assert process_group(group, None) == expected_result
  

def test_process_group_empty_metadata():
    # Test when metadata is an empty dictionary
    group = {
      "uuid": "5f05311e-8f81-4a67-a5b5-1501b6d6496a",
      "name": "Reporters",
      "count": 315,
      "ingestion_day": None,
      "ingestion_month": None,
      "ingestion_year": None
    }
    metadata = {}
    expected_result = group.copy()
    expected_result["ingestion_date"] = None
    assert process_group(group, metadata) == expected_result


def test_process_group_empty_group():
    # Test when group is an empty dictionary
    group = {}
    metadata = {"workspace_code": "test_workspace"}
    expected_result = {"workspace_code": "test_workspace", 
                       "ingestion_day": None, 
                       "ingestion_month": None, 
                       "ingestion_year": None,
                       "ingestion_date": None}
    assert process_group(group, metadata) == expected_result


def test_process_group_original_not_modified():
    # Test that the original group is not modified
    group = {
      "uuid": "5f05311e-8f81-4a67-a5b5-1501b6d6496a",
      "name": "Reporters"
    }
    metadata = {"workspace_code": "test_workspace"}
    original_group = group.copy()
    
    processed_group = process_group(group, metadata)
    
    # Check original not modified
    assert group == original_group
    # Check processed group has expected content
    assert processed_group != original_group
    assert processed_group["workspace_code"] == "test_workspace"


def test_process_group_metadata_override():
    # Test when metadata has keys that already exist in group
    group = {
      "uuid": "5f05311e-8f81-4a67-a5b5-1501b6d6496a",
      "name": "Reporters"
    }
    metadata = {"name": "New Name", "workspace_code": "test_workspace"}
    expected_result = {
      "uuid": "5f05311e-8f81-4a67-a5b5-1501b6d6496a",
      "name": "New Name",
      "workspace_code": "test_workspace",
      "ingestion_day": None,
      "ingestion_month": None,
      "ingestion_year": None,
      "ingestion_date": None,
    }
    assert process_group(group, metadata) == expected_result
