from . import BaseDataset
from ..workspaces import Workspace


class RunsDataset(BaseDataset):
    """
    A class to handle the Runs dataset.

    This class inherits from BaseDataset and is used to manage the Runs dataset.
    It provides methods to download, process, and manage the dataset.
    """

    def __init__(self, workspace:Workspace = None,
                 base_folder: str = "./datasets",
                 storage_options: dict = None,
                 raw_dataset_batch_size: int = None):
        """
        Initialize a MessagesDataset object.

        Args:
            workspace: The workspace object associated with the dataset (RapidPro workspace).
            base_folder: The base folder where the dataset will be stored. 
                Everything will be stored within the <base_folder>/messages folder.
            storage_options: Additional options for the storage backend (e.g., fsspec compatible).
            raw_dataset_batch_size: The batch size for downloading the raw dataset.
        """

        super().__init__(name="runs",
                         workspace=workspace,
                         base_folder=base_folder,
                         storage_options=storage_options,
                         raw_dataset_batch_size=raw_dataset_batch_size)
