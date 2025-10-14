import logging
import pandas as pd
from typing import List, Dict, Any, Optional, Tuple
from deltalake import write_deltalake, DeltaTable
from rapidpro_api.stats import Stats

class DownloadStats:
    """
    Encapsulates statistics for a single workspace download.

    Example usage:
        # Initialize workspace and parameters
        workspace = some_workspace_object  # Your workspace object
        max_retries = 3
        data_folder = "/path/to/data"
        
        # Create download stats tracker
        download_stats = DownloadStats(workspace, max_retries, data_folder)
        
        # Track download attempts
        for attempt in range(1, max_retries + 1):
            download_stats.update_attempt(attempt)
            try:
                # Perform download operation here
                # ... download logic ...
                
                # On success
                download_stats.record_success()
                download_stats.set_comment("Download completed successfully")
                break
                
            except Exception as e:
                if attempt == max_retries:
                    # Final failure
                    download_stats.record_failure(str(e))
                    download_stats.set_comment("Max retries exceeded")
                
        # Get final statistics
        stats_dict = download_stats.to_dict()
        print(f"Download completed: {download_stats.completed}")
        print(f"Stats: {stats_dict}")
    """
    
    def __init__(self, ws, retries: int, base_folder: str):
        """
        Initialize stats for a single workspace download.
        
        Args:
            ws: Workspace object
            retries: Maximum number of retries
            base_folder: Base folder for data storage
        """
        self.stats = Stats()
        self.ws_code = ws.code
        self.completed = False
        
        # Set initial attributes
        self.stats.set_attribute("workspace_code", ws.code)
        self.stats.set_attribute("workspace_active", ws.active)
        self.stats.set_attribute("workspace_vendor", ws.vendor)
        self.stats.set_attribute("data_folder", base_folder)
        self.stats.set_attribute("max_retries", retries)
        self.stats.set_attribute("completed", "False")
        self.stats.set_attribute("comments", "")
        self.stats.start_timer("download_time")
        self.stats.set_attribute("download_attemps", 0)
        self.stats.set_attribute("exception", "")
        self.stats.set_attribute("exception_type", "")
    
    def update_attempt(self, attempt: int):
        """Update the download attempt count."""
        self.stats.set_attribute("download_attemps", attempt)
    
    def record_success(self):
        """Record a successful download completion."""
        self.completed = True
        self.stats.set_attribute("completed", "True")
        self.stats.stop_timer("download_time")
    
    def record_failure(self, error_msg: str = "", exception_type: type = None):
        """Record a failed download."""
        self.completed = False
        self.stats.set_attribute("completed", "False")
        self.stats.stop_timer("download_time")
        if error_msg:
            self.set_exception(error_msg, exception_type)
    
    def set_comment(self, comment: str):
        """Set a comment for this download."""
        self.stats.set_attribute("comments", comment)
    
    def set_exception(self, comment: str, exception_type: type = None):
        """Set a comment for this download."""
        self.stats.set_attribute("exception", comment)
        if exception_type:
            self.stats.set_attribute("exception_type", str(exception_type))

   
    def to_dict(self) -> Dict[str, Any]:
        """Convert stats to dictionary."""
        return self.stats.to_dict()
    
    def to_delta(self, delta_path: str):
        """
        Save the stats to a Delta Lake table.
        
        Args:
            delta_path: Path to the Delta Lake table
        """
        df = pd.DataFrame([self.to_dict()])
        write_deltalake(table_or_uri=delta_path, data=df, mode="append")

