import pytest
from unittest.mock import MagicMock
from rapidpro_api.datasets import ContactsDataset
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
def contacts_dataset(mock_workspace):
  return ContactsDataset(workspace=mock_workspace, base_folder="/tmp/test_data")


def test_contacts_dataset_initialization(contacts_dataset, mock_workspace):
    assert contacts_dataset.name == "contacts"
    assert contacts_dataset.workspace == mock_workspace
    assert contacts_dataset.base_folder == "/tmp/test_data"
    assert contacts_dataset.raw_dataset_batch_size == BaseDataset.DEFAULT_BATCH_SIZE
    assert contacts_dataset.rapidpro_client_method == "get_contacts"

