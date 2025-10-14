import pytest
from rapidpro_api.flow_processors import process_flow

@pytest.fixture
def sample_flows():
  return [
    {
      "uuid": "c5d67e0a-ffa5-4240-8f9d-111111111111",
      "name": "Test flow 1",
      "type": "message",
      "archived": False,
      "labels": [],
      "expires": 4320,
      "created_on": "2025-05-22T08:11:05.795588Z",
      "runs": {
        "active": 0,
        "waiting": 0,
        "completed": 0,
        "interrupted": 0,
        "expired": 0,
        "failed": 0
      },
      "results": [
        {
          "key": "report",
          "name": "Report",
          "categories": ["Report", "Other"],
          "node_uuids": ["a4f1aee9-22a6-4a2a-86fe-58874f1ee0a6"]
        }
      ]
    },
    {
      "uuid": "960e2999-91bc-45eb-970e-222222222222",
      "name": "Test Flow2",
      "type": "message",
      "archived": False,
      "labels": [],
      "expires": 4320,
      "created_on": "2025-05-15T07:48:55.945351Z",
      "runs": {
        "active": 0,
        "waiting": 0,
        "completed": 207,
        "interrupted": 0,
        "expired": 0,
        "failed": 0
      },
      "results": []
    }
  ]

def test_process_flow_with_runs(sample_flows):
  flow = sample_flows[0]
  processed = process_flow(flow)
  assert processed["uuid"] == flow["uuid"]
  assert processed["name"] == flow["name"]
  assert processed["active"] == flow["runs"]["active"]
  assert processed["waiting"] == flow["runs"]["waiting"]
  assert "runs" not in processed

def test_process_flow_without_runs(sample_flows):
  flow = sample_flows[1]
  flow.pop("runs", None)  # Remove runs to simulate no runs
  processed = process_flow(flow)
  assert processed["uuid"] == flow["uuid"]
  assert processed["name"] == flow["name"]
  assert "active" not in processed
  assert "waiting" not in processed
  assert "runs" not in processed

def test_process_flow_empty_flow():
  flow = {}
  processed = process_flow(flow)
  assert processed == {}

def test_process_flow_with_extra_fields():
  flow = {
    "uuid": "test-uuid",
    "name": "Test Flow",
    "runs": {"active": 5, "completed": 10},
    "extra_field": "extra_value"
  }
  processed = process_flow(flow)
  assert processed["uuid"] == flow["uuid"]
  assert processed["name"] == flow["name"]
  assert processed["active"] == flow["runs"]["active"]
  assert processed["completed"] == flow["runs"]["completed"]
  assert "extra_field" in processed
  assert processed["extra_field"] == "extra_value"
  assert "runs" not in processed