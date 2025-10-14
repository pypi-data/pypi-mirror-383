import logging
import re
from datetime import datetime
import pandas as pd
import time 

from temba_client.v2 import TembaClient
from . import RawDataset 
from ..workspaces import Workspace
from ..time_utils import yesterday_end_of_day, get_date_range







class BaseDataset:
    """ 
    Convention structure for the raw dataset:
    Raw dataset assumes this "<name>/raw/<workspace_code>/<yyyy>/<yyyy-mm-dd>" as the partitioning scheme.
    where name is something like contacts, flows, runs, messages, etc.
    The workspace_code is the code of the workspace
    The yyyy-mm-dd is the date range of the data.

    When all the data is downloaded the first date is set to 2014-01-01 and the last date is set to the end of 
    the last period (end of day 14 or end of last day of the month)

    """

    DEFAULT_BATCH_SIZE = 100000 # 100k
    """
    Default batch size for saving a file in the raw dataset. It will create files with this number of records.
    """

    INIT_DATE = datetime(2014, 1, 1, 0, 0, 0) # January 1st, 2014
    """
    First date of the dataset. RapidPro started around 2014, so any workspace should not have data before this date.
    """
    
    def __init__(self, name, 
                 workspace:Workspace,
                 base_folder:str="./datasets",
                 storage_options:dict=None,
                 raw_dataset_batch_size:int=None):
        """
        Initialize a BaseDataset object.
        
        Args:
            name: The name of the dataset (e.g. contacts, flows, runs, messages, etc.)
            workspace: The workspace object associated with the dataset
            base_folder: The base folder where the dataset will be stored
            raw_dataset_batch_size: The batch size for saving a raw dataset (defaults to 100k)
            
        """
        
        self.name = name
        self.workspace = workspace
        self.base_folder = base_folder
        self.dataset_base_folder = f"{self.base_folder}/{self.name}"
        self.raw_dataset_batch_size = raw_dataset_batch_size or BaseDataset.DEFAULT_BATCH_SIZE
        self.storage_options = storage_options
        self.raw_dataset = RawDataset("raw", base_folder=self.dataset_base_folder, storage_options=self.storage_options)
        self.rapidpro_client = TembaClient(self.workspace.host, self.workspace.token)
        # this is the method that will be used to download the data by default.
        self.rapidpro_client_method = "get_" + name

    def __str__(self):
        return f"{self.__class__.__name__}({self.name}, {self.workspace.code}, {self.base_folder}, {self.raw_dataset_batch_size}, {self.rapidpro_client_method})"
    
    def __repr__(self):
        return self.__str__()
    

    def _is_valid_ws_partition(self, ws_partition:list):
        """
        Validates that the partition has the format None, [], [<yyyy>], or [<yyyy>, <yyyy-mm-dd>]
        returns True if the partition is valid, False otherwise.
        Args:
            ws_partition: The partition to validate.
        Returns:
            True if the partition is valid, False otherwise.
        Example:
            >>> ds = BaseDataset(name="contacts", workspace=None)
            >>> ds._validate_is_ws_partition(["2023"])
            True
            >>> ds._validate_is_ws_partition(["2023", "2023-10-01"])
            True
            >>> ds._validate_is_ws_partition(["2023", "2023-10-01", "2023-10-02"])
            False
        """
        if ws_partition is None or len(ws_partition) == 0:
            return True
        if len(ws_partition) > 2:
            return False
        # If we reach here, at least 1 element
        # check if the first element is a year using a regexp
        if re.match(r"^\d{4}$", ws_partition[0]):
            # TODO check if the year of the second element is the same as the first element
            # TODO check if the second element is a valid date
            if len(ws_partition) == 2:
                # check if the first element is a year and the second element is a date using a regexp
                return bool(re.match(r"^\d{4}-\d{2}-\d{2}$", ws_partition[1]))
            else:
                # check if the first element is a year
                return True
        else:
            return False


    def _add_ws_to_partition(self, ws_partition:list=None) -> list:
        """
        Add the workspace code to the partition. By convention ws_partition is a partition within the workspace 
        for example ["2023","2023-10-01"] and this function will add the workspace code 
        as the first element of the partition.
        This function assumes that the dataset is partitioned following this schema:
         workspace.code / yyyy / yyyy-mm-dd
        where the workspace code is the first element of the partition.
        ws_needs to be set. 

        Args:
            partition: has to be either None, [], [yyyy] or [yyyy, yyyy-mm-dd].
        Returns:
            The partition list.
        Example:
            >>> ds = BaseDataset(name="contacts", workspace=Workspace(code="code"))
            >>> ds._add_ws_to_partition(partition=["2023", "2023-10-01"])
            ['code', '2023', '2023-10-01']
            >>> ds._compute_partition(partition=None)
            ['workspace_code']
            >>> ds._compute_partition(partition=["whatever])
            ValueError: partition is not valid. It should be None, [], [yyyy], or [yyyy, yyyy-mm-dd]
        """
        if not self._is_valid_ws_partition(ws_partition):
            raise ValueError("partition is not valid. It should be None, [], [yyyy], or [yyyy, yyyy-mm-dd]")
        if ws_partition is None or len(ws_partition) == 0:
                return [self.workspace.code]
        else:
            return [self.workspace.code] + ws_partition
            

    def raw_dataset_files(self, ws_partition:list=None, as_dataframe=False)-> [str, pd.DataFrame]:
        """
        Get the list of files in the raw dataset for the specified partition.
        If the partition is None, it will return all the files in the dataset.
        If as_dataframe is True, it will return the files as a dataframe.
        If as_dataframe is False, it will return the files as a list.
        Args:
            ws_partition: The partition. If workspace is set, then you do not need to add the workspace files e.g. ["2023","2023-10-01"]
            as_dataframe: Whether to return the files as a dataframe or a list
        Returns:
            The files in the partition
        Raises:
            FileNotFoundError: If the partition is not found or if it is empty.
        """
        # check if the partition is valid
        partition = self._add_ws_to_partition(ws_partition)
        return self.raw_dataset.files(partition=partition, as_dataframe=as_dataframe)

    def get_last_downloaded_date(self, ws_partition:list=None) -> datetime:
        """
        Get the last date downloaded for the specified partition in the current workspace.
        self.workspace needs to be set.
        If the partition is None, it will return the last date downloaded for all partitions.
        Args:
            ws_partition: The partition within the workspace to filter the files e.g. ["2023","2023-10-01"]
        Returns:
            datetime with last date downloaded for the partition.
            None if there are no files in the partition
        """
        try:
            files_df = self.raw_dataset_files( ws_partition=ws_partition, as_dataframe=True)
        except FileNotFoundError:
            logging.warning("get_last_downloaded_date: Folder not found for partition %s in workspace %s", ws_partition, self.workspace.code)
            return None
        if files_df.empty:
            logging.warning("get_last_downloaded_date: No files found for partition %s in workspace %s", ws_partition, self.workspace.code)
            return None
        # In the files_df the following columns exist
        # level1 = workspace
        # level2 = year [2023,2024, etc]
        # level3 = yyyy-mm-dd string [2023-10-01, 2023-10-02, etc]
        # We have to get the most recent date in the level3
        files_df = files_df[files_df["level3"].notna()]
        files_df["level3"] = pd.to_datetime(files_df["level3"], format="%Y-%m-%d")
        files_df = files_df.sort_values(by=["level3"], ascending=False)
        # get the last date downloaded
        last_date = files_df.iloc[0]["level3"]
        last_date = last_date.replace(hour=0, minute=0, second=0, microsecond=0)
        # get the last date downloaded in the format yyyy-mm-dd
        return last_date



    def download_dated_dataset(self, clear:bool=False, continue_if_exists:bool=True, after_date:datetime=None, before_date:datetime=None, frequency:str="D") -> bool:
        """
        downloads a dataset from RapidPro that is date bounded.
        If after_date is not set, it will download since the first date in the dataset.
        If before_date is not set, it will download until the previous completed period. For example, if it is day, then it will download until yesterday end of day. If it is week, it will download until the last 
        completed week, if it is month end, it will download until the last completed month, and if it is year, it will download until the last completed year.
        
        Note: if you want to force the download till now, just add one day, month or year to the before_date. For example, if you want to download until today, set before_date to yesterday_end_of_day() + 1 day.

        If continue_if_exists is True, it will continue downloading from the last date downloaded (including that date). For example, if the after_date is set to 2023-01-01 and the last date downloaded is 2023-10-01
        it will download from 2023-10-01 to the before_date (if set).
        
        If continue_if_exists is False, it will reset each partition in the period and re-download.
        The partition will be stored within [workspace_code, yyyy, yyyy-mm-dd] where the yyyy-mm-dd is the starting date of the range range.

        
        Args:
            clear: If True, it will clear each partition before downloading. If False, it will continue adding batches to the partition.
            continue_if_exists: If False, it will reset any existing partition in the date range otherwise it will continue downloading the last partition if it is not marked as completed (is_last_batch=False in 00_metadata.json)
            after_date: The date to start the download from. If not set will download since ever (self.INIT_DATE)
            before_date: The last date to download. If not set, it will use yesterday. 
            frequency: The frequency of the data to download. It can be either day ("D"), week ("W"), month end ("ME") or year ("Y"). Default is "D" (daily).

        Returns:
            True if was able to finish. Exception if there was some issue.
        Raises:
            ValueError: If the after_date is greater than the before_date or if the partition is not valid.
            ValueError: If the frequency is not one of the following: D, W, ME, Y
        Example:
            
            >>> ds = BaseDataset(name="contacts", workspace=Workspace(code="code"))
            >>> ds.download_dated_dataset(clear=True, after_date="2023-10-01", before_date="2023-10-31", frequency="D")
            It will download the "contacts" dataset for the workspace "code" from 2023-10-01 to 2023-10-31 in a daily frequency.
            If a partition exists, it will be cleared before downloading.
            
            >>> ds.download_dated_dataset(continue_if_exists=True, after_date="2023-10-01", before_date="2023-10-15", frequency="M")
            It will download the "contacts" dataset for the workspace "code" from 2023-10-01 to 2023-10-15 in a monthly frequency.
            Because continue_if_exists is True, it will continue downloading from the last partition fully downloaded.
            Because the frequency is set to ME (month end), it will download the data for the month of September 2023.
        """
        logging.info("%s - %s Called download_dated_dataset (clear: %s, continue_if_exists=%s, after_date %s, before_date %s, frequency %s)", self.name, self.workspace.code, clear, continue_if_exists, after_date, before_date, frequency)
        # check that after_date is not greater than before_date
        if after_date and before_date and after_date > before_date:
            raise ValueError("after_date cannot be greater than before_date")

        if frequency not in ["D", "W", "ME", "Y"]:
            raise ValueError("frequency must be one of the following: D, W, ME, Y")
        
        if continue_if_exists and after_date is None:
            # get the last date downloaded
            last_date = self.get_last_downloaded_date()
            if last_date is None:
                logging.warning("%s:  No previous data downloaded. Set %s as after_date", self.workspace.code, after_date)
            else:
                logging.info("%s: Setting after_date to the last date downloaded: %s", self.workspace.code, last_date)
                after_date = last_date 
            # check that the last date is not greater than the before_date
            if before_date and last_date > before_date:
                raise ValueError(f"last_date downloaded ({last_date}) cannot be greater than before_date ({before_date})")
            # set the after_date to the last date downloaded

        # Set the default value for the after_date and before_date
        after_date = after_date or self.INIT_DATE
    
        yesterday = yesterday_end_of_day()
        end_loop = before_date or yesterday # this date is when the end of the date range will be set to. 

        last_date_downloaded = None
        logging.info("%s download_dated_dataset: Starting download loop (continue_if_exists: %s, after_date: %s, before_date: %s, yesterday=%s, end_loop=%s, frequency: %s)", self.name, continue_if_exists, after_date, before_date, yesterday, end_loop, frequency)   
        
        #Log all the periods that will be computed
        logging.info("%s -> Periods to be downloaded:", self.workspace.code)
        for i_date in pd.date_range(start=after_date, end=end_loop, freq=frequency):
            # get the partition name
            i_after_date, i_before_date = get_date_range(a_date=i_date, frequency=frequency)
            ws_partition = [i_after_date.strftime("%Y"), i_after_date.strftime("%Y-%m-%d")]

            i_after_date_str = i_after_date.strftime("%Y-%m-%dT%H:%M:%SZ")
            i_before_date_str = i_before_date.strftime("%Y-%m-%dT%H:%M:%SZ")
            logging.info("          Period: %s -> %s (%s): %s [freq: %s] after: %s, before: %s]", self.name, self.workspace.code, self.workspace.host, ws_partition, frequency, i_after_date_str, i_before_date_str)

        
        for i_date in pd.date_range(start=after_date, end=end_loop, freq=frequency):
            # get the partition name
            i_after_date, i_before_date = get_date_range(a_date=i_date, frequency=frequency)
            ws_partition = [i_after_date.strftime("%Y"), i_after_date.strftime("%Y-%m-%d")]

            i_after_date_str = i_after_date.strftime("%Y-%m-%dT%H:%M:%SZ")
            i_before_date_str = i_before_date.strftime("%Y-%m-%dT%H:%M:%SZ")

            logging.info("Downloading %s -> %s (%s): %s [freq: %s] after: %s, before: %s]", self.name, self.workspace.code, self.workspace.host, ws_partition, frequency, i_after_date_str, i_before_date_str)
            # set beggining and end of the day
            
            self._downloader(ws_partition=ws_partition, clear=clear, continue_if_exists=continue_if_exists,
                             rapidpro_client_kwargs={"after": i_after_date_str,
                                                     "before": i_before_date_str})
            last_date_downloaded = i_after_date
        logging.info("%s: %s [%s]  Download_dated_dataset: Finished download loop. Last period downloaded = %s [freq: %s ]", self.name, self.workspace.code, self.workspace.vendor, last_date_downloaded, frequency)
        return True
        


    def download_full_dataset(self, clear:bool=False, continue_if_exists:bool=False) -> bool:
        """
        Download the full dataset from RapidPro.
        It will download the full dataset in [workspace_code, yyyy, yyyy-mm-dd] where the yyyy-mm-dd date is today's day. The download will include all the data.
        If the partition already exist and clear is False, it will return True if the partition is already completed.
        If the partition is not completed, and continue_if_exists is True, it will continue adding batches to the partition.
        If the partition is not completed and continue_if_exists is False, it will raise a ValueError.
    
        Args:
            partition: The partition to store the  download.
            clear: If True, it will clear the partition before downloading.
            continue_if_exists: If True, it will continue adding batches to the partition if it already exists. Ignored if clear is True.
        Returns:
            True if was able to finish. Exception if there was some issue.
        Raises:
            ValueError: If the partition exists, is not completed, and both flags, clear and continue_if_exists, are False (so it cannot do anything with a partition that is not empty).
        """
        today = datetime.now().strftime("%Y-%m-%d")
        todays_year = datetime.now().strftime("%Y")
        # set the default value for the partition

        ws_partition = [todays_year, today]

        return self._downloader(ws_partition=ws_partition, clear=clear, continue_if_exists=continue_if_exists,)


    def _downloader(self, ws_partition:list = None, clear:bool = False,
                    continue_if_exists:bool = False,
                    rapidpro_client_method:str = None, 
                    rapidpro_client_args:list=None, 
                    rapidpro_client_kwargs:dict=None) -> bool:
        """
        Download the dataset from RapidPro.
        partition must include self.workspace.code as the first element.
        Args:
            ws_partition: The partition within the workspace to store the downloaded data e.g. ["2023","2023-10-01"]
            clear: If True, it will clear the partition before downloading.
            continue_if_exists: If True, it will continue adding batches to the partition if it already exists. Ignored if clear is True.
            rapidpro_client_method: The method to use to download the data from RapidPro. If not set it will use the default method (self.rapidpro_client_method, which is initialized to get_<self.name>. f.i. if name is contacts, it will use get_contacts)
            rapidpro_client_args: The arguments to pass to the method.
            rapidpro_client_kwargs: The keyword arguments to pass to the method.
        Returns:
            True if it was able to complete the download, or if the partition is already completed. 
        Raises:
            ValueError: If the partition exists and is not completed and both flags, clear and continue_if_exists, are False (so it cannot do anything with a partition that is not empty). 
        Example:
            >>> ds = BaseDataset(name="contacts", workspace=Workspace(code="code"))
            >>> ds._downloader(ws_partition=["2023", "2023-10-01"], clear=True)    
            >>> ds._downloader(ws_partition=["2023", "2023-10-01"], clear=False, rapidpro_client_kwargs={"after_date": "2023-10-01T00:00:00Z", "before_date": "2023-10-01T23:59:59Z"})
        """
        rapidpro_client_method = rapidpro_client_method or self.rapidpro_client_method
        rapidpro_client_args = rapidpro_client_args or []
        rapidpro_client_kwargs = rapidpro_client_kwargs or {}

        partition = self._add_ws_to_partition(ws_partition=ws_partition)
        
        logging.info("Downloading %s -> %s [%s] with %s method (clear %s, continue_if_exists %s).", self.name, partition ,self.workspace.code, rapidpro_client_method, clear,continue_if_exists)
        resume_cursor = None
        # Check if the partition is empty
        if not self.raw_dataset.is_empty(partition=partition):
            # If not empty and clear is True => clear the partition
            if clear:
                logging.info("%s: %s [%s] Clearing partition %s before download.", self.name, self.workspace.code, self.workspace.vendor, partition)
                self.raw_dataset.clear(partition=partition)
            else:
                logging.info("%s: %s [%s] Partition %s already exists and not empty", self.name, self.workspace.code, self.workspace.vendor, partition)
                # Check if the partition is marked as completed
                if self.raw_dataset.has_final_batch(partition=partition):
                    logging.info("%s: %s [%s] Partition %s is already marked as completed. Returning", self.name, self.workspace.code, self.workspace.vendor, partition)
                    return True
                else:
                    # Here clear is False, and continue_if_exists is False => raise an error because 
                    # partition is not marked as completed and we are not allowed to continue.
                    if not continue_if_exists:
                        logging.error("%s: %s [%s] Partition %s already exists and is not empty. Use clear=True to clear the partition or continue_if_exists=True to continue adding batches.", self.name, self.workspace.code, self.workspace.vendor, partition)
                        raise ValueError(f"Partition {partition} in {self.workspace.code} already exists and is not empty. Set clear=True to clear the partition or continue_if_exists=True to continue adding batches.")
                    # We are allowed to continue downloading, so we will get the last cursor from the metadata
                    logging.info("Partition %s is not marked as completed. Continuing download.", self.workspace.code)
                    # get the cursor metadata from the workspace
                    metadata = self.raw_dataset.get_metadata(partition=partition)
                    # add cursor to the metadata
                    if metadata and "resume_cursor" in metadata:
                        resume_cursor = metadata["resume_cursor"]
                        logging.info("Using last cursor %s from metadata for partition %s", resume_cursor, partition)
                    else:
                        logging.info("No cursor found in metadata for partition %s. Starting from the beginning. Clearing partition", partition)
                        self.raw_dataset.clear(partition=partition)
                        resume_cursor = None
        # get the rapidpro client method 
        method = getattr(self.rapidpro_client, rapidpro_client_method)
        # Check if the method is callable
        if not callable(method):
            raise ValueError(f"{method} is not a callable method in {self.rapidpro_client.__class__.__name__}")
        
        # Counters
        saved_items = 0
        records_downloaded = 0
        download_batch_number = 0
        save_batch_number = 0
        raw_data = []
        logging.info("%s -> %s (%s): %s %s args: %s kwargs: %s, resume_cursor %s", self.name, self.workspace.code, self.workspace.vendor, ws_partition, rapidpro_client_method, rapidpro_client_args, rapidpro_client_kwargs, resume_cursor)
        iterator = method(*rapidpro_client_args, **rapidpro_client_kwargs).iterfetches(retry_on_rate_exceed=True, resume_cursor=resume_cursor)
        for batch in iterator:
            logging.info("%s -> %s (%s): %s %s Downloaded %d items. Partition total %d. In memory %d records.", self.name, self.workspace.code, self.workspace.vendor, ws_partition, rapidpro_client_method, len(batch), records_downloaded, len(raw_data))
            records_downloaded += len(batch)
            download_batch_number += 1
            for item in batch:
                item_dict = item.serialize()
                raw_data.append(item_dict)
                if len(raw_data) >= self.raw_dataset_batch_size:
                    saved_items += len(raw_data)
                    logging.info("%s: Saving batch %d in partition: %s. Partition total: %d items", self.workspace.code, save_batch_number, partition, saved_items)
                    self.raw_dataset.append_save(raw_data, partition=partition, resume_cursor=iterator.get_cursor(), is_final_batch=False)
                    raw_data = []
                    save_batch_number += 1
        # Save any remaining data
        if raw_data:
            saved_items += len(raw_data)
            logging.info("%s (%s): Saving **FINAL BATCH** in partition %s. Batch # %s. Total in partition: %d. Last batch: %d items", self.workspace.code, self.workspace.vendor, partition, save_batch_number, saved_items, len(raw_data))
            self.raw_dataset.append_save(raw_data, partition=partition, is_final_batch=True)
        # Successfull download
        return True
    
    def iter_dated_batch_raw_files(self, after_date: datetime=None, before_date: datetime=None, with_file_info:bool=False) -> [list, dict]:
        """
        Iterate over the existing dataset file batches.
        Args:
            after_date: The date to start the iteration from. If not set will iterate from the first date in the dataset.
            before_date: The date to end the iteration. If not set will iterate until the last date in the dataset.
            with_file_info: If True, it will yield a tuple with the file info and the raw data. If False, it will yield only the raw data.
        Yields:
            A tuple with the file info (dict) and the raw data (list of dict where each dict is a record from RproAPI) if with_file_info is True, otherwise
            it will yield only the raw data.
        Returns:
            A generator that yields batches of data (list of dicts).
        Raises:
            FileNotFoundError: If no data has been downloaded yet or if the workspace is not found.
        Example:
            >>> ds = BaseDataset(name="contacts", workspace=Workspace(code="code"))
            >>> for file_info, raw_data in ds.iter_dated_batch_raw_files(after_date=datetime(2023, 10, 1), before_date=datetime(2023, 10, 31), with_file_info=True):
            >>>     print(file_info)  # file info will be a dict of RawDataset file info
            >>>     print(raw_data)  # raw_data will be a list of dicts with the raw data from RapidPro API
            >>>     # process the raw_data here
            >>>     # e.g. process_contacts_pl(raw_data, metadata=metadata)
            >>> # also getting the index of the file (explore the whole dataset)
            >>> for index, (file_info, raw_data) in enumerate(ds.iter_dated_batch_raw_files(with_file_info=True)):
            >>>     print(f"Processing file {index+1}: {file_info['path']}")
        """
        if after_date is None:
            after_date = self.INIT_DATE
        if before_date is None:
            before_date = datetime.now()

        after_date_str = after_date.strftime('%Y-%m-%d')
        before_date_str = before_date.strftime('%Y-%m-%d')


        logging.info("[%s] Processing workspace %s from %s until %s...",
                    self.workspace.code, self.workspace.code, after_date_str, before_date_str)

        # get the list of files
        files_df = self.raw_dataset.files(partition=[self.workspace.code], as_dataframe=True)
        
        # print (files_df.head())
        if files_df.empty:
            logging.warning("[%s] No files found for workspace %s",
                            self.workspace.code, self.workspace.code)
            return
        num_files = len(files_df)
        logging.info("[%s] Found %s files for workspace %s",
                    self.workspace.code, num_files, self.workspace.code)

        for index, row in files_df.iterrows():
            # the following cols are expected in the row
            # level1 workspace.code
            # level2 yyyy
            # level3 yyyy-mm-dd
            # path is the path to the file
            # filesize

            file_path = row['path']
            if row['level3'] < after_date_str:
                logging.info("%s - %s: [%s/%s] Skipping file %s as it is earlier than the after date (first date) %s",
                            self.name, self.workspace.code, index, num_files, file_path, after_date_str)
                continue
            if row['level3'] > before_date_str:
                logging.info("%s - %s: [%s/%s] Skipping file  %s as it is newer than the before date (last date) %s",
                            self.name, self.workspace.code, index, num_files, file_path, before_date_str)
                continue
            
            logging.info("%s - %s: [%s/%s] Iterating file %s (%s bytes)...",
                        self.name, self.workspace.code, index, num_files, file_path, row['filesize'])
            raw_data = self.raw_dataset.get_file_data(file_path)
            if with_file_info:
                yield row, raw_data
            else:
                yield raw_data
    
    def iter_last_date_raw_files(self, with_file_info:bool=False) -> [list, dict]:
        """
        Iterate over the last partition date files in the dataset [workspace_code, yyyy, yyyy-mm-dd].
        This will iterate over the last partition downloaded.
        This is useful for processing datasets that are downloaded with download_full_dataset. 
        If you download -> process one period at a time, you can use this method to iterate over the last partition date files.
        
        Note: This method assumes that the last partition is already downloaded and marked as completed.

        Args:
            with_file_info: If True, it will yield a tuple with the file info and the raw data. If False, it will yield only the raw data.

        Yields:
            A tuple with the file info and the batch with the raw data contained in the file if with_file_info is True, otherwise
            it will yield only the batches raw data.
        Returns:
            A generator that yields batches of data.
        Raises:
            FileNotFoundError: If no data has been downloaded yet or if the last partition is not found.
        """
        last_date = self.get_last_downloaded_date()
        logging.info("%s - %s : Last date downloaded for %s is %s", self.name, self.workspace.code, self.workspace.code, last_date)
        if last_date is None:
            logging.error("%s - %s: No data downloaded yet. Cannot iterate over last date files.", self.name, self.workspace.code)
            raise FileNotFoundError(f"{self.name} - {self.workspace.code}: No data downloaded yet. Cannot iterate over last date files.")
        if not self.raw_dataset.has_final_batch(partition=[self.workspace.code, last_date.strftime("%Y"), last_date.strftime("%Y-%m-%d")]):
            logging.warning("%s - %s: Last partition %s is not yet completed. However, will be iterating over last date files.", self.name, self.workspace, last_date.strftime("%Y-%m-%d"))
        # get files in partition
        files_df = self.raw_dataset.files(partition=[self.workspace.code, last_date.strftime("%Y"), last_date.strftime("%Y-%m-%d")], as_dataframe=True)
        if files_df.empty:
            logging.warning("%s - %s: No files found for last partition %s", self.name, self.workspace.code, last_date.strftime("%Y-%m-%d"))
            return
        # iterate over the files in the partition
        for index, row in files_df.iterrows():
            logging.info("%s - %s: [%s/%s] Iterating file %s (%s bytes)...",
                        self.name, self.workspace.code, index+1, len(files_df), row['path'], row['filesize'])
            if with_file_info:
                yield row, self.raw_dataset.get_file_data(row['path'])
            else:
                yield  self.raw_dataset.get_file_data(row['path'])


    def clear_partition(self, ws_partition:list=None):
        """
        Clear the partition in the raw dataset.
        Args:
            ws_partition: The workspace partition to clear. If None, it will clear the whole dataset.
        Returns:
            True if the partition was cleared, False if it was already empty.
        Raises:
            ValueError: If the partition is not valid.
        Example:
            >>> ds = BaseDataset(name="contacts", workspace=Workspace(code="code"))
            >>> ds.clear_partition(ws_partition=["2023", "2023-10-01"])
        """
        partition = self._add_ws_to_partition(ws_partition=ws_partition)
        return self.raw_dataset.clear(partition=partition)