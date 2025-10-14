import pytest
import polars as pl
from unittest.mock import patch, MagicMock
from rapidpro_api.run_processors_pl import process_runs_pl

@pytest.fixture
def sample_runs():
  """Create sample run data for testing."""
  return [
    {
      "uuid": "run-123",
      "flow": {"uuid": "flow-123", "name": "Test Flow"},
      "contact": {"uuid": "contact-123", "urn": "tel:+1234567890"},
      "values": {
        "question1": {
          "name": "Question 1",
          "value": "Answer 1",
          "category": "Cat1",
          "node": "node1",
          "time": "2023-01-01T10:00:00Z"
        },
        "question2": {
          "name": "Question 2",
          "value": "Answer 2",
          "category": "Cat2",
          "node": "node2",
          "time": "2023-01-01T10:05:00Z"
        }
      }
    },
    {
      "uuid": "run-456",
      "flow": {"uuid": "flow-456", "name": "Another Flow"},
      "contact": {"uuid": "contact-456", "urn": "facebook:user456"},
      "values": {
        "question3": {
          "name": "Question 3",
          "value": "Answer 3",
          "category": "Cat3",
          "node": "node3",
          "time": "2023-01-01T11:00:00Z"
        }
      }
    }
  ]


@pytest.fixture
def runs_with_empty_values():
  """Create runs with empty values."""
  return [
    {
      "uuid": "run-empty",
      "flow": {"uuid": "flow-empty", "name": "Empty Flow"},
      "contact": {"uuid": "contact-empty", "urn": "tel:+0000000000"},
      "values": {}
    }
  ]


@pytest.fixture
def runs_without_optional_fields():
  """Create runs without flow, contact, or values fields."""
  return [
    {
      "uuid": "run-minimal"
    }
  ]

def test_empty_run_batch():
    """Test that empty run batch returns empty DataFrame."""
    result = process_runs_pl([])
    assert result.is_empty()
  
def test_basic_processing(sample_runs):
    """Test basic processing of runs."""

    result = process_runs_pl(sample_runs)
    
    # Should have 3 rows (2 values from first run + 1 value from second run)
    assert len(result) == 3
    
    # Check that values were exploded and normalized
    rows = result.to_dicts()
    
    # First run, first value
    assert rows[0]["uuid"] == "run-123"
    assert rows[0]["flow_uuid"] == "flow-123"
    assert rows[0]["flow_name"] == "Test Flow"
    assert rows[0]["contact_uuid"] == "contact-123"
    assert rows[0]["key"] == "question1"
    assert rows[0]["name"] == "Question 1"
    assert rows[0]["value"] == "Answer 1"
    assert rows[0]["category"] == "Cat1"
    assert rows[0]["node"] == "node1"
    assert rows[0]["time"] == "2023-01-01T10:00:00Z"
    assert rows[0]["urn_type"] == "tel"
    
    # First run, second value
    assert rows[1]["uuid"] == "run-123"
    assert rows[1]["key"] == "question2"
    assert rows[1]["name"] == "Question 2"
    
    # Second run
    assert rows[2]["uuid"] == "run-456"
    assert rows[2]["flow_uuid"] == "flow-456"
    assert rows[2]["contact_uuid"] == "contact-456"
    assert rows[2]["key"] == "question3"
    assert rows[2]["urn_type"] == "facebook"
  

def test_empty_values_handling(runs_with_empty_values):
    """Test handling of runs with empty values."""
    result = process_runs_pl(runs_with_empty_values)
    
    # Should have 1 row with dummy empty_run entry
    assert len(result) == 1
    
    row = result.row(0, named=True)
    assert row["uuid"] == "run-empty"
    assert row["key"] == "empty_run"
    assert row["name"] == "**empty_run**"
    assert row["value"] == ""
    assert row["category"] == ""
    assert row["node"] == ""
    assert row["time"] == ""
  
def test_missing_flow_field(runs_without_optional_fields):
    """Test processing runs without flow field."""
    result = process_runs_pl(runs_without_optional_fields)
    
    # Should process without error
    assert len(result) == 1
    assert "flow_uuid" not in result.columns
    assert "flow_name" not in result.columns
  
def test_missing_contact_field(runs_without_optional_fields):
    """Test processing runs without contact field."""
    result = process_runs_pl(runs_without_optional_fields)
    
    # Should process without error
    assert len(result) == 1
    assert "contact_uuid" not in result.columns
    assert "urn_type" not in result.columns
  
def test_missing_values_field(runs_without_optional_fields):
    """Test processing runs without values field."""
    result = process_runs_pl(runs_without_optional_fields)
    
    # Should still return a row with the run uuid
    assert len(result) == 1
    row = result.row(0, named=True)
    assert row["uuid"] == "run-minimal"
  

def test_with_metadata_cols(sample_runs):
    """Test adding metadata columns."""
    metadata = {"source": "test_source", "batch_id": 42}
    
    result = process_runs_pl(sample_runs, metadata=metadata)
    
    # Check that metadata columns are added
    assert "source" in result.columns
    assert "batch_id" in result.columns
    
    # Check values
    for row in result.to_dicts():
      assert row["source"] == "test_source"
      assert row["batch_id"] == 42
  
def test_invalid_metadata_type(sample_runs):
    """Test handling invalid metadata type."""
    
    # Should not add metadata but still process runs
    result = process_runs_pl(sample_runs, metadata="not a dict") 
    assert len(result) == 3
    assert "not a dict" not in result.columns
  
def test_null_contact_urn(sample_runs):
    """Test handling null contact URN."""
    # Modify sample data to have null URN
    sample_runs[0]["contact"]["urn"] = None
    
    result = process_runs_pl(sample_runs)
    
    # Should handle null URN gracefully
    assert len(result) == 3
    rows = result.to_dicts()
    assert rows[0]["urn_type"] is None
  
def test_column_selection(sample_runs):
    """Test that only expected columns are selected in output."""
    
    result = process_runs_pl(sample_runs)
    
    expected_cols = [
      "uuid", "flow_uuid", "flow_name", "contact_uuid", "urn_type", 
      "key", "name", "value", "category", "node", "time"
    ]
    
    # All expected columns should be present
    for col in expected_cols:
      assert col in result.columns
  

def test_values_as_list():
    """Test processing runs where values is already a list."""   
    runs = [
      {
        "uuid": "run-list",
        "flow": {"uuid": "flow-list", "name": "List Flow"},
        "contact": {"uuid": "contact-list", "urn": "tel:+1111111111"},
        "values": [
          {
            "key": "q1",
            "name": "Question 1",
            "value": "Answer 1",
            "category": "Cat1",
            "node": "node1",
            "time": "2023-01-01T10:00:00Z"
          }
        ]
      }
    ]
    
    result = process_runs_pl(runs)
    
    # Should process correctly
    assert len(result) == 1
    row = result.row(0, named=True)
    assert row["key"] == "q1"
    assert row["name"] == "Question 1"
    
def test_output_column_filtering():
    """Test that non-existent columns are filtered from output."""
    runs = [{"uuid": "test-run"}]  # Minimal run data
    
    result = process_runs_pl(runs)
    
    # Only uuid should be in the output since other columns don't exist
    expected_in_output = ["uuid"]
    for col in expected_in_output:
      assert col in result.columns
    
    # These columns shouldn't exist since source data doesn't have them
    not_expected = ["flow_uuid", "flow_name", "contact_uuid", "urn_type"]
    for col in not_expected:
      assert col not in result.columns