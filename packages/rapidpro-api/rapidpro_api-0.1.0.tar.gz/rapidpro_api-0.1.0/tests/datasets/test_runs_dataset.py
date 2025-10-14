import pytest
from unittest.mock import MagicMock
from rapidpro_api.datasets import RunsDataset
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
def runs_dataset(mock_workspace):
  return RunsDataset(workspace=mock_workspace, base_folder="/tmp/test_data")


def test_runs_dataset_initialization(runs_dataset, mock_workspace):
    assert runs_dataset.name == "runs"
    assert runs_dataset.workspace == mock_workspace
    assert runs_dataset.base_folder == "/tmp/test_data"
    assert runs_dataset.raw_dataset_batch_size == BaseDataset.DEFAULT_BATCH_SIZE
    assert runs_dataset.rapidpro_client_method == "get_runs"

