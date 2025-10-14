from . import BaseDataset
from ..workspaces import Workspace


class GroupsDataset(BaseDataset):
    """
    A class to handle the Groups dataset.

    This class inherits from BaseDataset and is used to manage the Groups dataset.
    It provides methods to download, process, and manage the dataset.
    """

    def __init__(self,
                 workspace:Workspace = None,
                 base_folder: str = "./datasets",
                 storage_options: dict = None,
                 raw_dataset_batch_size: int = None):
        """
        Initialize a ContactsDataset object.

        Args:
            workspace: The workspace object associated with the dataset (RapidPro workspace).
            base_folder: The base folder where the dataset will be stored.
            fs: The file system object to use for file operations (fsspec compatible). Uses local file system by default.
        """

        super().__init__(name="groups",
                         workspace=workspace,
                         base_folder=base_folder,
                         storage_options=storage_options,
                         raw_dataset_batch_size=raw_dataset_batch_size)
