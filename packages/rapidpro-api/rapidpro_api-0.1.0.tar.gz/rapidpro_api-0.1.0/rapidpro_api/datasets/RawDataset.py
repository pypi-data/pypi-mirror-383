import json
import gzip
from fsspec.implementations.local import LocalFileSystem
from fsspec.core import url_to_fs
import pandas as pd
import logging


"""
A class for managing raw datasets. A raw dataset is considered a dataset that is not processed and resides in its json format.

A raw dataset is composed by a name and optionally a list of partitions that end up setting the path where the file with the data is saved.

A dataset is a folder. And a partition is a subfolder. For example if the dataset name is "contacts" and the partitions are ["africa", "kenya"]. 
The dataset will be saved in the following path `contacts/africa/kenya`. Other partitions can be ["africa", "nigeria"] or ["europe", "spain"] which would result in
"contacts/africa/nigeria" and "contacts/europe/spain" respectively.

The data in a dataset can be stored in batches. Following the example above,
if the `RawDataset.append_save` is called for that dataset and partition with a batch of data, then the data
will be saved in the following path: contacts/region1/country1/batch-0.json.

Future calls to RawDataset.append will increment the batch number. For example, if the next call to append_save is called with the same dataset and partition,
then the data will be saved in the following path: contacts/region1/country1/batch-1.json.

The data can be saved in compressed format or not. If the data is saved in compressed 
format, then the file will be saved as: contacts/region1/country1/batch-0.json.gzip

Also, very basic metadata is saved in a file called 00_metadata.json. This file contains the last part number
and the partition name. The last part number is used to know what is the last part number that was added.

The RawDataset class is compatible with [fsspec](https://filesystem-spec.readthedocs.io/en/latest/). 
This means that it can be used with any filesystem that is compatible with fsspec such as Azure Blob, S3, Google Cloud Storage, etc.
By default, the RawDataset class uses the local filesystem.

Example:
    # Create a dataset
    data = [{
        "name": "John Doe",
        "age": 30,
        "city": "Nairobi"
    }]

    dataset = RawDataset(base_folder="data_raw/")
    dataset.append_save("contacts", data, ["africa", "kenya"], zip=True)

    data[0]["city"] = "Lagos"
    dataset.append_save("contacts", data, ["africa", "nigeria"], zip=True)
    data[0]["city"] = "Madrid"
    dataset.append_save("contacts", data, ["europe", "spain"], zip=True)
    dataset.files("contacts")
    >>> 
    
    dataset.clear("contacts", ["africa", "kenya"])
    dataset.clear("contacts")
    dataset.files("contacts")
    

"""


class RawDataset:
    """
    Class for managing raw / original / datasets

    It is compatible with fspec. 
    If when instantiated no fs is provided, then the local filesystem is used

    Each dataset is a folder and each partition is a subfolder
    The data is saved in the following format:
    {base_folder}/dataset_name/partition_level1/partition_level2/batch-0.[json|zip]

    """
    metadata_filename = "00_metadata.json"

    def __init__(self, name, base_folder="./datasets", storage_options=None):
        """
        Initialize the DatasetSaver.

        Args:
            dataset_name (str): Name of the dataset to save.
            base_folder (str): Base folder for saving datasets.
            storage_options (dict, optional): Additional options for the filesystem. Defaults to None.
        Example:
            dataset = RawDataset("contacts", base_folder="raw/")
            # Example using az blob storage
            dataset = RawDataset("contacts", base_folder="az://mycontainer/data_raw/", storage_options={"account_name": "myaccount", "account_key": "mykey"})
            # You can also use the default ENV variables AZURE_STORAGE_* 
            dataset = RawDataset("contacts", base_folder="az://mycontainer/data_raw/")
            # Example using s3 storage
            dataset = RawDataset("contacts", base_folder="s3://mybucket/data_raw/")

        """
        self.dataset_name = name
        self.base_folder = base_folder
        # build the dataset folder path
        self.dataset_folder = RawDataset.build_dataset_folder(base_folder, name)
        # Create the fsspec filesystem object
        # From the base_folder (url) create the filesystem object (fsspec.core.url_to_fs(url, **kwargs)[source]
        # get the list of available filesystems from fsspec
        # https://filesystem-spec.readthedocs.io/en/latest/api.html#fsspec
        
        fs, _ = url_to_fs(self.dataset_folder, storage_options=storage_options or {})
        self.fs = fs
        if not fs:
            self.fs = LocalFileSystem()
    
    @classmethod
    def build_dataset_folder(cls, base_folder: str, dataset_name: str):
        """
        Build the dataset folder path.
        Args:
            base_folder (str): Base folder for saving datasets.
            dataset_name (str): Name of the dataset to save.
        Returns:
            str: The full path to the dataset folder.
        """
        # if base_folder ends with / then separator = ""
        # else separator = "/"
        separator = "" if base_folder.endswith("/") else "/"
        return base_folder + separator + dataset_name
    
    @classmethod
    def build_partition_folder(cls, dataset_folder: str, partition: list = None):
        """
        Build the partition folder path.
        This is useful when creating the full path for a partition.
        Args:
            dataset_folder (str): The base folder for the dataset.
            partition (list, optional): Lists the partition the data belongs to.
        Returns:
            str: The full path to the partition folder.
        """
        if partition is None:
            partition = []
        # The final path will be dataset_folder + partition1 / partition2 ...
        folder = dataset_folder
        for sub_partition in partition:
            folder += "/" + sub_partition
        return folder
    
    
    def get_partition_folder(self, partition: list = None):
        """
        Get the folder for a partition
        Args:
            partition (list, optional): Lists the partition the data belongs to.
        Returns:
            str: The folder for the partition
        """
        return RawDataset.build_partition_folder(self.dataset_folder, partition)

    def exists(self, partition: list = None):
        """
        Check if the dataset or partition folder exists.
        Args:
            partition (list, optional): partition whose folder you want to check if exists  .
        Returns:
            bool: True if the dataset or partition exists, False otherwise
        """
        folder = self.get_partition_folder(partition)
        # check if the folder exists
        return self.fs.exists(folder)


    def is_empty(self, partition: list = None):
        """
        Check if the partition is empty
        Args:
            partition (list, optional): Lists the partition the data belongs to.
        Returns:
            bool: True if the partition is empty, False otherwise
        Raises:
            FileNotFoundError: If the partition or dataset does not exist or has been cleared.
        """
        # There are two options
        # 1. The folder does not exist, then the partition is empty
        if self.exists(partition) is False:
            return True
        # 2. The folder exists, then we need to check if the last batch number is 0
        get_last_batch_number = self.get_last_batch_number(partition)
        if get_last_batch_number == 0:
            return True
        else:
            return False


    def get_metadata(self, partition: list = None):
        """
        Get the metadata for a partition
        Args:
            partition (list, optional): Lists the partition the data belongs to.
        Returns:
            dict: Metadata for the partition
        Raises:
            FileNotFoundError: If the partition or dataset does not exist or has been cleared.
        Example:
            >>> dataset.get_metadata(["partition1", "partition2"])
            # Returns the metadata dict for the partition dataset_name/partition1/partition2
        Example metadata:
        {
            "last_batch": 1,
            "is_final_batch": False,
            "partition": ["partition1", "partition2"],
            "resume_cursor": None
        }
        """
        
        folder = self.get_partition_folder(partition)

        # check if the folder exists
        if self.fs.exists(folder):
            # Get the metadata file
            metadata_file = folder + "/" + self.metadata_filename
            # check if the metadata file exists
            if self.fs.exists(metadata_file):
                logging.debug("Metadata file exists: %s", metadata_file)
                with self.fs.open(metadata_file, "r") as f:
                    # load the json 
                    metadata = json.load(f)
                    return metadata
            else:
                raise FileNotFoundError(f"Metadata file does not exist: {metadata_file}")
        else:
            raise FileNotFoundError(f"Partition/Dataset does not exist or has been cleared. The folder {folder} does not exist")

    def _save_metadata(self, metadata: dict, partition: list = None, ):
        """
        Updates the metadata file for the partition with the values. Assumes the values has the correct schema.
        """
        folder = self.get_partition_folder(partition)
        metadata_file = folder + "/" + self.metadata_filename
        logging.debug("Saving metadata file: %s", metadata_file)
        with self.fs.open(metadata_file, "w") as f:
            json.dump(metadata, f)


    def has_final_batch(self, partition: list = None):
        """
        Check if the partition has a final batch
        Args:
            partition (list, optional): Lists the partition the data belongs to.
        Returns:
            bool: True if the partition has a final batch, False otherwise
        """
        metadata = self.get_metadata(partition)
        return metadata.get("is_final_batch", False)

    def set_is_final_batch(self, new_value:bool, partition: list = None):
        """
        Sets the 'is_final_batch' flag in the metadata for the specified partition.
        Args:
            new_value (bool): The value to set for the 'is_final_batch' flag.
            partition (list, optional): The partition for which to set the flag. Defaults to None.
        Example:
            dataset.set_is_final_batch(True, ["partition_level1", "partition_level2"])
        """
 
        metadata = self.get_metadata(partition=partition)
        metadata['is_final_batch'] = new_value
        self._save_metadata(metadata, partition=partition)


    def get_last_batch_number(self, partition: list = None):
        """
        Get the last batch number for a partition.
        Checks if the metadata file exists and if it does, then it gets the last batch number from there.
        If the metadata file does not exist, then it checks if there are any batch-XXX.XXX files in the folder.
        Args:
            partition (list, optional): Lists the partition the data belongs to.
        Returns:
            int: Last batch number for the partition. Or 0 if the partition is empty.
        """
        files = []
        last_batch = 0
        
        # if the partition does not exist, then the partition is empty
        if self.exists(partition) is False:
            return last_batch
        folder = self.get_partition_folder(partition)
        
        try: # Count the number of files in the folder
            files = self.fs.ls(folder)
        
            # If the folder is empty, then we can create the first part
            # If the folder is not empty, then we need to get the last part number
            logging.debug("Files in folder: %s", files)
            if len(files) != 0:
                # There should be a special file called 00_metadata.json
                # that contains the last part number
                # This is used to know what is the last part number
                # if the folder has more than 1 part, then we need to load the last partfile
                metadata_file = folder + "/" + self.metadata_filename
                if self.fs.exists(metadata_file):
                    logging.debug("Metadata file exists: %s", metadata_file)
                    with self.fs.open(metadata_file, "r") as f:
                        # load the json 
                        metadata = json.load(f)
                        # get the last part number
                        logging.debug("Metadata: %s", metadata)
                        last_batch = metadata["last_batch"]
                else:
                    logging.debug("Metadata file does not exist: %s", metadata_file)
                    logging.debug("Validating batch-x files in folder")
                    for file in files:
                        if "batch-" in file:
                            last_batch = max(last_batch, int(file.split("batch-")[1].split(".")[0]))
        except FileNotFoundError:
            # On blobs folder do not actually exist till a file is added
            pass 
        return last_batch
    
    def append_save(self, data:dict, partition: list = None, zip: bool = True, resume_cursor=None, is_final_batch=False):
        """
        Save a dict based dataset as json or gzip
        The data is saved in the dataset folder 

        Args:
            partition (list, optional): Lists the partition the data belongs to.
            zip (bool, optional): Whether to save the file in compressed format or not.
            final_batch (bool, optional): Whether to save the file as final batch or not.
        """
        folder = self.get_partition_folder(partition)
    
        # Create the directory for the dataset if does not exist
        if not self.fs.exists(folder):
            self.fs.mkdir(folder, recursive=True)
        
        # Get the last batch number
        last_batch = self.get_last_batch_number(partition)
        logging.debug("Last existing batch number: %s", last_batch)
    
        # Create the new file
        new_batch = last_batch + 1
        new_batch_str = str(new_batch).zfill(9)
        # The new file will be called batch-<number padded with 0>.[gzip|json]
        logging.info("Saving partition %s in %s, zip=%s, items=%s, batch=%s, resume_cursor=%s", partition, folder, zip, len(data), new_batch, resume_cursor)
        if zip:
            new_file = folder + "/batch-" + new_batch_str + ".gzip"
            # Save the zipped file
            with self.fs.open(new_file, "wb") as f:
                # Save the file as json
                # compress the file
                with gzip.GzipFile(fileobj=f, mode='wb') as gz:
                    gz.write(json.dumps(data).encode("utf-8"))
        else:
            new_file = folder + "/batch-" + new_batch_str + ".json"
            # Save the file
            with self.fs.open(new_file, "w") as f:
                # Save the file as json
                json.dump(data, f)

        # Save the metadata file
        metadata = {
                "last_batch": new_batch,
                 "is_final_batch": is_final_batch,
                "partition": partition,
                "resume_cursor": resume_cursor
        }
        self._save_metadata(metadata=metadata, partition=partition)


    def clear_save(self, data:dict, partition: list = None, zip: bool = True, is_final_batch=False):
        """
        First clear the dataset/partition and then save the dict in the partition.

        Args:
            data (dict): Data to save.
            partition (list, optional): Lists the partition the data belongs to.
            zip (bool, optional): Whether to save the file in compressed format or not.
            is_final_batch (bool, optional): Whether to save the file as final batch or not.
        Example:
            >>> dataset.clear_save({"foo": "bar"}, ["partition1", "partition2"], zip=True, is_final_batch=True)
            # The partition will be cleared and then the data will be saved in the following path:
            # dataset_name/partition1/partition2/batch-1.gzip will be created.
            # in 00_metadata.json the attribute last_batch will be set to 1 and is_final_batch will be set to True
        """
        # Clear the dataset/partition
        self.clear(partition)
        # Save the dataset
        self.append_save(data, partition=partition, zip=zip, is_final_batch=is_final_batch)

    def clear(self, partition: list = None):
        """
        Clear the dataset or a partition

        Args:
            partition (list, optional): Partition to clear. If not set, the whole dataset will be cleared.
        Example:
            dataset.clear(["partition1", "partition2"])
            dataset_name/partition1/partition2 will be cleaned.
            dataset.clear("dataset_name") will clear the whole dataset_name.

        """
        folder = self.get_partition_folder(partition)
        # Remove the folder
        logging.debug("Requested to clear folder %s", folder)
        # check if the folder exists
        if self.fs.exists(folder):
            # remove the folder
            self.fs.rm(folder, recursive=True)
            logging.debug("Removed folder: %s", folder)
        else:
            logging.debug("Folder %s does not exist", folder)

    def clear_many_partitions(self, partitions: list):
        """
        Clear multiple partitions

        Args:
            partitions (list): List of partitions to clear.
        Example:
            dataset.clear_many([["partition1", "partition2"], ["partition3", "partition4"]])
            # dataset_name/partition1/partition2 and dataset_name/partition3/partition4 will be cleaned.
        """
        for partition in partitions:
            self.clear(partition)


    def partitions(self, within_partition:list=None, as_dataframe: bool = False):
        """
        Get the partitions of a dataset

        Args:
            as_dataframe (bool, optional): If True, return the partitions as a pandas dataframe. If False, return the partitions as a list of dicts.
        Returns:
            list: List of dicts with partition info in the dataset.
            For example:
            [
                {
                    "dataset_name": "dataset_name",
                    "level1": "partition1",
                    "level2": "partition2"
                    "list": [
                        "partition1",
                        "partition2"
                    ],
                    "path": "/home/user/dataset_name/partition1/partition2",
                },
                ...
            ]
            if as_dataframe is True, then it will return a pandas dataframe with the same information.
        Raises:
            FileNotFoundError: If the partition or dataset does not exist.
        Example:
            # will return all partitions in the dataset_name.
            ds.partitions()
            ds.partitions(as_dataframe=True)
            # subset of partitions within the dataset_name
            ds.partitions(within_partition=["partition1", "partition2"])
        """
        files = self.files(partition=within_partition, as_dataframe=True)
        if files.empty:
            logging.debug("No files found in the dataset or partition.")
            return pd.DataFrame() if as_dataframe else []
        # files is a dataframe. We drop the columns that are file specific path, filename, zip and filesize
        files = files.drop(columns=["path", "filename", "zip", "filesize"], errors='ignore')
        # Now we need to get unique records in partition_path column
        partitions = files.drop_duplicates(subset=["partition_path"])
        if as_dataframe:
            return partitions.reset_index(drop=True)
        else:
            return partitions.to_dict(orient='records')


    def files(self, partition: list = None, as_dataframe: bool = False):
        """
        Get the files of a dataset or a partition

        Args:
            partition (list, optional): List of partitions to get. If not set, the whole dataset will be returned.
            as_dataframe (bool, optional): If True, return the files as a pandas dataframe. If False, return the files as a list of dicts.
        Returns:
            list: List of dicts with file info in the dataset or partition.
            For example:
            [
                {
                    "dataset_name": "dataset_name",
                    "level1": "partition1",
                    "level2": "partition2",
                    "partition": [
                        "partition1",
                        "partition2"
                    ],
                    "dataset_path": "/dataset_name/",
                    partition_path: "/dataset_name/partition1/partition2
                    "filename": "batch-0.json",
                    "path": "/home/user/dataset_name/partition1/partition2/batch-0.json",
                    "zip": True,
                    "filesize": 1024
                },
                ...
            ]
            if as_dataframe is True, then it will return a pandas dataframe with the same information.
        Raises:
            FileNotFoundError: If the partition or dataset does not exist.  
        Example:
            ds.files(partition=["partition1", "partition2"])
            files within dataset_name/partition1/partition2 will be returned.
            ds.files() will return the whole dataset_name.
        """
        folder = self.get_partition_folder(partition)
        
        if partition is None:
            partition = []
        
        # check if the folder exists
        if self.fs.exists(folder):
            # Get all files recursively using fs.find which is more efficient
            if hasattr(self.fs, 'find'):
                # Some filesystems like S3FileSystem have 'find' method
                files = self.fs.find(folder, maxdepth=None)
            elif hasattr(self.fs, 'glob'):
                # Others may have 'glob' method
                files = self.fs.glob(f"{folder}/**")
            else:
                # Fallback to manual recursion if necessary
                files = []
                def list_recursively(path):
                    for file_path in self.fs.ls(path):
                        if self.fs.isdir(file_path):
                            list_recursively(file_path)
                        files.append(file_path)
                
                list_recursively(folder)
        else:
            # if the folder does not exist, then raise an error
            raise FileNotFoundError(f"Partition/Dataset does not exist or has been cleared. The folder {folder} does not exist")
        
        # Now we create a pandas dataframe with the files including these columns
        # dataset_name, level1, level2, ... , leveln, path, filesize
        # The path is the full path of the file
        # The filesize is the size of the file in bytes
        # The level1, level2, ... , leveln are the partitions
        # The dataset_name is the name of the dataset
        # Create a list to store file information
        file_info = []
        # Process each file in the directory
        for file_path in files:
            file_info_dict = {}
            # if it is the metadata file, then skip it
            if file_path.endswith(self.metadata_filename):
                continue
            
            # ignore .DS_Store files
            if file_path.endswith(".DS_Store"):
                continue

            # Add dataset name
            file_info_dict["dataset_name"] = self.dataset_name
            
            # Add partition levels if they exist
            for i, sub_part in enumerate(partition):
                file_info_dict[f"level{i+1}"] = sub_part
            
            # Remove from the file_path anything that is before the dataset name enclosed in /
            # This is to get the relative path of the file
            # For example if the file_path is /home/user/dataset_name/partition1/partition2/batch-0.json
            # then the relative path will be partition1/partition2/batch-0.json
            dataset_path = f"/{self.dataset_name}/"
            relative_path = file_path.split(dataset_path, 1)[-1] if dataset_path in file_path else file_path

            # Split by '/' to get all partition levels
            path_parts = relative_path.split('/')
            # Skip the last part if it's a file
            if '.' in path_parts[-1]:
                file_info_dict["filename"] = path_parts[-1]
                path_parts = path_parts[:-1]
            
            # Add any additional partition levels found in the path
            for i, part in enumerate(path_parts):
                level_key = f"level{i+1}"
                if level_key not in file_info_dict:
                    file_info_dict[level_key] = part
            
            file_info_dict["partition"] = path_parts
            file_info_dict["dataset_path"] = dataset_path
            file_info_dict["partition_path"] = dataset_path + "/".join(path_parts)
            file_info_dict["path"] = file_path
            file_info_dict["zip"] = file_path.endswith(".gzip")
            file_info_dict["filesize"] = self.fs.info(file_path)["size"]
            
            
            file_info.append(file_info_dict)

        if as_dataframe:
            # Create a pandas DataFrame from the collected information
            return pd.DataFrame(file_info)
        return file_info
        
    def get_file_data(self, file_path):
        """
        Get the data from a file
        Args:
            file_path (str): Path to the file.
        Returns:
            dict: Data from the file.
        """
        # Check if the file exists
        if not self.fs.exists(file_path):
            raise FileNotFoundError(f"File does not exist. The file {file_path} does not exist")
        
        # Check if the file is compressed
        if file_path.endswith(".gzip"):
            with self.fs.open(file_path, "rb") as f:
                # decompress the file
                with gzip.GzipFile(fileobj=f, mode='rb') as gz:
                    data = gz.read()
                    return json.loads(data)
        else:
            with self.fs.open(file_path, "r") as f:
                data = f.read()
                return json.loads(data)
        
    def download(self, local_base_folder: str, partition: list = None,):
        """
        Download the files of a dataset or a partition to a local folder.
        If the dataset is already local, it will create a copy on the new local_base_folder.
        If the dataset is in a cloud environment, it will download the files to the local_base_folder.
        If the partition is not set, then the whole dataset will be downloaded.
        
        The local folder will have the same structure as the dataset.
        The base folder will be created if it does not exist.
        
        The files will be downloaded in the following format:
        {local_base_folder}/{dataset_name(f.i raw)}/{partition_level1}/{partition_level2}/batch-0.[json|gzip]
        
        Args:
            partition (list, optional): Specify a partition to download. If not set, the whole dataset will be downloaded.
            output_folder (str, optional): Folder where the files will be downloaded. Defaults to "./".
        Returns:
            local_file_path
        """
        # Remote folder with the dataset to download
        remote_folder = self.get_partition_folder(partition) + "/"

        # get the local folder path
        local_dataset_path = RawDataset.build_dataset_folder(local_base_folder, self.dataset_name)
        local_partition_path = RawDataset.build_partition_folder(local_dataset_path, partition)
        # Create the local folder if it does not exist
        # Create the LocalFileSystem object
        local_fs = LocalFileSystem()
        if not local_fs.exists(local_partition_path):
            local_fs.mkdir(local_partition_path, recursive=True)

        logging.info("%s RawDataset::download Downloading %s to %s", self.dataset_name, remote_folder, local_partition_path)
        self.fs.get(remote_folder, local_partition_path, recursive=True)

        return local_partition_path
    