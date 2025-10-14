import pandas as pd
import logging
from deltalake import write_deltalake
from typing import List, Dict, Any
from rapidpro_api.stats import ProcessStats


class ProcessStatsList:
    """
    Manages a collection of ProcessStats for multiple workspaces.
    
    This class provides functionality to:
    - Collect and manage processing statistics from multiple workspaces
    - Track successful and failed processing operations
    - Calculate aggregate metrics and success rates
    - Save statistics to Delta Lake tables
    - Generate comprehensive summaries
    
    Example usage:
        # Initialize the stats list
        stats_list = ProcessStatsList("flows", "process_all")
        
        # Process workspaces and collect stats
        for workspace in workspaces:
            success, process_stats = process_workspace_data(workspace)
            stats_list.add_stats(process_stats)
        
        # Get summary and save results
        summary = stats_list.get_summary()
        stats_list.save_stats_to_delta("/path/to/stats/table")
        
        # Print results
        print(f"Processed {summary['successful_processing']} workspaces successfully")
        print(f"Failed to process {summary['failed_processing']} workspaces")
    """
    
    def __init__(self, dataset: str, action: str):
        """
        Initialize the processing stats list.
        
        Args:
            dataset: Name of the dataset being processed (e.g., "flows", "contacts")
            action: Action being performed (e.g., "process_all", "process_update")
        """
        self.dataset = dataset
        self.action = action
        self.workspace_stats: List[ProcessStats] = []
        self.processed_ok: List[str] = []
        self.processed_error: List[str] = []
    
    def add_stats(self, process_stats: ProcessStats):
        """
        Add a ProcessStats instance to the collection.
        
        Args:
            process_stats: The ProcessStats instance to add
        """
        self.workspace_stats.append(process_stats)
        
        if process_stats.completed:
            self.processed_ok.append(process_stats.ws_code)
        else:
            self.processed_error.append(process_stats.ws_code)
    
    def get_successful_workspaces(self) -> List[str]:
        """Get list of successfully processed workspace codes."""
        return self.processed_ok.copy()
    
    def get_failed_workspaces(self) -> List[str]:
        """Get list of failed workspace codes."""
        return self.processed_error.copy()
    
    def get_total_count(self) -> int:
        """Get total number of processed workspaces."""
        return len(self.workspace_stats)
    
    def get_success_count(self) -> int:
        """Get number of successful processing operations."""
        return len(self.processed_ok)
    
    def get_failure_count(self) -> int:
        """Get number of failed processing operations."""
        return len(self.processed_error)
    
    def get_success_rate(self) -> float:
        """Get success rate as a percentage."""
        total = self.get_total_count()
        return (self.get_success_count() / total * 100) if total > 0 else 0.0
    
    def get_total_files_processed(self) -> int:
        """Get total number of files processed across all workspaces."""
        return sum(stats.get_files_processed_count() for stats in self.workspace_stats)
    
    def get_total_rows_processed(self) -> int:
        """Get total number of rows processed across all workspaces."""
        return sum(stats.get_rows_processed_count() for stats in self.workspace_stats)
    
    def get_total_processing_time(self) -> float:
        """Get total processing time across all workspaces in seconds."""
        return sum(stats.get_total_processing_time() for stats in self.workspace_stats)
    
    def get_average_processing_rate(self) -> float:
        """
        Get average processing rate across all successful workspaces in rows per second.
        
        Returns:
            Average rows per second, or 0.0 if no successful processing
        """
        successful_stats = [stats for stats in self.workspace_stats if stats.completed]
        if not successful_stats:
            return 0.0
        
        rates = []
        for stats in successful_stats:
            rate = stats.get_processing_rate()
            if rate is not None and rate > 0:
                rates.append(rate)
        
        return sum(rates) / len(rates) if rates else 0.0
    
    def get_processing_summary_by_workspace(self) -> List[Dict[str, Any]]:
        """
        Get a summary of processing statistics for each workspace.
        
        Returns:
            List of dictionaries with workspace processing summaries
        """
        summaries = []
        for stats in self.workspace_stats:
            summaries.append({
                "workspace_code": stats.ws_code,
                "completed": stats.completed,
                "files_processed": stats.get_files_processed_count(),
                "rows_processed": stats.get_rows_processed_count(),
                "processing_time": stats.get_total_processing_time(),
                "processing_rate": stats.get_processing_rate()
            })
        return summaries
    
    def save_stats_to_delta(self, delta_path: str):
        """
        Save all collected stats to a Delta Lake table.
        
        Args:
            delta_path: Path to the Delta Lake table
        """
        if not self.workspace_stats:
            logging.warning("No processing stats to save")
            return
        
        stats_df = pd.DataFrame([ws_stats.to_dict() for ws_stats in self.workspace_stats])
        logging.info("Saving processing stats to %s...", delta_path)
        write_deltalake(table_or_uri=delta_path, data=stats_df, mode="append")
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get a comprehensive summary of processing statistics.
        
        Returns:
            Dictionary containing summary statistics
        """
        return {
            "dataset": self.dataset,
            "action": self.action,
            "total_workspaces": self.get_total_count(),
            "successful_processing": self.get_success_count(),
            "failed_processing": self.get_failure_count(),
            "success_rate": self.get_success_rate(),
            "total_files_processed": self.get_total_files_processed(),
            "total_rows_processed": self.get_total_rows_processed(),
            "total_processing_time": self.get_total_processing_time(),
            "average_processing_rate": self.get_average_processing_rate(),
            "successful_workspaces": self.get_successful_workspaces(),
            "failed_workspaces": self.get_failed_workspaces()
        }
    
    def get_stats_dataframe(self) -> pd.DataFrame:
        """
        Get all stats as a pandas DataFrame.
        
        Returns:
            DataFrame containing all workspace processing statistics
        """
        if not self.workspace_stats:
            return pd.DataFrame()
        return pd.DataFrame([ws_stats.to_dict() for ws_stats in self.workspace_stats])
    
    def print_summary(self):
        """Print a formatted summary to the console."""
        summary = self.get_summary()
        print(f"\n=== Processing Summary for {summary['dataset']} - {summary['action']} ===")
        print(f"Total workspaces processed: {summary['total_workspaces']}")
        print(f"Successful processing: {summary['successful_processing']}")
        print(f"Failed processing: {summary['failed_processing']}")
        print(f"Success rate: {summary['success_rate']:.1f}%")
        print(f"Total files processed: {summary['total_files_processed']}")
        print(f"Total rows processed: {summary['total_rows_processed']:,}")
        print(f"Total processing time: {summary['total_processing_time']:.2f} seconds")
        print(f"Average processing rate: {summary['average_processing_rate']:.2f} rows/second")
        
        if summary['successful_workspaces']:
            print(f"Successful workspaces: {', '.join(summary['successful_workspaces'])}")
        if summary['failed_workspaces']:
            print(f"Failed workspaces: {', '.join(summary['failed_workspaces'])}")
    
    def print_detailed_summary(self):
        """Print a detailed summary including per-workspace statistics."""
        self.print_summary()
        
        workspace_summaries = self.get_processing_summary_by_workspace()
        if workspace_summaries:
            print(f"\n=== Per-Workspace Details ===")
            for ws_summary in workspace_summaries:
                status = "✅" if ws_summary['completed'] else "❌"
                rate_str = f"{ws_summary['processing_rate']:.2f}" if ws_summary['processing_rate'] else "N/A"
                print(f"{status} {ws_summary['workspace_code']}: "
                      f"{ws_summary['files_processed']} files, "
                      f"{ws_summary['rows_processed']:,} rows, "
                      f"{ws_summary['processing_time']:.2f}s, "
                      f"{rate_str} rows/s")
    
    def get_top_performers(self, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get the top performing workspaces by processing rate.
        
        Args:
            limit: Maximum number of workspaces to return
            
        Returns:
            List of workspace summaries sorted by processing rate (descending)
        """
        summaries = self.get_processing_summary_by_workspace()
        # Filter successful workspaces with valid processing rates
        successful_summaries = [
            s for s in summaries 
            if s['completed'] and s['processing_rate'] is not None and s['processing_rate'] > 0
        ]
        # Sort by processing rate in descending order
        sorted_summaries = sorted(successful_summaries, key=lambda x: x['processing_rate'], reverse=True)
        return sorted_summaries[:limit]
    
    def get_slowest_performers(self, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get the slowest performing workspaces by processing rate.
        
        Args:
            limit: Maximum number of workspaces to return
            
        Returns:
            List of workspace summaries sorted by processing rate (ascending)
        """
        summaries = self.get_processing_summary_by_workspace()
        # Filter successful workspaces with valid processing rates
        successful_summaries = [
            s for s in summaries 
            if s['completed'] and s['processing_rate'] is not None and s['processing_rate'] > 0
        ]
        # Sort by processing rate in ascending order
        sorted_summaries = sorted(successful_summaries, key=lambda x: x['processing_rate'])
        return sorted_summaries[:limit]
    
    def __str__(self) -> str:
        """Return a string representation of the processing stats list."""
        return (f"ProcessStatsList(dataset={self.dataset}, action={self.action}, "
                f"total={self.get_total_count()}, successful={self.get_success_count()}, "
                f"failed={self.get_failure_count()}, success_rate={self.get_success_rate():.1f}%)")