import pytest
from unittest.mock import MagicMock
from rapidpro_api.datasets import GroupsDataset
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
def groups_dataset(mock_workspace):
  return GroupsDataset(workspace=mock_workspace, base_folder="/tmp/test_data")


def test_groups_dataset_initialization(groups_dataset, mock_workspace):
    assert groups_dataset.name == "groups"
    assert groups_dataset.workspace == mock_workspace
    assert groups_dataset.base_folder == "/tmp/test_data"
    assert groups_dataset.raw_dataset_batch_size == BaseDataset.DEFAULT_BATCH_SIZE
    assert groups_dataset.rapidpro_client_method == "get_groups"

