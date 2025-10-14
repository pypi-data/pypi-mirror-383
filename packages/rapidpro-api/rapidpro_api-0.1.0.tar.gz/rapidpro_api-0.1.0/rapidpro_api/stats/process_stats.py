import pandas as pd
import logging
from deltalake import write_deltalake
from typing import Dict, Any, Optional
from datetime import datetime
from rapidpro_api.stats import Stats

class ProcessStats:
    """
    Encapsulates statistics for a single workspace processing operation.
    
    This class tracks various metrics during data processing including:
    - Files processed and rows processed
    - Time spent on different operations (download, processing, writing, optimization)
    - Processing rates and averages
    - Success/failure status and error information
    
    Example usage:
        # Initialize processing stats
        workspace = some_workspace_object
        output_path = "/path/to/delta/table"
        continue_processing = True
        
        # Create process stats tracker
        process_stats = ProcessStats(workspace, output_path, continue_processing)
        
        # Track processing workflow
        process_stats.start_processing()
        
        # Track file processing
        for file_data in files:
            process_stats.start_file_download()
            # ... download file ...
            process_stats.end_file_download()
            
            process_stats.start_file_processing()
            # ... process file ...
            rows_in_file = len(processed_data)
            process_stats.end_file_processing(rows_in_file)
            
            process_stats.start_file_writing()
            # ... write to delta ...
            process_stats.end_file_writing(columns_count)
        
        # Track optimization (if applicable)
        process_stats.start_optimization()
        # ... perform delta lake optimization ...
        process_stats.end_optimization(files_before, files_after)
        
        # Record completion
        process_stats.record_success("Processing completed successfully")
        
        # Get final statistics
        stats_dict = process_stats.to_dict()
    """
    
    def __init__(self, workspace, output_path: str, continue_processing: bool = False):
        """
        Initialize stats for a single workspace processing operation.
        
        Args:
            workspace: Workspace object being processed
            output_path: Path where processed data will be stored
            continue_processing: Whether this is continuing from previous processing
        """
        self.stats = Stats()
        self.ws_code = workspace.code
        self.completed = False
        
        # Set initial attributes
        self.stats.set_attribute("workspace_code", workspace.code)
        self.stats.set_attribute("workspace_active", workspace.active)
        self.stats.set_attribute("workspace_vendor", workspace.vendor)
        self.stats.set_attribute("continue_processing", str(continue_processing))
        self.stats.set_attribute("output_path", output_path)
        self.stats.set_attribute("completed_processing", "False")
        self.stats.set_attribute("exception_message", "")
        self.stats.set_attribute("comments", "")
        self.stats.set_attribute("last_processed_date", "None")
        
        # Initialize counters
        self.stats.count("files_processed", 0, unit="file")
        self.stats.count("downloaded_bytes", 0, unit="byte")
        self.stats.count("rows_processed", 0, unit="row")
        self.stats.count("columns", 0, unit="column")
        self.stats.count("before_optimization", 0, unit="file")
        self.stats.count("after_optimization", 0, unit="file")
        
        # Set up timers
        self.stats.start_timer("total_processing_time")
        self.stats.set_cumulative_timer("download_time")
        self.stats.set_cumulative_timer("processing_time")
        self.stats.set_cumulative_timer("writing_time")
        self.stats.set_cumulative_timer("optimization_time")
        
        # Set up ratios for performance metrics
        self.stats.set_ratio("avg_time_per_file", "total_processing_time", "files_processed")
        self.stats.set_ratio("avg_rows_per_second", "rows_processed", "total_processing_time")
        self.stats.set_ratio("avg_file_processing_time", "processing_time", "files_processed")
        self.stats.set_ratio("avg_rows_processed_per_second", "rows_processed", "processing_time")
        self.stats.set_ratio("avg_file_download_time", "download_time", "files_processed")
        self.stats.set_ratio("avg_download_speed", "downloaded_bytes", "download_time")
        self.stats.set_ratio("avg_file_size", "downloaded_bytes", "files_processed")
        self.stats.set_ratio("avg_file_writing_time", "writing_time", "files_processed")
        
    
    def set_last_processed_date(self, last_date: Optional[datetime]):
        """
        Set the last processed date for continuing processing.
        
        Args:
            last_date: The last processed date, or None if starting fresh
        """
        if last_date:
            self.stats.set_attribute("last_processed_date", str(last_date))
        else:
            self.stats.set_attribute("last_processed_date", "None")
    
    def start_file_download(self):
        """Start timing file download operation.
        When several files need to be downloaded it accumulates the download time"""
        self.stats.start_cumulative_timer("download_time")
    
    def end_file_download(self, file_size:int = 0, return_last_file_time:Optional[bool] = False) -> float:
        """End timing file download operation.
        When several files need to be downloaded it accumulates the download time each time start_file_download and end_file_download are called.
        Args:
            file_size: Size of the downloaded file in bytes (optional) (>0 to count)
            return_last_file_time: If True, return the elapsed time for this download operation

        Returns:
            Total accumulated time for all files, or the elapsed time for this last file if return_last_file_time is True
        """
        if file_size > 0:
            self.stats.count("downloaded_bytes", file_size)
        return self.stats.end_cumulative_timer("download_time", return_elapsed=return_last_file_time)
        
    
    def start_file_processing(self):
        """Start timing file processing operation."""
        self.stats.start_cumulative_timer("processing_time")
    
    def end_file_processing(self, rows_processed: int, return_last_process_time: Optional[bool] = False ) -> float:
        """
        End timing file processing operation and update row count.
        
        Args:
            rows_processed: Number of rows processed in this file
        """
        self.stats.count("rows_processed", rows_processed)
        self.stats.count("files_processed", 1)
        return self.stats.end_cumulative_timer("processing_time", return_elapsed=return_last_process_time)
    
    def start_file_writing(self):
        """Start timing file writing operation."""
        self.stats.start_cumulative_timer("writing_time")
    
    def end_file_writing(self, columns_count: Optional[int] = None, return_last_write_time:Optional[bool] = False) -> float:
        """
        End timing file writing operation and optionally update column count.
        When several files need to be written it accumulates the writing time each time start_file_writing and end_file_writing are called.

        Args:
            columns_count: Number of columns in the processed data
            return_last_write_time: If True, return the elapsed time for this writing operation
        Returns:
            Total accumulated time for all writing operations, or the elapsed time for this operation if return_last_write_time is True
        """
        if columns_count is not None:
            if self.stats.get_counter_value("columns") == 0:
                self.stats.count("columns", columns_count)
        return self.stats.end_cumulative_timer("writing_time", return_elapsed=return_last_write_time)
    
    def start_optimization(self, unit:str="files"):
        """Start timing delta lake optimization operation."""
        # Update the optimization unit (e.g. files, rows, partitions)
        if unit !="files":
            self.stats.set_counter_unit("before_optimization", unit=unit)
            self.stats.set_counter_unit("after_optimization", unit=unit)
        self.stats.start_cumulative_timer("optimization_time")
    
    def end_optimization(self, before_optimization: int, after_optimization: int, return_last_optimization_time:bool = False) -> float:
        """
        End timing delta lake optimization operation and record file counts.
        
        Args:
            before_optimization: Number of files before optimization
            after_optimization: Number of files after optimization
        """
        self.stats.count("before_optimization", before_optimization)
        self.stats.count("after_optimization", after_optimization)

        return self.stats.end_cumulative_timer("optimization_time", return_elapsed=return_last_optimization_time)
    
    def get_optimization_time(self) -> float:
        """Get the optimization time in seconds."""
        return self.stats.get_elapsed_time("optimization_time")
    
    def get_items_before_optimization(self) -> int:
        """Get the number of items before optimization."""
        return int(self.stats.get_counter_value("before_optimization"))
    
    def get_items_after_optimization(self) -> int:
        """Get the number of items after optimization."""
        return int(self.stats.get_counter_value("after_optimization"))
    
    def record_success(self, comment: str = ""):
        """
        Record successful completion of processing.
        
        Args:
            comment: Optional comment about the processing
        """
        self.completed = True
        self.stats.set_attribute("completed_processing", "True")
        self.stats.stop_timer("total_processing_time")
        if comment:
            self.stats.set_attribute("comments", comment)
    
    def record_failure(self, error_msg: str = "", comment: str = ""):
        """
        Record failed processing.
        
        Args:
            error_msg: Error message that caused the failure
            comment: Additional comment about the failure
        """
        self.completed = False
        self.stats.set_attribute("completed_processing", "False")
        self.stats.stop_timer("total_processing_time")
        if error_msg:
            self.stats.set_attribute("exception_message", error_msg)
        if comment:
            self.stats.set_attribute("comments", comment)
    
    def record_no_data_to_process(self):
        """Record that there was no new data to process (still considered successful)."""
        self.completed = True
        self.stats.set_attribute("completed_processing", "True")
        self.stats.stop_timer("total_processing_time")
        self.stats.set_attribute("comments", "No new data to process")

    def record_skipped_inactive_workspace(self):
        """Record that an inactive workspace was skipped (still considered successful)."""
        self.completed = True
        self.stats.set_attribute("completed_processing", "True")
        self.stats.stop_timer("total_processing_time")
        self.stats.set_attribute("comments", "Skipped never downloaded inactive workspace")

    def set_comment(self, comment: str):
        """
        Set or update the comment field.
        
        Args:
            comment: Comment to set
        """
        self.stats.set_attribute("comments", comment)

    def get_files_processed_count(self) -> int:
        """Get the number of files processed."""
        return int(self.stats.get_counter_value("files_processed"))

    def get_rows_processed_count(self) -> int:
        """Get the number of rows processed."""
        return int(self.stats.get_counter_value("rows_processed"))

    def get_total_processing_time(self) -> float:
        """Get the total processing time in seconds."""
        return self.stats.get_elapsed_time("total_processing_time")

    def get_processing_rate(self) -> Optional[float]:
        """
        Get the processing rate in rows per second.
        
        Returns:
            Rows per second, or None if no data processed
        """
        try:
            return self.stats.calculate_ratio("avg_rows_per_second")
        except ValueError:
            return None

    def to_dict(self) -> Dict[str, Any]:
        """Convert stats to dictionary."""
        return self.stats.to_dict()

    def to_delta(self, delta_path: str):
        """Append the current stats as a new row to a delta table."""
        df = pd.DataFrame([self.to_dict()])
        logging.info(f"Saving stats for workspace {self.ws_code} to {delta_path}...")
        write_deltalake(table_or_uri=delta_path, data=df, mode="append")
    
    def __str__(self) -> str:
        """Return a detailed string representation of the processing stats."""
        files = self.get_files_processed_count()
        rows = self.get_rows_processed_count()
        time = self.get_total_processing_time()
  
        status = "✓ Completed" if self.completed else "✗ Not Completed"
        opt_time = self.get_optimization_time()
        before_opt = self.get_items_before_optimization()
        after_opt = self.get_items_after_optimization()
        
        result = (f"ProcessStats:\n"
            f"  Workspace: {self.ws_code}\n"
            f"  Status: {status}\n"
            f"  Files Processed: {files:,}\n"
            f"  Rows Processed: {rows:,}\n"
            f"  Total Time: {time:.2f}s\n"
            f"  Avg Time/File: {time/files if files > 0 else 0:.2f}s\n"
            f"  Processing Rate: {rows/time if time > 0 else 0:.1f} rows/sec")
        
        if opt_time > 0:
            result += (f"\n  Optimization Time: {opt_time:.2f}s\n"
                  f"  Before Optimization: {before_opt:,}\n"
                  f"  After Optimization: {after_opt:,}")
        
        return result