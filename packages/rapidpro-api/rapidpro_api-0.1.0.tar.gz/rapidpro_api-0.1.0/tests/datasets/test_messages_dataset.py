import pytest
from unittest.mock import MagicMock
from rapidpro_api.datasets import MessagesDataset
from rapidpro_api.workspaces import Workspace
from rapidpro_api.datasets import BaseDataset

@pytest.fixture
def mock_workspace():
  workspace = MagicMock(spec=Workspace)
  workspace.code = "test_ws"
  workspace.host = "https://test.rapidpro.io"
  workspace.token = "test_token"
  return workspace


@pytest.fixture
def messages_dataset(mock_workspace):
  return MessagesDataset(workspace=mock_workspace, base_folder="/tmp/test_data")


def test_messages_dataset_initialization(messages_dataset, mock_workspace):
    assert messages_dataset.name == "messages"
    assert messages_dataset.workspace == mock_workspace
    assert messages_dataset.base_folder == "/tmp/test_data"
    assert messages_dataset.raw_dataset_batch_size == BaseDataset.DEFAULT_BATCH_SIZE
    assert messages_dataset.rapidpro_client_method == "get_messages"

