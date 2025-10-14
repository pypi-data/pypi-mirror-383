import pytest
import polars as pl
from unittest.mock import patch, MagicMock
import logging
from datetime import datetime
from freezegun import freeze_time

from rapidpro_api.contact_processors_pl import process_contacts_pl


@pytest.fixture
def sample_contacts():
    """Create a sample Polars DataFrame with mock contact data."""
    return [
        {
            "uuid": "12345678-1234-1234-1234-123456789012",
            "name": "John Doe",
            "urns": ["tel:+1234567890", "facebook:johndoe"],
            "groups": [{"uuid": "ug1", "name": "group1"}, {"uuid": "ug2", "name": "group2"}],
            "fields": {"field1": "value1", "field2": "value2", "gender": "male", "born": "1990"},
            "created_on": "2023-01-01T00:00:00Z",
            "modified_on": "2023-02-01T00:00:00Z",
            "last_seen_on": "2024-03-01T00:00:00Z",
            "status": "active"
        },
        {
            "uuid": "87654321-4321-4321-4321-210987654321",
            "name": "Jane Smith",
            "urns": ["facebook:janesmith"],
            "groups": [{"uuid": "ug2", "name": "group2"}, {"uuid": "ug3","name": "group3"}],
            "fields": {"field1": "other_value", "field3": "value3", "gender": "female"},
            "created_on": "2023-02-15T00:00:00Z",
            "modified_on": "2023-03-01T00:00:00Z",
            "last_seen_on": None,
            "status": "active"
        }
    ]


@pytest.fixture
def empty_contacts():
    """Create an empty Polars DataFrame with the right schema."""
    return []


class TestProcessContactsPl:
    def test_empty_dataframe(self, empty_contacts):
        """Test that an empty dataframe returns an empty dataframe."""
        with patch("rapidpro_api.contact_processors_pl.logging") as mock_logging:
            result = process_contacts_pl(empty_contacts)
            assert result.is_empty()
            mock_logging.warning.assert_called_once()

    def test_basic_processing(self, sample_contacts):
        """Test basic processing of contacts."""
        result = process_contacts_pl(sample_contacts)
        
        # Check row count
        assert len(result) == 2
        
        # Check that the first contact has the expected date components
        row0 = result.row(0, named=True)
        assert row0["created_on_year"] == "2023"
        assert row0["created_on_month"] == "2023-01"
        assert row0["created_on_day"] == "2023-01-01"
        assert row0["last_seen_on_year"] == "2024"
        assert row0["last_seen_on_month"] == "2024-03"
        assert row0["last_seen_on_day"] == "2024-03-01"
        
        # Check that the original data is preserved
        assert row0["uuid"] == "12345678-1234-1234-1234-123456789012"
        assert row0["status"] == "active"

    def test_last_seen_fallback(self, sample_contacts):
        """Test that last_seen_on falls back to modified_on when null."""
        result = process_contacts_pl(sample_contacts)
        
        # Second row has null last_seen_on
        row1 = result.row(1, named=True)
        
        # Should fall back to modified_on
        assert row1["last_seen_on"] == "2023-03-01T00:00:00Z"
        assert row1["last_seen_on_year"] == "2023"
        assert row1["last_seen_on_month"] == "2023-03"
        assert row1["last_seen_on_day"] == "2023-03-01"

    def test_with_metadata(self, sample_contacts):
        """Test adding metadata columns."""
        metadata = {"source": "test", "batch": 123}
        result = process_contacts_pl(sample_contacts, metadata=metadata)
        
        # Check that metadata columns were added
        assert result.row(0, named=True)["source"] == "test"
        assert result.row(0, named=True)["batch"] == 123
        assert result.row(1, named=True)["source"] == "test"
        assert result.row(1, named=True)["batch"] == 123

    def test_with_fields(self, sample_contacts):
        """Test extracting fields from the nested fields column."""
        result = process_contacts_pl(sample_contacts, fields=["field1", "field3"])
        
        # Check that fields were extracted
        row0 = result.row(0, named=True)
        row1 = result.row(1, named=True)
        
        assert row0["field1"] == "value1"
        # assert row0["field3"] exists but is None
        # because first contact doesn't have field3
        assert "field3" in row0
        assert row0["field3"] is None  # First contact doesn't have field3
        
        assert row1["field1"] == "other_value"
        assert row1["field3"] == "value3"

    def test_with_groups(self, sample_contacts):
        """Test extracting group membership."""
        result = process_contacts_pl(sample_contacts, groups=["group1", "group3"])
        
        # Check that group membership was extracted
        row0 = result.row(0, named=True)
        row1 = result.row(1, named=True)
        
        assert row0["group1"] is True
        assert row0["group3"] is False
        
        assert row1["group1"] is False
        assert row1["group3"] is True

    def test_extract_urn_type(self, sample_contacts):
        """Test extracting URN type."""
        result = process_contacts_pl(sample_contacts)
        
        # Check URN type extraction
        assert result.row(0, named=True)["urn_type"] == "tel"
        assert result.row(1, named=True)["urn_type"] == "facebook"

    def test_missing_columns(self):
        """Test processing with missing columns."""
        # Create a DataFrame with missing columns
        contacts = [
            {"uuid": "12345", "name": "Test Contact"}
            # Missing other columns
        ]
        # Should process without error
        result = process_contacts_pl(contacts)
        assert len(result) == 1
        assert "created_on_year" not in result.columns
        assert "last_seen_on_year" not in result.columns

    def test_empty_nested_data(self):
        """Test processing with empty nested data (fields, groups, urns)."""
        contacts = [
            {
                "uuid": "12345",
                "fields": {},  # Empty fields
                "groups": [],  # Empty groups
                "urns": []     # Empty URNs
            }
        ]
        
        result = process_contacts_pl(contacts, fields=["field1"], groups=["group1"])
        assert len(result) == 1
        assert result.row(0, named=True)["field1"] is None
        assert result.row(0, named=True)["group1"] is False
        assert result.row(0, named=True)["urn_type"] is None

    def test_null_nested_data(self):
        """Test processing with null nested data."""
        contacts = [{
            "uuid": ["12345"],
            "fields": {},  # Null fields
            "groups": [],  # Null groups 
            "urns": []     # Null URNs
        }]
        
        result = process_contacts_pl(contacts, fields=["field1"], groups=["group1"])
        assert len(result) == 1
        assert result.row(0, named=True)["field1"] is None
        assert result.row(0, named=True)["group1"] is False
        assert result.row(0, named=True)["urn_type"] is None

    def test_invalid_metadata_type(self, sample_contacts):
        """Test handling invalid metadata type."""
        # Not a dictionary
        result = process_contacts_pl(sample_contacts, metadata="not a dict")
        # Should not add metadata but still process dataframe
        assert len(result) == 2
        assert "not a dict" not in result.columns