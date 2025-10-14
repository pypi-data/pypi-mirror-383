import pytest
from unittest.mock import MagicMock
from rapidpro_api.datasets import FlowsDataset
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
def flows_dataset(mock_workspace):
  return FlowsDataset(workspace=mock_workspace, base_folder="/tmp/test_data")


def test_flows_dataset_initialization(flows_dataset, mock_workspace):
    assert flows_dataset.name == "flows"
    assert flows_dataset.workspace == mock_workspace
    assert flows_dataset.base_folder == "/tmp/test_data"
    assert flows_dataset.raw_dataset_batch_size == BaseDataset.DEFAULT_BATCH_SIZE
    assert flows_dataset.rapidpro_client_method == "get_flows"

