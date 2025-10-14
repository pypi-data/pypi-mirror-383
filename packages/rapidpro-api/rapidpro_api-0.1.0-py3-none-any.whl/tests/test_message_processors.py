import pytest
from unittest.mock import MagicMock, patch

from rapidpro_api.message_processors import process_message, is_in_labels, flatten


@pytest.fixture
def real_sample_message():
    return {
        "id": 4105426,
        "broadcast": 2690007,
        "contact": {"uuid": "d33e9ad5-5c35-414c-abd4-e7451c69ff1d", "name": "Bob McFlow"},
        "urn": "tel:+1234567890",
        "channel": {"uuid": "9a8b001e-a913-486c-80f4-1356e23f582e", "name": "Vonage"},
        "direction": "out",
        "type": "text",
        "status": "wired",
        "visibility": "visible",
        "text": "How are you?",
        "attachments": [{"content_type": "audio/wav", "url": "http://domain.com/recording.wav"}],
        "quick_replies": [{"text": "Great"}, {"text": "Improving"}],
        "labels": [{"name": "Important", "uuid": "5a4eb79e-1b1f-4ae3-8700-09384cca385f"}],
        "flow": {"uuid": "254fd2ff-4990-4621-9536-0a448d313692", "name": "Registration"},
        "created_on": "2016-01-06T15:33:00.813162Z",
        "sent_on": "2016-01-06T15:35:03.675716Z",
        "modified_on": "2016-01-06T15:35:03.675716Z"
    }

def test_process_message_with_real_sample(real_sample_message):
    result = process_message(real_sample_message, 
                            metadata={"workspace_code": "test_workspace"},
                            labels=["Important", "Urgent"])
    assert result is not None
    # ensure dicstionary keys are flattened and processed correctly
    assert "contact_uuid" in result
    assert result["contact_uuid"] == "d33e9ad5-5c35-414c-abd4-e7451c69ff1d"
    assert "contact_name" in result
    assert result["contact_name"] == "Bob McFlow"
    assert "urn_type" in result
    assert "channel_uuid" in result
    assert "flow_uuid" in result

    assert "is_broadcast" in result
    assert result["is_broadcast"] is True
    assert "Important" in result
    assert result["Important"] is True
    assert "Urgent" in result
    assert result["Urgent"] is False
    assert "workspace_code" in result
    assert result["workspace_code"] == "test_workspace"

# Is in labels test
def test_is_in_labels_with_labels(real_sample_message):
    labels = ["Important", "Urgent"]
    result = is_in_labels(real_sample_message['labels'], labels=labels)
    assert result is not None
    assert result["Important"] is True
    assert result["Urgent"] is False

def test_is_in_labels_without_labels(real_sample_message):
    result = process_message(real_sample_message)
    assert result is not None
    assert "Important" not in result

def test_flatten_with_valid_dict():
    obj = {"name": "Alice", "age": 30}
    prefix = "user"
    result = flatten(obj, prefix)
    assert result == {"user_name": "Alice", "user_age": 30}

# Flatten text   
def test_flatten_with_empty_dict():
    obj = {}
    prefix = "user"
    result = flatten(obj, prefix)
    assert result == {}


def test_flatten_with_non_dict():
    obj = ["Alice", "Bob"]
    prefix = "user"
    result = flatten(obj, prefix)
    assert result == {}

def test_process_message_missing_some_fields_gets_processed():
    message = {
        "id": 123,
        "sender": "user789"
    }
    process_message(message)
    assert message is not None
    assert message.get("id") == 123

def test_process_message_empty_text(real_sample_message):
  real_sample_message["text"] = ""
  result = process_message(real_sample_message)
  assert result is not None

def test_process_message_with_no_labels(real_sample_message):
  real_sample_message["labels"] = []
  result = process_message(real_sample_message)
  assert result is not None

def test_process_message_with_none_labels(real_sample_message):
  real_sample_message["labels"] = None
  result = process_message(real_sample_message)
  assert result is not None

def test_process_message_with_no_quick_replies(real_sample_message):
  real_sample_message["quick_replies"] = []
  result = process_message(real_sample_message)
  assert result is not None

def test_process_message_with_invalid_attachments(real_sample_message):
  real_sample_message["attachments"] = [{}]
  result = process_message(real_sample_message)
  assert result is not None

def test_process_message_with_missing_contact(real_sample_message):
  del real_sample_message["contact"]
  result = process_message(real_sample_message)
  assert result is not None

def test_process_message_with_missing_channel(real_sample_message):
    del real_sample_message["channel"]
    result = process_message(real_sample_message)
    assert result is not None


