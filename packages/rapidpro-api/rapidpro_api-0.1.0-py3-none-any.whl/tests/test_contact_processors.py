import pytest
from unittest.mock import patch, MagicMock
import logging
from datetime import datetime
from freezegun import freeze_time

from rapidpro_api.contact_processors import (
  get_contact_urn_type,
  get_contact_urn_types,
  filter_contact_fields,
  get_age_group,
  parse_gender,
  process_contact
)


class TestGetContactUrnType:
  def test_valid_urn(self):
    assert get_contact_urn_type("facebook:12345") == "facebook"
    assert get_contact_urn_type("twitter:username") == "twitter"
    assert get_contact_urn_type("tel:+1234567890") == "tel"

  def test_invalid_urn_format(self):
    with pytest.raises(ValueError):
      get_contact_urn_type("facebook12345")
  
  def test_non_string_urn(self):
    with pytest.raises(ValueError):
      get_contact_urn_type(12345)
    with pytest.raises(ValueError):
      get_contact_urn_type(None)
    with pytest.raises(ValueError):
      get_contact_urn_type(["facebook:12345"])


class TestGetContactUrnTypes:
  def test_valid_urns(self):
    urns = ["facebook:12345", "twitter:username", "tel:+1234567890"]
    assert get_contact_urn_types(urns) == ["facebook", "twitter", "tel"]
  
  def test_empty_list(self):
    assert get_contact_urn_types([]) == []
  
  def test_non_list_urns(self):
    assert get_contact_urn_types("facebook:12345") == []
    assert get_contact_urn_types(None) == []
    assert get_contact_urn_types(123) == []


class TestFilterContactFields:
  def test_valid_filtering(self):
    all_fields = {"field1": "value1", "field2": "value2", "field3": "value3"}
    fields_to_filter = ["field1", "field3"]
    expected = {"field1": "value1", "field3": "value3"}
    assert filter_contact_fields(all_fields, fields_to_filter) == expected
  
  def test_missing_fields(self):
    all_fields = {"field1": "value1"}
    fields_to_filter = ["field1", "field2"]
    expected = {"field1": "value1", "field2": None}
    assert filter_contact_fields(all_fields, fields_to_filter) == expected
  
  def test_empty_filters(self):
    all_fields = {"field1": "value1", "field2": "value2"}
    assert filter_contact_fields(all_fields, []) == {}
  
  def test_invalid_input(self):
    assert filter_contact_fields(None, ["field1"]) == {}
    assert filter_contact_fields({"field1": "value1"}, None) == {}
    assert filter_contact_fields({"field1": "value1"}, "field1") == {}


class TestGetAgeGroup:
  def test_valid_ages(self):
    # freeze the date to a specific point for consistent age calculations
    with freeze_time("2000-01-01"):
      assert get_age_group(2000) == "0-14"
      assert get_age_group(1986) == "0-14"
      assert get_age_group(1985) == "15-19"
      assert get_age_group(1981) == "15-19"
      assert get_age_group(1980) == "20-24"
      assert get_age_group(1976) == "20-24"
      assert get_age_group(1975) == "25-30"
      assert get_age_group(1970) == "25-30"
      assert get_age_group(1969) == "31-34"
      assert get_age_group(1966) == "31-34"
      assert get_age_group(1965) == "35+"
      assert get_age_group(1940) == "35+"
    
  def test_edge_cases(self):
    assert get_age_group(-1) == "None"
    assert get_age_group(None) == "None"
    assert get_age_group("not a year") == "None"
    assert get_age_group("-1") == "None"
    

class TestParseGender:
  def test_male_terms(self):
    assert parse_gender("male") == "Male"
    assert parse_gender("MALE") == "Male"
    assert parse_gender("boy") == "Male"
    assert parse_gender("hombre") == "Male"
    assert parse_gender("Gabo") == "Male"
  
  def test_female_terms(self):
    assert parse_gender("female") == "Female"
    assert parse_gender("FEMALE") == "Female"
    assert parse_gender("girl") == "Female"

    assert parse_gender("mujer") == "Female"
  
  def test_other_terms(self):
    assert parse_gender("other") == "Invalid"
    assert parse_gender("unknown") == "Invalid"
    assert parse_gender("anything_else") == "Invalid"
  
  def test_empty_input(self):
    assert parse_gender("") == "None"
    assert parse_gender(None) == "None"
  
  def test_with_female_list(self):
    assert parse_gender("weird") == "Invalid"
    assert parse_gender("weird", female_list=["weird"]) == "Female"

  def test_with_male_list(self):
    assert parse_gender("weird") == "Invalid"
    assert parse_gender("weird", female_list=["weird"]) == "Female"
   
  
  def test_extend_to_default_list_false(self):
    assert parse_gender("male", male_list=["weird"], extend_default_list=False) == "Invalid"
    assert parse_gender("female", female_list=["weird"], extend_default_list=False) == "Invalid"
    

class TestProcessContact:
  @pytest.fixture
  def sample_contact(self):
    return {
      "uuid": "12345678-1234-1234-1234-123456789012",
      "name": "John Doe",
      "urns": ["tel:+1234567890", "facebook:johndoe"],
      "groups": [{"name": "group1"}, {"name": "group2"}],
      "fields": {"field1": "value1", "field2": "value2"},
      "created_on": "2023-01-01T00:00:00Z",
      "modified_on": "2023-02-01T00:00:00Z",
      "last_seen_on": "2024-03-01T00:00:00Z",
      "status": "active"
    }
  
  def test_basic_processing(self, sample_contact):
    result = process_contact(sample_contact)
    assert result["uuid"] == sample_contact["uuid"]
    assert result["name"] == sample_contact["name"]
    assert result["urn_type"] == "tel"
    assert result["created_on_year"] == "2023"
    assert result["created_on_month"] == "2023-01"
    assert result["created_on_day"] == "2023-01-01"
    assert result["last_seen_on_year"] == "2024"
    assert result["last_seen_on_month"] == "2024-03"
    assert result["last_seen_on_day"] == "2024-03-01"

  
  def test_with_fields(self, sample_contact):
    result = process_contact(sample_contact, fields=["field1"])
    assert result["field1"] == "value1"
    assert "field2" not in result
  
  def test_with_groups(self, sample_contact):
    result = process_contact(sample_contact, groups=["group1", "group3"])
    assert result["group1"] is True
    assert result["group3"] is False
  
  def test_with_metadata(self, sample_contact):
    metadata = {"source": "test", "batch": 123}
    result = process_contact(sample_contact, metadata=metadata)
    assert result["source"] == "test"
    assert result["batch"] == 123
  
  def test_invalid_created_on(self, sample_contact):
    with patch("rapidpro_api.contact_processors.logging") as mock_logging:
      invalid_contact = sample_contact.copy()
      invalid_contact["created_on"] = "not a date"
      result = process_contact(invalid_contact)
      assert "created_on_year" not in result
      mock_logging.warning.assert_called()
  
  def test_missing_urns(self, sample_contact):
    contact_no_urns = sample_contact.copy()
    del contact_no_urns["urns"]
    result = process_contact(contact_no_urns)
    assert result["urn_type"] is None
  
  def test_invalid_contact_type(self):
    with pytest.raises(ValueError):
      process_contact("not a dict")
  
  def test_invalid_metadata_type(self, sample_contact):
    with pytest.raises(ValueError):
      process_contact(sample_contact, metadata="not a dict")
