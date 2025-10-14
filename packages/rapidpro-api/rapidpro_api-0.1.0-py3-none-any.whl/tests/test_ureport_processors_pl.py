import pytest
from unittest.mock import patch, MagicMock
import polars as pl
from rapidpro_api import ureport_processors_pl

@pytest.fixture
def sample_contacts():
  return [
    {
      "uuid": "uuid-1",
      "name": "Alice",
      "status": "active",
      "created_on": "2023-01-01T00:00:00Z",
      "last_seen_on": "2023-01-02T00:00:00Z",
      "urns": ["tel:+1234567890"],
      "language": "en",
      "fields": {
        "registration_date": "2023-01-01",
        "state": "State A",
        "district": "District A",
        "ward": "Ward A",
        "born": "2000",
        "gender": "Female",
        "language": "en"
      },
      "groups": [{"name": "U-Reporter"}]
    },
    {
      "uuid": "uuid-2",
      "name": "Bob",
      "status": "inactive",
      "created_on": "2022-05-10T00:00:00Z",
      "last_seen_on": "2022-06-10T00:00:00Z",
      "urns": ["tel:+0987654321"],
      "language": None,
      "fields": {
        "registration_date": "2022-05-10",
        "state": "State B",
        "district": "District B",
        "ward": "Ward B",
        "born": "",
        "gender": "Male",
        "language": None
      },
      "groups": []
    },
    {
      "uuid": "uuid-3",
      "name": "Charlie",
      "status": "active",
      "created_on": "2021-03-15T00:00:00Z",
      "last_seen_on": "2021-03-20T00:00:00Z",
      "urns": [],
      "language": "fr",
      "fields": {},
      "groups": [{"name": "U-Reporter"}]
    }
  ]

def test_process_ureport_contacts_pl_basic(sample_contacts):
  
  df = ureport_processors_pl.process_ureport_contacts_pl(sample_contacts)
  assert isinstance(df, pl.DataFrame)
  assert set(df.columns) >= {"uuid", "status", "registration_date", "state", "district", "ward", "born", "gender", "age_group", "is_ureporter", "language"}
  assert df.filter(pl.col("uuid") == "uuid-1")["is_ureporter"].to_list()[0] is True
  assert df.filter(pl.col("uuid") == "uuid-2")["is_ureporter"].to_list()[0] is False
  assert df.filter(pl.col("uuid") == "uuid-1")["gender"].to_list()[0] == "Female"
  assert df.filter(pl.col("uuid") == "uuid-2")["gender"].to_list()[0] == "Male"
  assert df.filter(pl.col("uuid") == "uuid-3")["gender"].to_list()[0] == None
  assert df.filter(pl.col("uuid") == "uuid-1")["age_group"].to_list()[0] == "25-30"

def test_process_ureport_contacts_pl_with_metadata_fields(sample_contacts):
  metadata = {
    "registration_field": "RegDate",
    "state_field": "Province",
    "district_field": "Area",
    "ward_field": "Zone",
    "born_field": "BirthYear",
    "gender_field": "Sex",
    "ureporters_group": "SpecialGroup"
  }
  
  df = ureport_processors_pl.process_ureport_contacts_pl(sample_contacts, metadata=metadata)
  assert "registration_date" in df.columns
  assert "state" in df.columns
  assert "district" in df.columns
  assert "ward" in df.columns
  assert "born" in df.columns
  assert "gender" in df.columns
  assert "is_ureporter" in df.columns

def test_process_ureport_contacts_pl_empty():
  df = ureport_processors_pl.process_ureport_contacts_pl([])
  assert isinstance(df, pl.DataFrame)
  assert df.is_empty()

def test_process_ureport_contacts_pl_missing_fields():
  contacts = [
    {"uuid": "u1", "fields": {}, "groups": []}
  ]
  df = ureport_processors_pl.process_ureport_contacts_pl(contacts)
  assert df["gender"].to_list()[0] == None
  assert df["age_group"].to_list()[0] == None
  contacts2 = [
    {"uuid": "u1"}
  ]
  df = ureport_processors_pl.process_ureport_contacts_pl(contacts2)
  assert df["gender"].to_list()[0] == None
  assert df["age_group"].to_list()[0] == None


#### RUNS PROCESSING TESTS ####

@pytest.fixture
def sample_runs():
  return [{
      "uuid": "run-1",
      "flow": {
        "uuid": "f1",
        "name": "Flow 1"
      },
      "contact": {
        "uuid": "uuid-1",
      },
      "values": {
          "key1": {"name": "Question 1", "value": "Answer 1", "category": "Category 1"},
          "key2": {"name": "Question 2", "value": "Answer 2", "category": "Category 2"}
      },
      "exited_on": "2023-01-01T01:00:00Z",
      "exit_type": "completed",
      "responded": True,
      "path": [],
      "start": "2023-01-01T00:00:00Z"
    },
    {
      "uuid": "run-2",
      "flow" : { "uuid": "f2", "name": "Flow 2"},
      "contact": { "uuid": "uuid-2", "urn": "tel:+1234567890" },
      "exited_on": None,
      "exit_type": None,
      "responded": False,
      "contact": {},
      "values": {
        "key3": {"name": "Question 3", "value": "Answer 3", "category": "Category 3"}
      },
      "path": [],
      "start": "2023-01-02T00:00:00Z"
    },
    {
      "uuid": "run-3",
      "flow": {"uuid": "f3", "name": "Flow 3"},
      "contact": {"uuid": "uuid-3"},
      "values": {},
      "exited_on": None,
      "exit_type": None,
      "responded": False,
      "contact": {},
      "flow": {},
      "path": [],
      "start": None
    }
  ]


def test_process_ureport_runs_pl_basic(sample_runs):

  df = ureport_processors_pl.process_ureport_runs_pl(sample_runs)
  assert isinstance(df, pl.DataFrame)
  assert "key" in df.columns
  assert "name" in df.columns
  assert "value" in df.columns
  assert "category" in df.columns
  assert "flow_uuid" in df.columns
  assert "flow_name" in df.columns
  assert "contact_uuid" in df.columns
  assert "exited_on" in df.columns
  assert "exit_type" in df.columns
  assert "responded" in df.columns
  # dropped columns
  for col in ["contact", "flow", "path", "start"]:
    assert col not in df.columns

def test_process_ureport_runs_pl_empty():
  df = ureport_processors_pl.process_ureport_runs_pl([])
  assert isinstance(df, pl.DataFrame)
  assert df.is_empty()

def test_process_ureport_runs_pl_null_columns():

  df = ureport_processors_pl.process_ureport_runs_pl([{
      "uuid": "uuid-1", 
      "contact": {}, "flow": {}, "path": [], "start": None
    }])
  assert df["key"].to_list()[0] == "empty_run"
  assert "contact" not in df.columns
  assert "flow" not in df.columns
  assert "path" not in df.columns
  assert "start" not in df.columns