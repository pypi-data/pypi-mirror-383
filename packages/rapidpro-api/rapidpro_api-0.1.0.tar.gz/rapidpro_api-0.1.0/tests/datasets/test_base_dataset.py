import pytest
import pandas as pd
import json
import os
import gzip
from pathlib import Path
from unittest.mock import MagicMock, patch
from datetime import datetime
from freezegun import freeze_time

from rapidpro_api.datasets import BaseDataset
from rapidpro_api.workspaces import Workspace
from datetime import datetime, timedelta

@pytest.fixture
def mock_workspace():
    workspace = MagicMock(spec=Workspace)
    workspace.code = "test_ws"
    workspace.host = "https://test.rapidpro.io"
    workspace.token = "test_token"
    workspace.vendor = "test_vendor"
    return workspace


@pytest.fixture
def base_dataset(mock_workspace, tmp_path):
    return BaseDataset("contacts", workspace=mock_workspace, base_folder=str(tmp_path))

@pytest.fixture
def mock_rapidpro_client():
    item = MagicMock()
    item.serialize = MagicMock(return_value={"uuid": "123", "name": "Test rapidpro item"})
    return_iter = [item] * 10  # Simulate 10 items returned by the client

    get_contacts_return = MagicMock()
    get_contacts_return.iterfetches = MagicMock(return_value = return_iter)

    client = MagicMock()
    client.get_contacts = MagicMock(return_value=get_contacts_return)
    client.get_contacts.iterfetches = iter(return_iter)
    return client

def test_init(mock_workspace, tmp_path):
    ds = BaseDataset("contacts", workspace=mock_workspace, base_folder=str(tmp_path))
    assert ds.name == "contacts"
    assert ds.workspace == mock_workspace
    assert ds.base_folder == str(tmp_path) 
    assert ds.dataset_base_folder == f"{str(tmp_path)}/contacts"
    assert ds.rapidpro_client_method == "get_contacts"
    assert ds.raw_dataset_batch_size == BaseDataset.DEFAULT_BATCH_SIZE



def test_init_custom_batch_size(mock_workspace, tmp_path):
  ds = BaseDataset("contacts", workspace=mock_workspace, base_folder=str(tmp_path), raw_dataset_batch_size=5000)
  assert ds.raw_dataset_batch_size == 5000

def test_init_none_batch_size(mock_workspace, tmp_path):
  ds = BaseDataset("contacts", workspace=mock_workspace, base_folder=str(tmp_path), raw_dataset_batch_size=None)
  assert ds.raw_dataset_batch_size == BaseDataset.DEFAULT_BATCH_SIZE


def test_str_repr(mock_workspace, tmp_path):
  base_dataset = BaseDataset("contacts", workspace=mock_workspace, base_folder=str(tmp_path))
  expected = f"BaseDataset(contacts, {base_dataset.workspace.code}, {str(tmp_path)}, {base_dataset.raw_dataset_batch_size}, get_contacts)"
  assert str(base_dataset) == expected
  assert repr(base_dataset) == expected

def test_is_valid_ws_partition(base_dataset):
  # Test valid partition
  assert base_dataset._is_valid_ws_partition(ws_partition=None) is True
  assert base_dataset._is_valid_ws_partition([]) is True
  assert base_dataset._is_valid_ws_partition(["2023"]) is True
  assert base_dataset._is_valid_ws_partition(["2023", "2024"]) is False
  assert base_dataset._is_valid_ws_partition(["2023", "2023-01-01"]) is True
  # # first one is not a year
  assert base_dataset._is_valid_ws_partition(["invalid_ws"]) is False
  # Second one is not a yyyy-mm-dd
  assert base_dataset._is_valid_ws_partition(["2023", "invalid_ws"]) is False
  # 3 elements is not 
  assert base_dataset._is_valid_ws_partition(["2023", "2023-01-01", "X"]) is False
  

def test_raw_dataset_files_raises_exceptions(base_dataset):

  # Test with invalid partition (ValueError)
  with pytest.raises(ValueError):
    base_dataset.raw_dataset_files(ws_partition=["invalid_partition"])

  # Test when folder does not exist (FileNotFoundError)
  with pytest.raises(FileNotFoundError):
    base_dataset.raw_dataset_files()

  # Test when folder exists but no files (FileNotFoundError)
  (Path(base_dataset.base_folder) / "contacts" / "raw" / "test_ws").mkdir(parents=True, exist_ok=True)
  assert base_dataset.raw_dataset_files() == []


def test_add_ws_to_partition(base_dataset):
  # test with None partition
  result = base_dataset._add_ws_to_partition(None)
  assert result == ["test_ws"]

  # Test with empty partition
  result = base_dataset._add_ws_to_partition([])
  assert result == ["test_ws"]

  # Test with existing partition
  result = base_dataset._add_ws_to_partition(["2023"])
  assert result == ["test_ws", "2023"]

  # Test with multiple partitions
  result = base_dataset._add_ws_to_partition(["2023", "2024-01-01"])
  assert result == ["test_ws", "2023", "2024-01-01"]

def test_raw_dataset_files_no_partition(base_dataset):
  # Create the folder
  (Path(base_dataset.base_folder) / "contacts" / "raw" / "test_ws").mkdir(parents=True, exist_ok=True)
  # Add some test files
  temp_file = Path(base_dataset.base_folder) / "contacts" / "raw" / "test_ws" / "file1.json"
  temp_file.write_text('{"key": "value"}')
  temp_file2 = Path(base_dataset.base_folder) / "contacts" / "raw" / "test_ws" / "file2.json"
  temp_file2.write_text('{"key": "value"}')

  result = base_dataset.raw_dataset_files(as_dataframe=False)
  assert len(result) == 2

  (Path(base_dataset.base_folder) / "contacts" / "raw" / "test_ws").mkdir(parents=True, exist_ok=True)
  # Create some test files
  temp_file = Path(base_dataset.base_folder) / "contacts" / "raw" / "test_ws" / "file1.json"
  temp_file.write_text('{"key": "value"}')
  temp_file2 = Path(base_dataset.base_folder) / "contacts" / "raw" / "test_ws" / "file2.json"
  temp_file2.write_text('{"key": "value"}')

  result = base_dataset.raw_dataset_files(as_dataframe=False)
  assert len(result) == 2

def test_raw_dataset_files_with_partition(base_dataset):
  #Create the folder for the dataset
  (Path(base_dataset.base_folder) / "contacts" / "raw" / "test_ws" / "2023" / "2023-10-20").mkdir(parents=True, exist_ok=True)
  # Create some test files
  temp_file = Path(base_dataset.base_folder) / "contacts" / "raw" / "test_ws" / "2023" / "2023-10-20" / "file1.json"
  temp_file.write_text('{"key": "value"}')
  temp_file2 = Path(base_dataset.base_folder) / "contacts" / "raw" / "test_ws" / "2023" / "2023-10-20" / "file2.json"
  temp_file2.write_text('{"key": "value"}')

  result = base_dataset.raw_dataset_files(as_dataframe=False)
  assert len(result) == 2


def test_raw_dataset_files_as_dataframe(base_dataset):  
  # Create the folder for the dataset
  (Path(base_dataset.base_folder) / "contacts" / "raw" / "test_ws").mkdir(parents=True, exist_ok=True)
  result = base_dataset.raw_dataset_files(as_dataframe=True)
  assert type(result) == pd.DataFrame


def test_get_last_downloaded_date_no_metadata(base_dataset):
    assert base_dataset.get_last_downloaded_date() is None


@patch('rapidpro_api.datasets.RawDataset.RawDataset.files')
def test_get_last_downloaded_date(mock_files, base_dataset):
  files = [
    {"name": "raw", "level1": "test_ws", "level2": "2023", "level3": "2023-10-01", "path": "file1.json"}
  ]
  mock_files.return_value = pd.DataFrame(files)
  
  result = base_dataset.get_last_downloaded_date()
  
  assert result == datetime(2023, 10, 1, 0, 0, 0)
  mock_files.assert_called_once_with(partition=["test_ws"],as_dataframe=True)


@patch('rapidpro_api.datasets.RawDataset.RawDataset.files')
def test_get_last_downloaded_date_with_partition(mock_files, base_dataset):
  files = [
    {"name": "raw", "level1": "test_ws", "level2": "2023", "level3": "2023-10-01", "path": "file1.json"}
  ]
  mock_files.return_value = pd.DataFrame(files)
    
  result = base_dataset.get_last_downloaded_date(ws_partition=["2023"])
  
  assert result == datetime(2023, 10, 1, 0, 0, 0)
  mock_files.assert_called_once_with(partition=["test_ws", "2023"], as_dataframe=True)



@patch.object(BaseDataset, '_downloader')
@patch.object(BaseDataset, 'get_last_downloaded_date')
def test_download_dated_dataset_with_last_date_none(mock_get_last, mock_downloader, base_dataset):
  # Mock the last downloaded date to 2023-10-01 
  mock_get_last.return_value = None
  with freeze_time("2014-1-31"):
    base_dataset.download_dated_dataset(continue_if_exists=True)
    # mock_downloader is called 10 times (10-1,10-2,10-3.. 10-09, 10-10)
    # by default it loads till the previous day
    assert mock_downloader.call_count == 30
    _, kwargs1 = mock_downloader.call_args_list[0]
    assert kwargs1.get('rapidpro_client_kwargs').get('after') == BaseDataset.INIT_DATE.strftime("%Y-%m-%d") + "T00:00:00Z"
    assert kwargs1.get('rapidpro_client_kwargs').get('before') == BaseDataset.INIT_DATE.strftime("%Y-%m-%d") + "T23:59:59Z"

    _, kwargs29 = mock_downloader.call_args_list[29]
    assert kwargs29.get('rapidpro_client_kwargs').get('after')  == datetime(2014, 1, 30, 0, 0).strftime("%Y-%m-%d") + "T00:00:00Z"
    assert kwargs29.get('rapidpro_client_kwargs').get('before')  == datetime(2014, 1, 30, 23, 59, 59).strftime("%Y-%m-%d") + "T23:59:59Z"

@patch.object(BaseDataset, '_downloader')
@patch.object(BaseDataset, 'get_last_downloaded_date')
def test_download_dated_dataset_no_continue(mock_get_last, mock_downloader, base_dataset):
  mock_get_last.return_value = datetime(2023, 10, 1, 0, 0, 0)
  with freeze_time("2014-1-31"):
    # it will use this date as first date for download regardless of the last downloaded date.
    after_date = datetime(2014, 1, 2)
    base_dataset.download_dated_dataset(after_date=after_date, continue_if_exists=False)
    # mock_downloader is called 10 times (10-1,10-2,10-3.. 10-09, 10-10)
    # by default it loads till the previous day
    assert mock_downloader.call_count == 29
    _, kwargs1 = mock_downloader.call_args_list[0]
    assert kwargs1.get('rapidpro_client_kwargs').get('after') == after_date.strftime("%Y-%m-%d") + "T00:00:00Z"
    assert kwargs1.get('rapidpro_client_kwargs').get('before') == after_date.strftime("%Y-%m-%d") + "T23:59:59Z"

    _, kwargs29 = mock_downloader.call_args_list[28]
    assert kwargs29.get('rapidpro_client_kwargs').get('after')  == datetime(2014, 1, 30, 0, 0).strftime("%Y-%m-%d") + "T00:00:00Z"
    assert kwargs29.get('rapidpro_client_kwargs').get('before')  == datetime(2014, 1, 30, 23, 59, 59).strftime("%Y-%m-%d") + "T23:59:59Z"

@patch.object(BaseDataset, '_downloader')
@patch.object(BaseDataset, 'get_last_downloaded_date')
def test_download_dated_dataset_value_error(mock_get_last, mock_downloader, base_dataset):
  mock_get_last.return_value = datetime(2023, 10, 1, 0, 0, 0)
  with freeze_time("2014-1-31"):
    # it will use this date as first date for download regardless of the last downloaded date.
    after_date = datetime(2015, 1, 2)
    before_date = datetime(2014, 1, 2)
    # This will raise the value error because after_date is posterior to the before_date  
    with pytest.raises(ValueError):
      base_dataset.download_dated_dataset(after_date=after_date, before_date=before_date, continue_if_exists=False)
    # This will raise the value error because last_downloaded_date is after the before_date
    with pytest.raises(ValueError):
      base_dataset.download_dated_dataset(after_date=None, before_date=before_date, continue_if_exists=True)


@patch.object(BaseDataset, '_downloader')
@patch.object(BaseDataset, 'get_last_downloaded_date')
def test_download_dated_dataset_continue(mock_get_last, mock_downloader, base_dataset):
  # Mock the last downloaded date to 2023-10-01 
  mock_get_last.return_value = datetime(2023, 10, 1, 0, 0, 0)
  # Mock the current date to 11 days after the last downloaded date
  with freeze_time("2023-10-11"):
    base_dataset.download_dated_dataset(continue_if_exists=True)
    # mock_downloader is called 10 times (10-1,10-2,10-3.. 10-09, 10-10)
    # by default it loads till the previous day
    assert mock_downloader.call_count == 10 
    _, kwargs1 = mock_downloader.call_args_list[0]
    assert kwargs1.get('rapidpro_client_kwargs').get('after') == datetime(2023, 10, 1, 0, 0).strftime("%Y-%m-%d") + "T00:00:00Z"
    assert kwargs1.get('rapidpro_client_kwargs').get('before') == datetime(2023, 10, 1, 23, 59, 59).strftime("%Y-%m-%d") + "T23:59:59Z"

    _, kwargs9 = mock_downloader.call_args_list[9]
    assert kwargs9.get('rapidpro_client_kwargs').get('after')  == datetime(2023, 10, 10, 0, 0).strftime("%Y-%m-%d") + "T00:00:00Z"
    assert kwargs9.get('rapidpro_client_kwargs').get('before')  == datetime(2023, 10, 10, 23, 59, 59).strftime("%Y-%m-%d") + "T23:59:59Z"
    

@patch.object(BaseDataset, '_downloader')
def test_download_dated_dataset_with_before_date(mock_downloader, base_dataset):
  after_date = datetime.strptime("2023-10-01", "%Y-%m-%d")
  before_date = datetime.strptime("2023-10-31", "%Y-%m-%d")
  
  base_dataset.download_dated_dataset(continue_if_exists=False, after_date=after_date, before_date=before_date)
  
  assert mock_downloader.call_count == 31 # 1 to 31 of October  
  _, kwargs1 = mock_downloader.call_args_list[0]
  _, kwargs31 = mock_downloader.call_args_list[30]

  assert kwargs1.get('rapidpro_client_kwargs').get('after') == datetime(2023, 10, 1, 0, 0).strftime("%Y-%m-%d") + "T00:00:00Z"
  assert kwargs1.get('rapidpro_client_kwargs').get('before') == datetime(2023, 10, 1, 0, 0).strftime("%Y-%m-%d") + "T23:59:59Z"

  assert kwargs31.get('rapidpro_client_kwargs').get('after') == datetime(2023, 10, 31, 0, 0).strftime("%Y-%m-%d") + "T00:00:00Z"
  assert kwargs31.get('rapidpro_client_kwargs').get('before') == datetime(2023, 10, 31, 23, 59, 59).strftime("%Y-%m-%d") + "T23:59:59Z"

@patch.object(BaseDataset, '_downloader')
def test_download_full_dataset(mock_downloader, base_dataset):
  
  with freeze_time("2023-10-01"):
    base_dataset.download_full_dataset()
    mock_downloader.assert_called_once_with(
      ws_partition=["2023", "2023-10-01"],
      clear=False,
      continue_if_exists=False
    )

@patch.object(BaseDataset, '_downloader')
def test_download_full_dataset_with_trues(mock_downloader, base_dataset):
  
  with freeze_time("2023-10-01"):
    base_dataset.download_full_dataset(clear=True, continue_if_exists=True)
    mock_downloader.assert_called_once_with(
      ws_partition=["2023", "2023-10-01"],
      clear=True,
      continue_if_exists=True
    )


@patch('rapidpro_api.datasets.RawDataset.RawDataset.clear')
def test_downloader_basic(mock_clear, base_dataset):
  # Setup mock data and client response
  mock_item1 = MagicMock()
  mock_item2 = MagicMock()
  mock_response = MagicMock()
  mock_response.__iter__ = lambda self=None: iter([mock_item1, mock_item2])
  # Mock the client method
  base_dataset.rapidpro_client.get_contacts = MagicMock(return_value=mock_response)
  base_dataset._downloader(
    ws_partition=["2023"],
    clear=True,
    rapidpro_client_method="get_contacts"
  )
  # The partition does not exist => clear not called
  mock_clear.assert_not_called()
  base_dataset.rapidpro_client.get_contacts.assert_called_once()


@patch('rapidpro_api.datasets.RawDataset.RawDataset.clear')
def test_downloader_with_kwargs(mock_clear, base_dataset):
  # Setup mock data and client response
  mock_item1 = MagicMock()
  mock_item2 = MagicMock()
  mock_response = MagicMock()
  mock_response.__iter__.return_value = [mock_item1, mock_item2]
  
  # Mock the client method
  base_dataset.rapidpro_client.get_contacts = MagicMock(return_value=mock_response)
  
  after_date = datetime.strptime("2023-10-01", "%Y-%m-%d")
  before_date = datetime.strptime("2023-10-31", "%Y-%m-%d")
  
  base_dataset._downloader(
    ws_partition=["2023"],
    clear=False,
    rapidpro_client_kwargs={'after_date':after_date, 'before_date':before_date},
  )
  mock_clear.assert_not_called()
  base_dataset.rapidpro_client.get_contacts.assert_called_once_with(after_date=after_date, before_date=before_date)

@patch('rapidpro_api.datasets.RawDataset.RawDataset.is_empty')
@patch('rapidpro_api.datasets.RawDataset.RawDataset.clear')
@patch('rapidpro_api.datasets.RawDataset.RawDataset.append_save')
def test_downloader_no_data(mock_append_save, mock_clear, mock_empty, base_dataset):
  # Setup mock empty response
  mock_response = MagicMock()
  mock_response.__iter__.return_value = []
  mock_empty.return_value = False

  # Mock the client method
  base_dataset.rapidpro_client.get_contacts = MagicMock(return_value=mock_response)
  base_dataset._downloader(ws_partition=None, clear=True)
  mock_empty.assert_called_once()
  mock_clear.assert_called_once_with(partition=["test_ws"])
  mock_append_save.assert_not_called()

# test downloader with continue_if_exists
@patch('rapidpro_api.datasets.RawDataset.RawDataset.is_empty')
@patch('rapidpro_api.datasets.RawDataset.RawDataset.clear')
@patch('rapidpro_api.datasets.RawDataset.RawDataset.append_save')
@patch('rapidpro_api.datasets.RawDataset.RawDataset.get_metadata')
def test_downloader_continue_if_exists(mock_get_metadata, mock_rapidpro_client, mock_clear, mock_empty, base_dataset):
  
  # Mock is_empty to return False
  mock_empty.return_value = False

  # Mock get_metadata to simulate resume
  mock_get_metadata.return_value = {
    "last_batch": False,
    "resume_cursor": "test_cursor"
  }
  base_dataset.rapidpro_client = mock_rapidpro_client
  base_dataset._downloader(ws_partition=None, clear=False, continue_if_exists=True)

  mock_empty.assert_called_once()
  mock_clear.assert_not_called()
  assert mock_get_metadata.call_count == 2 # one for has_last_batch and one for resume_cursor
  mock_get_metadata.assert_any_call(partition=["test_ws"])
  base_dataset.rapidpro_client.get_contacts.assert_called_once()

  base_dataset.rapidpro_client.get_contacts().iterfetches.assert_called_once()
  # Check that resume_cursor is passed in the call
  called_kwargs = base_dataset.rapidpro_client.get_contacts().iterfetches.call_args.kwargs
  assert called_kwargs.get("resume_cursor") == "test_cursor"


@patch('rapidpro_api.datasets.RawDataset.RawDataset.is_empty')
@patch('rapidpro_api.datasets.RawDataset.RawDataset.clear')
@patch('rapidpro_api.datasets.RawDataset.RawDataset.append_save')
@patch('rapidpro_api.datasets.RawDataset.RawDataset.get_metadata')
def test_downloader_continue_if_exists_no_cursor(mock_get_metadata, mock_rapidpro_client, mock_clear, mock_empty, base_dataset):

  # Mock is_empty to return False
  mock_empty.return_value = False
  mock_get_metadata.return_value = {
    "last_batch": False,
  }
  base_dataset.rapidpro_client = mock_rapidpro_client
  base_dataset._downloader(ws_partition=None, clear=False, continue_if_exists=True)

  mock_empty.assert_called_once()
  mock_clear.assert_called_once()
  assert mock_get_metadata.call_count == 2 # one for has_last_batch and one for resume_cursor
  mock_get_metadata.assert_any_call(partition=["test_ws"])
  base_dataset.rapidpro_client.get_contacts.assert_called_once()

  base_dataset.rapidpro_client.get_contacts().iterfetches.assert_called_once()
  # Check that resume_cursor is passed in the call
  called_kwargs = base_dataset.rapidpro_client.get_contacts().iterfetches.call_args.kwargs
  assert called_kwargs.get("resume_cursor") == None




@patch('rapidpro_api.datasets.RawDataset.RawDataset.is_empty')
@patch('rapidpro_api.datasets.RawDataset.RawDataset.clear')
@patch('rapidpro_api.datasets.RawDataset.RawDataset.append_save')
def test_downloader_continue_if_exists_empty(mock_append_save, mock_clear, mock_empty, base_dataset):
    # Setup mock empty response
    mock_response = MagicMock()
    mock_response.__iter__ = lambda self=None: iter([])

    # Mock the client method
    base_dataset.rapidpro_client.get_contacts = MagicMock(return_value=mock_response)

    # Mock is_empty to return True
    mock_empty.return_value = True

    base_dataset._downloader(ws_partition=None, clear=False, continue_if_exists=True)

    mock_empty.assert_called_once()
    mock_clear.assert_not_called()
    mock_append_save.assert_not_called()


@pytest.fixture
def base_dataset_with_files(base_dataset):
    # Create a structure with dated files
    base = Path(base_dataset.base_folder) / "contacts" / "raw" / "test_ws"
    (base / "2023" / "2023-10-01").mkdir(parents=True, exist_ok=True)
    (base / "2023" / "2023-10-02").mkdir(parents=True, exist_ok=True)
    (base / "2023" / "2023-10-03").mkdir(parents=True, exist_ok=True)
    (base / "2023" / "2023-10-01" / "batch-000000001.json").write_text('[{"date": "2023-10-01", "val": 1}]')
    (base / "2023" / "2023-10-02" / "batch-000000002.json").write_text('[{"date": "2023-10-02", "val": 2}]')
    (base / "2023" / "2023-10-03" / "batch-000000003.json").write_text('[{"date": "2023-10-03", "val": 3}]')
    (base / "2023" / "2023-10-03" / "00_metadata.json").write_text('{"last_batch": 3}')
    return base_dataset

def test_iter_dated_batch_raw_files_basic(base_dataset_with_files):
    # Should yield batches of files for each date
    batches = list(base_dataset_with_files.iter_dated_batch_raw_files())
    assert len(batches) == 3
    # Each batch should be a list of file paths
    for batch in batches:
        assert isinstance(batch, list)
        assert len(batch) == 1

def test_iter_dated_batch_raw_files_empty_workspace(base_dataset):
    # If the workspace does not exist, should yield error
    with pytest.raises(FileNotFoundError):
        list(base_dataset.iter_dated_batch_raw_files())
    # if the workspace exists, but it is empty, should yield nothing
    base = Path(base_dataset.base_folder) / "contacts" / "raw" / "test_ws"
    base.mkdir(parents=True, exist_ok=True)
    batches = list(base_dataset.iter_dated_batch_raw_files())
    assert batches == []

def test_iter_dated_batch_raw_files_with_date_range(base_dataset_with_files):
    # Only files in the date range should be yielded
    after = datetime(2023, 10, 2)
    before = datetime(2023, 10, 3)
    batches = list(base_dataset_with_files.iter_dated_batch_raw_files(after_date=after, before_date=before))
    assert len(batches) == 2
    

def test_iter_dated_batch_raw_files_corner_dates(base_dataset_with_files):
    # after_date after all files, yields nothing
    after = datetime(2023, 10, 10)
    batches = list(base_dataset_with_files.iter_dated_batch_raw_files(after_date=after))
    assert batches == []
    # before_date before all files, yields nothing
    before = datetime(2023, 9, 30)
    batches = list(base_dataset_with_files.iter_dated_batch_raw_files(before_date=before))
    assert batches == []


def test_iter_dated_batch_raw_files_with_file_info(base_dataset_with_files):
    # Should yield file info with date and value
    file_info_list = []
    raw_data_list = []
    for file_info, raw_data in base_dataset_with_files.iter_dated_batch_raw_files(with_file_info=True):
        file_info_list.append(file_info)
        raw_data_list.append(raw_data)
    assert len(file_info_list) == 3
    assert len(raw_data_list) == 3  
    # now check the content of the first file
    first_file_info = file_info_list[0]
    first_raw_data = raw_data_list[0]
    assert first_file_info['filename'] == "batch-000000001.json"
    assert isinstance(first_raw_data, list)


def test_iter_last_date_raw_files_basic(base_dataset_with_files):
    # Should yield files only for the last date
    batches = list(base_dataset_with_files.iter_last_date_raw_files())
    assert len(batches) == 1
    assert batches[0][0]["val"] == 3 



def test_iter_last_date_raw_files_with_file_info(base_dataset_with_files):

    # Should yield file info with date and value for the last date
    file_info_list = []
    raw_data_list = []
    for file_info, raw_data in base_dataset_with_files.iter_last_date_raw_files(with_file_info=True):
        file_info_list.append(file_info)
        raw_data_list.append(raw_data)
    assert len(file_info_list) == 1
    assert len(raw_data_list) == 1  
    # now check the content of the first file
    first_file_info = file_info_list[0]
    first_raw_data = raw_data_list[0]
    assert first_file_info['filename'] == "batch-000000003.json"
    assert isinstance(first_raw_data, list)
    assert first_raw_data[0]["val"] == 3  # Check the value in