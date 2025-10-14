from rapidpro_api.stats import Stats, DownloadStats
import pandas as pd
from deltalake import write_deltalake, DeltaTable
import logging
from typing import List, Dict, Any, Optional, Tuple


class DownloadStatsList:
    """
    Manages a collection of DownloadStats for multiple workspaces.
    
    Example:
        >>> stats_list = DownloadStatsList("flows", "download")
        >>> download_stats = DownloadStats("WS001", True, 150, 0.5, 1000, 950)
        >>> stats_list.add_stats(download_stats)
        >>> summary = stats_list.get_summary()
        >>> stats_list.save_stats_to_delta("path/to/delta/table")
    """
    
    def __init__(self, dataset: str, action: str):
        """
        Initialize the stats list.
        
        Args:
            dataset: Name of the dataset being processed
            action: Action being performed
        """
        self.dataset = dataset
        self.action = action
        self.workspace_stats: List[DownloadStats] = []
        self.downloaded_ok: List[str] = []
        self.downloaded_error: List[str] = []
    
    def add_stats(self, download_stats: DownloadStats):
        """
        Add a DownloadStats instance to the collection.
        
        Args:
            download_stats: The DownloadStats instance to add
        """
        self.workspace_stats.append(download_stats)
        
        if download_stats.completed:
            self.downloaded_ok.append(download_stats.ws_code)
        else:
            self.downloaded_error.append(download_stats.ws_code)
    
    def get_successful_workspaces(self) -> List[str]:
        """Get list of successfully downloaded workspace codes."""
        return self.downloaded_ok.copy()
    
    def get_failed_workspaces(self) -> List[str]:
        """Get list of failed workspace codes."""
        return self.downloaded_error.copy()
    
    def get_total_count(self) -> int:
        """Get total number of processed workspaces."""
        return len(self.workspace_stats)
    
    def get_success_count(self) -> int:
        """Get number of successful downloads."""
        return len(self.downloaded_ok)
    
    def get_failure_count(self) -> int:
        """Get number of failed downloads."""
        return len(self.downloaded_error)
    
    def get_success_rate(self) -> float:
        """Get success rate as a percentage."""
        total = self.get_total_count()
        return ((self.get_success_count() * 100)/ total ) if total > 0 else 0.0
    
    def save_stats_to_delta(self, delta_path: str):
        """Save all collected stats to a Delta Lake table."""
        if not self.workspace_stats:
            logging.warning("No stats to save")
            return
        
        stats_df = pd.DataFrame([ws_stats.to_dict() for ws_stats in self.workspace_stats])
        logging.info("Saving stats to %s...", delta_path)
        write_deltalake(table_or_uri=delta_path, data=stats_df, mode="append")
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a comprehensive summary of download statistics."""
        return {
            "dataset": self.dataset,
            "action": self.action,
            "total_workspaces": self.get_total_count(),
            "successful_downloads": self.get_success_count(),
            "failed_downloads": self.get_failure_count(),
            "success_rate": self.get_success_rate(),
            "successful_workspaces": self.get_successful_workspaces(),
            "failed_workspaces": self.get_failed_workspaces()
        }
    def __str__(self) -> str:
        """Return a prettified string representation of the download statistics summary."""
        summary = self.get_summary()
        
        lines = [
            f"DownloadStatsList Summary:",
            f"  Dataset: {summary['dataset']}",
            f"  Action: {summary['action']}",
            f"  Total Workspaces: {summary['total_workspaces']}",
            f"  Successful Downloads: {summary['successful_downloads']}",
            f"  Failed Downloads: {summary['failed_downloads']}",
            f"  Success Rate: {summary['success_rate']:.1f}%"
        ]
        
        if summary['successful_workspaces']:
            lines.append(f"  Successful Workspaces: {', '.join(summary['successful_workspaces'])}")
        
        if summary['failed_workspaces']:
            lines.append(f"  Failed Workspaces: {', '.join(summary['failed_workspaces'])}")
        
        return "\n".join(lines)