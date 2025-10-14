import os
import pytest
from unittest import mock
from rapidpro_api import telegram

@mock.patch("rapidpro_api.telegram.logging")
def test_message_success(mock_logging):
  with mock.patch.dict(os.environ, {"TELEGRAM_BOT_TOKEN": "token", "TELEGRAM_CHAT_ID": "chatid"}):
    with mock.patch("rapidpro_api.telegram.requests.post") as mock_post:
      mock_response = mock.Mock()
      mock_response.status_code = 200
      mock_response.json.return_value = {"ok": True}
      mock_post.return_value = mock_response

      result = telegram.message("Hello")
      assert result is True
      mock_post.assert_called_once()
      mock_logging.info.assert_called_with("Hello")

@mock.patch("rapidpro_api.telegram.logging")
def test_message_failure_status_code(mock_logging):
  with mock.patch.dict(os.environ, {"TELEGRAM_BOT_TOKEN": "token", "TELEGRAM_CHAT_ID": "chatid"}):
    with mock.patch("rapidpro_api.telegram.requests.post") as mock_post:
      mock_response = mock.Mock()
      mock_response.status_code = 400
      mock_response.json.return_value = {"ok": False}
      mock_post.return_value = mock_response

      result = telegram.message("Hello")
      assert result is False

@mock.patch("rapidpro_api.telegram.logging")
def test_message_failure_json_not_ok(mock_logging):
  with mock.patch.dict(os.environ, {"TELEGRAM_BOT_TOKEN": "token", "TELEGRAM_CHAT_ID": "chatid"}):
    with mock.patch("rapidpro_api.telegram.requests.post") as mock_post:
      mock_response = mock.Mock()
      mock_response.status_code = 200
      mock_response.json.return_value = {"ok": False}
      mock_post.return_value = mock_response

      result = telegram.message("Hello")
      assert result is False

@mock.patch("rapidpro_api.telegram.logging")
def test_message_missing_bot_token(mock_logging):
  with mock.patch.dict(os.environ, {"TELEGRAM_CHAT_ID": "chatid"}, clear=True):
    result = telegram.message("Hello")
    assert result is False

@mock.patch("rapidpro_api.telegram.logging")
def test_message_missing_chat_id(mock_logging):
  with mock.patch.dict(os.environ, {"TELEGRAM_BOT_TOKEN": "token"}, clear=True):
    result = telegram.message("Hello")
    assert result is False

@mock.patch("rapidpro_api.telegram.logging")
def test_message_exception_handling(mock_logging):
  with mock.patch.dict(os.environ, {"TELEGRAM_BOT_TOKEN": "token", "TELEGRAM_CHAT_ID": "chatid"}):
    with mock.patch("rapidpro_api.telegram.requests.post", side_effect=Exception("Network error")):
      result = telegram.message("Hello")
      assert result is False