import pandas as pd
from typing import Dict, List, Optional, Any
import logging

# These functions deal with the workspaces

# -*- coding: utf-8 -*-

"""
@file   workspaces.py"
@brief  Workspaces
@details
This module contains functions to process workspaces.
A workspace represents the connection information to a RapidPro instance and a set of 
metadata values. 

This data is stored in two files (defaulted to workspace_metadata.csv and workspace_secrets.csv)
The one with the secrets contains the following columns:
workspace_code (str a-zA-Z0-9_) - a unique identifier of the workspace
host (str) - the host of the RapidPro instance (f.i, rapidpro.io)
token (str) - the token to access the RapidPro instance
active (book) - a boolean value to indicate if the workspace is active or not

The one with the metadata contains, ad minimum the workspace_code. Then it can
contain other arbitrary columns with metadata such as workspace_name, country, region, business_unit...


By Convention we've established that:
 * metadata columns that end with _field are used to indicate the name of a field in RapidPro
 * metadata columns that end with _label are used to indicate the name of a label for a field in RapidPro

 This is useful for processing multiple workspaces with different configurations. For example, if we have a 
 metadata column called "country_field" with the value "country", then we know that in that workspace, the 
 field that contains the country information is called "country". But there may be another workspace in 
 which the column "country_field" has the value "nation", so in that workspace, the field that contains 
 the country information is called "nation".

"""

class Workspace:
    """
    Represents a RapidPro workspace with connection information and metadata.
    """
    def __init__(self, code: str, host: str, token: str, active: bool = True, vendor:str="", metadata: Optional[Dict[str, Any]] = None):
      """
      Initialize a workspace.
      
      Args:
        code: Unique identifier for the workspace
        host: Host of the RapidPro instance
        token: Token to access the RapidPro instance
        active: Boolean indicating if the workspace is active
        vendor: Optional string indicating the vendor of the workspace. It is determined based on the host if empty. See _vendor()
        metadata: Dictionary with additional metadata for the workspace
      """
      self.code = code
      self.host = host
      self.token = token
      self.active = active
      self.metadata = metadata or {}
      self.vendor = self._vendor(vendor)  # Determine vendor based on host
    
    def get_metadata(self, with_fields=True, with_labels=True) -> Dict[str, Any]:
        """Return the metadata of the workspace including code, host, vendor and active status.
        For processing purposes, it might be useful to exclude fields that end with _field or _label
        Args:
          with_fields: If True, include fields that end with _field in the metadata
          with_labels: If True, include fields that end with _label in the metadata
        Returns:
          Dictionary with the metadata of the workspace
        """
        metadata = self.metadata.copy()
        if not with_fields:
          metadata = {k: v for k, v in metadata.items() if not k.endswith('_field')}
        if not with_labels:
          metadata = {k: v for k, v in metadata.items() if not k.endswith('_label')}
        metadata.update({
            'workspace_code': self.code,
            'workspace_host': self.host,
            'workspace_active': self.active,
            'workspace_vendor': self.vendor
        })
        return metadata
    
    def _vendor(self, vendor:str=None) -> str:
      """
      Return the vendor of the workspace based on the value of host if known otherwise returns "Unknown".
      Current vendors known are Ona (ona.io), TextIt(rapidpro.io) and Weni (ilhasoft.mobi).
      If vendor is provided, it is returned as is.

      This function is used during initialization.
      Args:
        vendor: Optional vendor name. If empty, it will be determined based on the host.
      Returns:
        str: The vendor name or "Unknown" if not recognized.
      Example:
        >>> ws = Workspace(code="test", host="rapidpro.io", token="abc123")
        >>> ws._vendor()
        >>> "TexIt"
        >>> ws._vendor("TextIt Inc.")
        >>> "TextIt Inc."
        >>> ws.vendor 
        >>> "TextIt"
        >>> ws = Workspace(code="test", host="rapidpro.io", token="abc123", vendor="TextIt Inc.")
        >>> ws._vendor()
        >>> "TextIt"
        >>> ws.vendor
        >>> "TextIt Inc."

      """
      if vendor != "":
        return vendor
      if self.host.endswith("rapidpro.io"):
        return "TextIt"
      elif self.host.endswith("ilhasoft.mobi"):
        return "Weni"
      elif self.host.endswith("ona.io"):
        return "Ona"
      else:
        return "Unknown"
        

    def __str__(self) -> str:
        """String representation of the workspace."""
        return f"Workspace({self.code}, {self.host}, active={self.active})"
    
    def __repr__(self) -> str:
      """Detailed representation of the workspace."""
      return f"Workspace({self.code}, {self.host}, active={self.active}, metadata={self.metadata})"
  
    def __eq__(self, other):
      """
      Compare if two workspaces are the same.
      
      Workspaces are considered equal if they have the same code, host, token, active status, and metadata.
      
      Args:
        other: Another workspace to compare with
        
      Returns:
        bool: True if workspaces are equal, False otherwise
      """
      if not isinstance(other, Workspace):
        return False
      return (self.code == other.code and
              self.host == other.host and
              self.token == other.token and
              self.vendor == other.vendor and
              self.active == other.active and
              self.metadata == other.metadata)

class WorkspaceList:
  """
  Manages a list of RapidPro workspaces.
  """
  def __init__(self):
    """Initialize an empty workspace list."""
    self.workspaces: List[Workspace] = []
  
  def load_workspaces(self, secrets_path: str = "workspace_secrets.csv", 
            metadata_path: str = "workspace_metadata.csv", error_on_code_missing_in_metadata=True) -> None:
    """
    Load workspaces from secrets and metadata files.
    
    Args:
      secrets_path: Path to the CSV file with workspace connection information
      metadata_path: Path to the CSV file with workspace metadata
      error_on_code_missing_in_metadata: If True, raise an error if a workspace code in secrets is not found in metadata
    """
    # Load secrets first
    try:
      secrets_df = pd.read_csv(secrets_path)
      logging.info("Secrets file loaded with %d workspaces.", len(secrets_df))
      
      # Verify required columns exist
      required_columns = ['workspace_code', 'host', 'token', 'active']
      missing_columns = [col for col in required_columns if col not in secrets_df.columns]
      
      if missing_columns:
        raise ValueError(f"Missing required columns in secrets file: {', '.join(missing_columns)}")
      
      # Load metadata if available
      try:
        metadata_df = pd.read_csv(metadata_path)
        logging.info("Metadata file loaded with %d workspaces.", len(metadata_df))
        logging.info("Metadata columns identified: %s", ", ".join(metadata_df.columns))
        metadata_dict = {row['workspace_code']: row.to_dict() 
                for _, row in metadata_df.iterrows()}
      except (FileNotFoundError, pd.errors.EmptyDataError):
        metadata_dict = {}
        logging.info("Metadata file not found or empty. Proceeding without metadata.")
      
      # Compare the number of workspaces in secrets and metadata
      if len(secrets_df) != len(metadata_dict):
        if error_on_code_missing_in_metadata:
          logging.error("Number of workspaces in secrets (%d) and metadata (%d) files differ.", 
                        len(secrets_df), len(metadata_dict))
          raise ValueError("Number of workspaces in secrets and metadata files differ.")
        else:
          logging.warning("Number of workspaces in secrets (%d) and metadata (%d) files differ.", 
                          len(secrets_df), len(metadata_dict))  
      # Create workspace objects
      for _, row in secrets_df.iterrows():
        code = row['workspace_code']

        # Check if the workspace code exists in metadata
        if code not in metadata_dict:
          if error_on_code_missing_in_metadata:
            logging.error("Workspace code %s not found in metadata file.", code)
            raise ValueError(f"Workspace code {code} not found in metadata file.")
          else:
            logging.warning("Workspace code %s not found in metadata file. Using empty metadata.", code)
        workspace = Workspace(
          code=code,
          host=row['host'],
          token=row['token'],
          active=bool(row['active']),
          metadata=metadata_dict.get(code, {})
        )
        # Remove the workspace_code key from metadata to avoid duplication
        if 'workspace_code' in workspace.metadata:
          del workspace.metadata['workspace_code']
        
        self.workspaces.append(workspace)
        logging.debug("Workspace loaded: code=%s, host=%s, active=%s", 
                     workspace.code, workspace.host, workspace.active)
        
    except (FileNotFoundError, pd.errors.EmptyDataError) as e:
      raise ValueError(f"Failed to load workspaces: {e}")
    
  def get_workspace(self, code: str) -> Optional[Workspace]:
    """
    Find a workspace by its code.
    
    Args:
      code: The workspace code to search for
      
    Returns:
      Workspace object if found, None otherwise
    """
    for workspace in self.workspaces:
      if workspace.code == code:
        return workspace
    return None
  
  def get_active_workspaces(self) -> List[Workspace]:
    """Return a list of all active workspaces."""
    return [ws for ws in self.workspaces if ws.active]
  
  def get_inactive_workspaces(self) -> List[Workspace]:
    """Return a list of all inactive workspaces."""
    return [ws for ws in self.workspaces if not ws.active]
  
  def len_inactive_workspaces(self) -> int:
    """Return the number of inactive workspaces."""
    return len(self.get_inactive_workspaces())
  
  def len_active_workspaces(self) -> int:
    """Return the number of active workspaces."""
    return len(self.get_active_workspaces())

  def __len__(self) -> int:
    """Return the number of workspaces, including both active and inactive."""
    return len(self.workspaces)
  
  def __iter__(self):
    """Allow iteration over workspaces."""
    return iter(self.workspaces)
  
  def to_pandas(self) -> pd.DataFrame:
    """
    Convert the workspace list to a pandas DataFrame.
    
    Returns:
      DataFrame with workspace information
    """
    data = [ws.get_metadata() for ws in self.workspaces]
    return pd.DataFrame(data)
