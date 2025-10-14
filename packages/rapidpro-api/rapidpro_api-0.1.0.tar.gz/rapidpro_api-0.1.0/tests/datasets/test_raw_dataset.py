
""" Test suite for the RawDataset class."""
import json
import gzip
import unittest
from unittest.mock import MagicMock
import pytest
import pandas as pd
from rapidpro_api.datasets import RawDataset  # Adjust import as needed
from fsspec.implementations.local import LocalFileSystem
from adlfs.spec import AzureBlobFileSystem

@pytest.fixture
def raw_dataset(tmp_path):
    """Creates a RawDataset instance with some sample data.
    Two partitions are created:
    - Africa: with 2 uncompressed JSON files and completed
    - Europe: with 2 gzip JSON files.
    The main dataset has 2 uncompressed JSON files and is not completed.
    The metadata files are also created for each partition and the main dataset.
    """
    ds = RawDataset("contacts", base_folder=str(tmp_path))
    (tmp_path / "contacts").mkdir(parents=True, exist_ok=True)
    # Create some files
    with open(tmp_path / "contacts" / "batch-000000001.json", "w", encoding="utf-8") as f:
        json.dump({"foo": "bar"}, f)
    with open(tmp_path / "contacts" / "batch-000000002.json", "w", encoding="utf-8") as f:
        json.dump({"foo": "baz"}, f)
    # Create metadata file
    with open(tmp_path / "contacts" / ds.metadata_filename, "w", encoding="utf-8") as f:
        json.dump({"last_batch": 2, "is_final_batch": False, "partition": None, 
                   "resume_cursor": "resume-cursor"}, f)
    # Create a partition
    (tmp_path / "contacts" / "africa").mkdir(parents=True, exist_ok=True)
    with open(tmp_path / "contacts" / "africa" / "batch-000000001.json", "w", encoding="utf-8") as f:
        json.dump({"foo": "africa"}, f)
    with open(tmp_path / "contacts" / "africa" / "batch-000000002.json", "w", encoding="utf-8") as f:
        json.dump({"foo": "africa2"}, f)
    # Create metadata file for partition
    with open(tmp_path / "contacts" / "africa" / ds.metadata_filename, "w", encoding="utf-8") as f:
        json.dump({"last_batch": 2, "is_final_batch": True, "partition": ["africa"]}, f)
    # Create another partition in which each batch is gzipped
    (tmp_path / "contacts" / "europe").mkdir(parents=True, exist_ok=True)
    with gzip.open(tmp_path / "contacts" / "europe" / "batch-000000001.gzip", "wt") as f:
        json.dump({"foo": "europe"}, f)
    with gzip.open(tmp_path / "contacts" / "europe" / "batch-000000002.gzip", "wt") as f:
        json.dump({"foo": "europe2"}, f)
    # Create metadata file for europe partition
    with open(tmp_path / "contacts" / "europe" / ds.metadata_filename, "w", encoding="utf-8") as f:
        json.dump({"last_batch": 2, "is_final_batch": True, "partition": ["europe"]}, f)
    return ds

def test_build_dataset_folder_with_trailing_slash():
      """Test build_dataset_folder with base folder ending with slash."""
      result = RawDataset.build_dataset_folder("data/", "contacts")
      assert result == "data/contacts"

def test_build_dataset_folder_without_trailing_slash():
      """Test build_dataset_folder with base folder not ending with slash."""
      result = RawDataset.build_dataset_folder("data", "contacts")
      assert result == "data/contacts"

def test_build_dataset_folder_empty_base():
      """Test build_dataset_folder with empty base folder."""
      result = RawDataset.build_dataset_folder("", "contacts")
      assert result == "/contacts"

def test_build_dataset_folder_root_path():
      """Test build_dataset_folder with root path."""
      result = RawDataset.build_dataset_folder("/", "contacts")
      assert result == "/contacts"

def test_build_dataset_folder_multiple_trailing_slashes():
      """Test build_dataset_folder with multiple trailing slashes."""
      result = RawDataset.build_dataset_folder("data///", "contacts")
      assert result == "data///contacts"

def test_build_partition_folder_none_partition():
      """Test build_partition_folder with None partition."""
      result = RawDataset.build_partition_folder("data/contacts", None)
      assert result == "data/contacts"

def test_build_partition_folder_empty_partition():
      """Test build_partition_folder with empty partition list."""
      result = RawDataset.build_partition_folder("data/contacts", [])
      assert result == "data/contacts"

def test_build_partition_folder_single_partition():
      """Test build_partition_folder with single partition."""
      result = RawDataset.build_partition_folder("data/contacts", ["africa"])
      assert result == "data/contacts/africa"

def test_build_partition_folder_multiple_partitions():
      """Test build_partition_folder with multiple partitions."""
      result = RawDataset.build_partition_folder("data/contacts", ["africa", "kenya", "nairobi"])
      assert result == "data/contacts/africa/kenya/nairobi"

def test_build_partition_folder_with_trailing_slash():
      """Test build_partition_folder with dataset folder ending with slash."""
      result = RawDataset.build_partition_folder("data/contacts/", ["africa"])
      assert result == "data/contacts//africa"

def test_build_partition_folder_nested_deep():
      """Test build_partition_folder with deeply nested partitions."""
      partitions = ["level1", "level2", "level3", "level4", "level5"]
      result = RawDataset.build_partition_folder("data/contacts", partitions)
      assert result == "data/contacts/level1/level2/level3/level4/level5"

@unittest.mock.patch("adlfs.spec.AzureBlobFileSystem")
@unittest.mock.patch("fsspec.core.url_to_fs")
def test_fs_discovery(mock_fs, mock_url_to_fs, tmp_path):
   
    """Test that the filesystem is set correctly."""
    ds = RawDataset("contacts", base_folder=str(tmp_path))
    # Check if the filesystem is set to LocalFileSystem
    assert isinstance(ds.fs, LocalFileSystem), "Filesystem should be LocalFileSystem"
    

def test_get_partition_folder_basic():
    """Test that the partition folder is constructed correctly."""
    ds = RawDataset("contacts", base_folder="data_raw")
    assert ds.get_partition_folder(["africa", "kenya"]) == "data_raw/contacts/africa/kenya"
    assert ds.get_partition_folder() == "data_raw/contacts"



def test_save_and_get_metadata_partition(tmp_path):
    ds = RawDataset("contacts", base_folder=str(tmp_path))
    (tmp_path / "contacts" / "africa").mkdir(parents=True, exist_ok=True)
    ds._save_metadata({"last_batch": 2, "is_final_batch": True, "partition": ["africa"]}, partition=["africa"])
    assert (tmp_path / "contacts" / "africa" / ds.metadata_filename).exists()


    # Check the contents of the metadata file
    with open(tmp_path / "contacts" / "africa" / ds.metadata_filename, "r", encoding="utf-8") as f:
        metadata = json.load(f)
        assert metadata["last_batch"] == 2
        assert metadata["is_final_batch"] is True
        assert metadata["partition"] == ["africa"]


    # Check the metadata retrieval
    assert ds.get_metadata(["africa"])["last_batch"] == 2
    assert ds.get_metadata(["africa"])["is_final_batch"] is True
    assert ds.get_metadata(["africa"])["partition"] == ["africa"]


def test_get_metadata_file_not_found(tmp_path):
    ds = RawDataset("contacts", base_folder=str(tmp_path))
    with pytest.raises(FileNotFoundError):
        ds.get_metadata(["africa", "kenya"])


def test_exists(tmp_path):
    ds = RawDataset("contacts", base_folder=str(tmp_path))
    (tmp_path / "contacts").mkdir(parents=True, exist_ok=True)
    assert ds.exists() is True
    assert ds.exists(["africa"]) is False
    (tmp_path / "contacts" / "africa").mkdir(parents=True, exist_ok=True)
    assert ds.exists(["africa"]) is True


def test_is_empty(tmp_path):
    ds = RawDataset("contacts", base_folder=str(tmp_path))
    (tmp_path / "contacts").mkdir(parents=True, exist_ok=True)
    assert ds.is_empty() is True
    assert ds.is_empty(["africa"]) is True
    (tmp_path / "contacts" / "africa").mkdir(parents=True, exist_ok=True)
    with open(tmp_path / "contacts" / "africa" / "batch-000000001.json", "w", encoding="utf-8") as f:
        json.dump({"foo": "bar"}, f)
    assert ds.is_empty(["africa"]) is False


def test_has_final_batch_true_false(tmp_path):
    ds = RawDataset("contacts", base_folder=str(tmp_path))
    (tmp_path / "contacts" / "africa" ).mkdir(parents=True, exist_ok=True)
    # manually create the final batch
    with open(tmp_path / "contacts" / "africa" / ds.metadata_filename, "w", encoding="utf-8") as f:
        json.dump({"last_batch": 1, "is_final_batch": True, "partition": ["africa"]}, f)
    assert ds.has_final_batch(["africa"]) is True
    # manually create a non-final batch
    with open(tmp_path / "contacts" / "africa" / ds.metadata_filename, "w", encoding="utf-8") as f:
        json.dump({"last_batch": 1, "is_final_batch": False, "partition": ["africa"]}, f)
    assert ds.has_final_batch(["africa"]) is False


def test_set_is_final_batch(tmp_path):
    ds = RawDataset("contacts", base_folder=str(tmp_path))
    (tmp_path / "contacts").mkdir(exist_ok=True)
    # manually create the final batch
    with open(tmp_path / "contacts" / ds.metadata_filename, "w", encoding="utf-8") as f:
        json.dump({"last_batch": 1, "is_final_batch": False, "partition": []}, f)
    ds.set_is_final_batch(True)
    with open(tmp_path / "contacts" / ds.metadata_filename, "r", encoding="utf-8") as f:
        metadata = json.load(f)
        assert metadata["is_final_batch"] is True


def test_set_is_final_batch_with_partition(tmp_path):
  ds = RawDataset("contacts", base_folder=str(tmp_path))
  (tmp_path / "contacts" / 'africa').mkdir(parents=True, exist_ok=True)
  # manually create the final batch
  with open(tmp_path / "contacts" / "africa" / ds.metadata_filename, "w") as f:
    json.dump({"last_batch": 1, "is_final_batch": False, "partition": ["africa"]}, f)
  ds.set_is_final_batch(True, ["africa"])
  with open(tmp_path / "contacts" / "africa" / ds.metadata_filename, "r") as f:
    metadata = json.load(f)
    assert metadata["is_final_batch"] is True


def test_set_is_final_batch_file_not_found(tmp_path):
  ds = RawDataset("contacts", base_folder=str(tmp_path))
  (tmp_path / "contacts").mkdir(exist_ok=True)
  with pytest.raises(FileNotFoundError):
    ds.set_is_final_batch(True)


def test_get_last_batch_number_empty(tmp_path):
  ds = RawDataset("contacts", base_folder=str(tmp_path))
  assert ds.get_last_batch_number(["africa"]) == 0
  # Now we create the partition folder 
  (tmp_path / "contacts" / 'africa').mkdir(parents=True, exist_ok=True)
  assert ds.get_last_batch_number(["africa"]) == 0


def test_append_save_creates_file_and_metadata(tmp_path):
  ds = RawDataset("contacts", base_folder=str(tmp_path))
  ds.append_save({"foo": "bar"}, zip=False)
  assert (tmp_path / "contacts" / "batch-000000001.json").exists()
  assert (tmp_path / "contacts" / ds.metadata_filename).exists()
  # Check the contents of the metadata file
  with open(tmp_path / "contacts" / ds.metadata_filename, "r") as f:
    metadata = json.load(f)
    assert metadata["last_batch"] == 1
    assert metadata["is_final_batch"] is False
    assert metadata["partition"] is None

  # Check the cursor is added
  ds.append_save({"foo": "bar"}, zip=False, resume_cursor="asdfghjkl")
  with open(tmp_path / "contacts" / ds.metadata_filename, "r") as f:
    metadata = json.load(f)
    assert metadata["last_batch"] == 2
    assert metadata["is_final_batch"] is False
    assert metadata["partition"] is None
    assert metadata["resume_cursor"] == "asdfghjkl"
  
  # Add a new final batch
  ds.append_save({"foo": "bar"}, zip=False, is_final_batch=True)
  assert (tmp_path / "contacts" / "batch-000000003.json").exists()
  assert (tmp_path / "contacts" / ds.metadata_filename).exists()
  
  # Check the contents of the metadata file
  with open(tmp_path / "contacts" / ds.metadata_filename, "r") as f:
    metadata = json.load(f)
    assert metadata["last_batch"] == 3
    assert metadata["is_final_batch"] is True
    assert metadata["partition"] is None
    assert metadata["resume_cursor"] is None  # No cursor after final batch


def test_append_save_creates_file_and_metadata_with_partition(tmp_path):
  # Now with a partition
   ds = RawDataset("contacts", base_folder=str(tmp_path))
   ds.append_save({"foo": "bar"}, partition=["africa"], zip=False)
   assert (tmp_path / "contacts" / "africa" / "batch-000000001.json").exists()
   assert (tmp_path / "contacts" / "africa" / ds.metadata_filename).exists()


def test_append_save_gzip(tmp_path):
  ds = RawDataset("contacts", base_folder=str(tmp_path))
  ds.append_save({"foo": "bar"}, zip=True)
  assert (tmp_path / "contacts" / "batch-000000001.gzip").exists()
  assert (tmp_path / "contacts" / ds.metadata_filename).exists()
  # Now with a partition
  ds.append_save({"foo": "bar"}, partition=["africa"], zip=True)
  assert (tmp_path / "contacts" / "africa" / "batch-000000001.gzip").exists()
  assert (tmp_path / "contacts" / "africa" / ds.metadata_filename).exists()


def test_clear_removes_folder(tmp_path):
  ds = RawDataset("contacts", base_folder=str(tmp_path))
  # create the partition we're going to delete
  (tmp_path / "contacts" / "africa").mkdir(parents=True, exist_ok=True)
  # add some data to the folder
  with open(tmp_path / "contacts" / "africa" / "batch-000000001.json", "w") as f:
    json.dump({"foo": "bar"}, f)
  # add metadata to the folder
  with open(tmp_path / "contacts" / "africa" / ds.metadata_filename, "w") as f:
    json.dump({"last_batch": 1, "is_final_batch": False, "partition": ["africa"]}, f)
  
  # Create the another partition to ensure it does not get deleted
  (tmp_path / "contacts" / "europe").mkdir(parents=True, exist_ok=True)
  with open(tmp_path / "contacts" / "europe" / "batch-000000001.json", "w") as f:
    json.dump({"foo": "bar"}, f)
  with open(tmp_path / "contacts" / "europe" / ds.metadata_filename, "w") as f:
    json.dump({"last_batch": 1, "is_final_batch": False, "partition": ["africa"]}, f)
  #
  #  Add some metadata to the root folder
  with open(tmp_path / "contacts" / ds.metadata_filename, "w") as f:
    json.dump({"last_batch": 1, "is_final_batch": False, "partition": None}, f)
  
  ds.clear(["africa"])
  assert not (tmp_path / "contacts" / "africa").exists()
  # check it did not remove the other stuff
  assert (tmp_path / "contacts" / "europe" / "batch-000000001.json").exists()
  assert (tmp_path / "contacts" / "europe").exists()
  assert (tmp_path / "contacts" / ds.metadata_filename).exists()


def test_clear_many_partitions(tmp_path):
  ds = RawDataset("contacts", base_folder=str(tmp_path))
  # create the partition we're going to delete
  (tmp_path / "contacts" / "africa").mkdir(parents=True, exist_ok=True)
  (tmp_path / "contacts" / "africa" / "batch-000000001.json").write_text("foo")

  (tmp_path / "contacts" / "europe").mkdir(parents=True, exist_ok=True)
  (tmp_path / "contacts" / "europe" / "batch-000000001.json").write_text("foo")
  
  (tmp_path / "contacts" / "keep").mkdir(parents=True, exist_ok=True)
  (tmp_path / "contacts" / "keep" / "batch-000000001.json").write_text("foo")
  
  # Now delete africa and europe  
  ds.clear_many_partitions([["africa"], ["europe"]]) 
  assert not (tmp_path / "contacts" / "africa").exists()
  assert not (tmp_path / "contacts" / "europe").exists()
  # check it did not remove the other stuff
  assert (tmp_path / "contacts" / "keep" / "batch-000000001.json").exists()


def test_files_file_not_found(tmp_path):
  ds = RawDataset("contacts", base_folder=str(tmp_path))
  ds.append_save({"foo": "bar"}, zip=False)
  with pytest.raises(FileNotFoundError):
    ds.files(["africa"])


def test_files(raw_dataset):
  files = raw_dataset.files()
  assert not isinstance(files, pd.DataFrame)
  assert len(files) == 6
  assert all(key in files[0] for key in ["dataset_name", "path", "partition", "partition_path", "dataset_path", "zip", "filesize"])
  files = raw_dataset.files(["africa"])
  assert not isinstance(files, pd.DataFrame)
  assert len(files) == 2
  # ensure the keys are correct
  assert all(key in files[0] for key in ["dataset_name", "level1", "path", "partition", "partition_path", "dataset_path", "zip", "filesize"])
  assert files[0]["level1"] is "africa"  
  assert files[0]["dataset_name"] == "contacts"
  assert files[0]['dataset_path'] == "/contacts/"
  assert files[0]["path"].endswith("contacts/africa/batch-000000001.json")
  assert files[0]["zip"] is False
  assert files[0]["partition"] == ["africa"] 
  assert files[0]["partition_path"] == "/contacts/africa"
  assert files[0]["filesize"] > 0


def test_files_as_dataframe(raw_dataset):
  files = raw_dataset.files(as_dataframe=True)
  assert isinstance(files, pd.DataFrame)
  assert len(files) == 6
  files = raw_dataset.files(["africa"], as_dataframe=True)
  assert isinstance(files, pd.DataFrame)
  assert len(files) == 2


def test_partitions(raw_dataset):
  partitions = raw_dataset.partitions()
  assert isinstance(partitions, list)
  assert len(partitions) == 3
  
def test_partitions_as_dataframe(raw_dataset):
  partitions = raw_dataset.partitions(as_dataframe=True)
  assert isinstance(partitions, pd.DataFrame)
  assert len(partitions) == 3


def test_get_file_data_json(tmp_path):
  ds = RawDataset("contacts", base_folder=str(tmp_path))
  file_path = tmp_path / "contacts" / "batch-000000001.json"
  (tmp_path / "contacts").mkdir(exist_ok=True)
  with open(file_path, "w") as f:
    json.dump({"foo": "bar"}, f)
  data = ds.get_file_data(str(file_path))
  assert data["foo"] == "bar"


def test_get_file_data_gzip(tmp_path):
  ds = RawDataset("contacts", base_folder=str(tmp_path))
  file_path = tmp_path / "contacts" / "batch-000000001.gzip"
  (tmp_path / "contacts").mkdir(exist_ok=True)
  with gzip.open(file_path, "wb") as f:
    f.write(json.dumps({"foo": "bar"}).encode("utf-8"))
  data = ds.get_file_data(str(file_path))
  assert data["foo"] == "bar"


def test_get_file_data_file_not_found(tmp_path):
  ds = RawDataset("contacts", base_folder=str(tmp_path))
  with pytest.raises(FileNotFoundError):
    ds.get_file_data("notfound.json")