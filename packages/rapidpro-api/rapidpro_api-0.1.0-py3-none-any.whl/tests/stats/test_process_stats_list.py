import pytest
import pandas as pd
from unittest.mock import Mock, patch, MagicMock
from rapidpro_api.stats import ProcessStatsList, ProcessStats
from rapidpro_api.workspaces import Workspace


class TestProcessStatsList:
    
    @pytest.fixture
    def workspace_successful(self):
        """Create a workspace for successful processing."""
        return Workspace(code="success_ws", active=True, host="host.com", token="token", vendor="vendor1")
    
    @pytest.fixture
    def workspace_failed(self):
        """Create a workspace for failed processing."""
        return Workspace(code="failed_ws", active=True, host="host.com", token="token", vendor="vendor2")
    
    @pytest.fixture
    def successful_process_stats(self, workspace_successful):
        """Create a successful ProcessStats instance."""
        stats = ProcessStats(workspace_successful, "/output/path", continue_processing=True)
        # Simulate some processing activity
        stats.start_file_processing()
        stats.end_file_processing(100)  # 100 rows processed
        stats.start_file_processing()
        stats.end_file_processing(200)  # 200 more rows processed
        stats.record_success("Processing completed successfully")
        return stats
    
    @pytest.fixture
    def failed_process_stats(self, workspace_failed):
        """Create a failed ProcessStats instance."""
        stats = ProcessStats(workspace_failed, "/output/path", continue_processing=False)
        # Simulate some processing activity before failure
        stats.start_file_processing()
        stats.end_file_processing(50)  # 50 rows processed before failure
        stats.record_failure("Database connection failed")
        return stats
    
    @pytest.fixture
    def stats_list(self):
        """Create a fresh ProcessStatsList instance."""
        return ProcessStatsList("test_dataset", "test_action")
    
    def test_init_default_values(self):
        dataset = "flows"
        action = "process_all"
        
        stats_list = ProcessStatsList(dataset, action)
        
        assert stats_list.dataset == dataset
        assert stats_list.action == action
        assert stats_list.workspace_stats == []
        assert stats_list.processed_ok == []
        assert stats_list.processed_error == []
    
    def test_add_stats_successful_processing(self, stats_list, successful_process_stats):
        stats_list.add_stats(successful_process_stats)
        
        assert len(stats_list.workspace_stats) == 1
        assert len(stats_list.processed_ok) == 1
        assert len(stats_list.processed_error) == 0
        assert stats_list.processed_ok[0] == "success_ws"
    
    def test_add_stats_failed_processing(self, stats_list, failed_process_stats):
        stats_list.add_stats(failed_process_stats)
        
        assert len(stats_list.workspace_stats) == 1
        assert len(stats_list.processed_ok) == 0
        assert len(stats_list.processed_error) == 1
        assert stats_list.processed_error[0] == "failed_ws"
    
    def test_add_stats_mixed_processing(self, stats_list, successful_process_stats, failed_process_stats):
        stats_list.add_stats(successful_process_stats)
        stats_list.add_stats(failed_process_stats)
        
        assert len(stats_list.workspace_stats) == 2
        assert len(stats_list.processed_ok) == 1
        assert len(stats_list.processed_error) == 1
        assert "success_ws" in stats_list.processed_ok
        assert "failed_ws" in stats_list.processed_error
    
    def test_get_successful_workspaces_empty(self, stats_list):
        result = stats_list.get_successful_workspaces()
        
        assert result == []
        assert isinstance(result, list)
    
    def test_get_successful_workspaces_with_data(self, stats_list, successful_process_stats):
        stats_list.add_stats(successful_process_stats)
        
        result = stats_list.get_successful_workspaces()
        
        assert result == ["success_ws"]
        # Verify it returns a copy, not the original list
        result.append("modified")
        assert len(stats_list.processed_ok) == 1
    
    def test_get_failed_workspaces_empty(self, stats_list):
        result = stats_list.get_failed_workspaces()
        
        assert result == []
        assert isinstance(result, list)
    
    def test_get_failed_workspaces_with_data(self, stats_list, failed_process_stats):
        stats_list.add_stats(failed_process_stats)
        
        result = stats_list.get_failed_workspaces()
        
        assert result == ["failed_ws"]
        # Verify it returns a copy, not the original list
        result.append("modified")
        assert len(stats_list.processed_error) == 1
    
    def test_get_total_count_empty(self, stats_list):
        assert stats_list.get_total_count() == 0
    
    def test_get_total_count_with_data(self, stats_list, successful_process_stats, failed_process_stats):
        stats_list.add_stats(successful_process_stats)
        stats_list.add_stats(failed_process_stats)
        
        assert stats_list.get_total_count() == 2
    
    def test_get_success_count_empty(self, stats_list):
        assert stats_list.get_success_count() == 0
    
    def test_get_success_count_with_data(self, stats_list, successful_process_stats, failed_process_stats):
        stats_list.add_stats(successful_process_stats)
        stats_list.add_stats(failed_process_stats)
        
        assert stats_list.get_success_count() == 1
    
    def test_get_failure_count_empty(self, stats_list):
        assert stats_list.get_failure_count() == 0
    
    def test_get_failure_count_with_data(self, stats_list, successful_process_stats, failed_process_stats):
        stats_list.add_stats(successful_process_stats)
        stats_list.add_stats(failed_process_stats)
        
        assert stats_list.get_failure_count() == 1
    
    def test_get_success_rate_empty(self, stats_list):
        assert stats_list.get_success_rate() == 0.0
    
    def test_get_success_rate_all_successful(self, stats_list):
        # Create multiple successful processing operations
        for i in range(3):
            ws = Workspace(code=f"ws_{i}", active=True, host="host", token="token", vendor="vendor")
            process_stats = ProcessStats(ws, "/output", continue_processing=False)
            process_stats.record_success()
            stats_list.add_stats(process_stats)
        
        assert stats_list.get_success_rate() == 100.0
    
    def test_get_success_rate_all_failed(self, stats_list):
        # Create multiple failed processing operations
        for i in range(3):
            ws = Workspace(code=f"ws_{i}", active=True, host="host", token="token", vendor="vendor")
            process_stats = ProcessStats(ws, "/output", continue_processing=False)
            process_stats.record_failure("Processing error")
            stats_list.add_stats(process_stats)
        
        assert stats_list.get_success_rate() == 0.0
    
    def test_get_success_rate_mixed(self, stats_list):
        # Create 2 successful and 3 failed processing operations (40% success rate)
        for i in range(2):
            ws = Workspace(code=f"success_{i}", active=True, host="host", token="token", vendor="vendor")
            process_stats = ProcessStats(ws, "/output", continue_processing=False)
            process_stats.record_success()
            stats_list.add_stats(process_stats)
        
        for i in range(3):
            ws = Workspace(code=f"failed_{i}", active=True, host="host", token="token", vendor="vendor")
            process_stats = ProcessStats(ws, "/output", continue_processing=False)
            process_stats.record_failure("Processing error")
            stats_list.add_stats(process_stats)
        
        assert stats_list.get_success_rate() == 40.0
    
    def test_get_total_files_processed_empty(self, stats_list):
        assert stats_list.get_total_files_processed() == 0
    
    def test_get_total_files_processed_with_data(self, stats_list, successful_process_stats, failed_process_stats):
        stats_list.add_stats(successful_process_stats)  # 2 files processed
        stats_list.add_stats(failed_process_stats)      # 1 file processed
        
        assert stats_list.get_total_files_processed() == 3
    
    def test_get_total_rows_processed_empty(self, stats_list):
        assert stats_list.get_total_rows_processed() == 0
    
    def test_get_total_rows_processed_with_data(self, stats_list, successful_process_stats, failed_process_stats):
        stats_list.add_stats(successful_process_stats)  # 300 rows processed (100 + 200)
        stats_list.add_stats(failed_process_stats)      # 50 rows processed
        
        assert stats_list.get_total_rows_processed() == 350
    
    def test_get_total_processing_time(self, stats_list, successful_process_stats, failed_process_stats):
        stats_list.add_stats(successful_process_stats)
        stats_list.add_stats(failed_process_stats)
        
        total_time = stats_list.get_total_processing_time()
        assert total_time >= 0  # Should be non-negative
        assert isinstance(total_time, float)
    
    def test_get_average_processing_rate_empty(self, stats_list):
        assert stats_list.get_average_processing_rate() == 0.0
    
    def test_get_average_processing_rate_no_successful(self, stats_list, failed_process_stats):
        stats_list.add_stats(failed_process_stats)
        
        assert stats_list.get_average_processing_rate() == 0.0
    
    def test_get_processing_summary_by_workspace_empty(self, stats_list):
        result = stats_list.get_processing_summary_by_workspace()
        
        assert result == []
        assert isinstance(result, list)
    
    def test_get_processing_summary_by_workspace_with_data(self, stats_list, successful_process_stats, failed_process_stats):
        stats_list.add_stats(successful_process_stats)
        stats_list.add_stats(failed_process_stats)
        
        summaries = stats_list.get_processing_summary_by_workspace()
        
        assert len(summaries) == 2
        assert all(isinstance(summary, dict) for summary in summaries)
        
        # Check required fields
        for summary in summaries:
            required_fields = ["workspace_code", "completed", "files_processed", "rows_processed", "processing_time", "processing_rate"]
            assert all(field in summary for field in required_fields)
        
        # Check specific values
        success_summary = next(s for s in summaries if s["workspace_code"] == "success_ws")
        failed_summary = next(s for s in summaries if s["workspace_code"] == "failed_ws")
        
        assert success_summary["completed"] is True
        assert failed_summary["completed"] is False
        assert success_summary["files_processed"] == 2
        assert failed_summary["files_processed"] == 1
        assert success_summary["rows_processed"] == 300
        assert failed_summary["rows_processed"] == 50
    
    @patch('rapidpro_api.stats.process_stats_list.write_deltalake')
    @patch('rapidpro_api.stats.process_stats_list.logging')
    def test_save_stats_to_delta_empty(self, mock_logging, mock_write_deltalake, stats_list):
        delta_path = "/path/to/delta"
        
        stats_list.save_stats_to_delta(delta_path)
        
        mock_logging.warning.assert_called_once_with("No processing stats to save")
        mock_write_deltalake.assert_not_called()
    
    @patch('rapidpro_api.stats.process_stats_list.write_deltalake')
    @patch('rapidpro_api.stats.process_stats_list.logging')
    @patch('rapidpro_api.stats.process_stats_list.pd.DataFrame')
    def test_save_stats_to_delta_with_data(self, mock_dataframe, mock_logging, mock_write_deltalake, 
                                          stats_list, successful_process_stats):
        delta_path = "/path/to/delta"
        mock_df = Mock()
        mock_dataframe.return_value = mock_df
        
        stats_list.add_stats(successful_process_stats)
        stats_list.save_stats_to_delta(delta_path)
        
        # Verify DataFrame was created with correct data
        mock_dataframe.assert_called_once()
        call_args = mock_dataframe.call_args[0][0]
        assert len(call_args) == 1  # One stats dict
        assert isinstance(call_args[0], dict)
        
        # Verify logging and write_deltalake were called
        mock_logging.info.assert_called_once_with("Saving processing stats to %s...", delta_path)
        mock_write_deltalake.assert_called_once_with(
            table_or_uri=delta_path, 
            data=mock_df, 
            mode="append"
        )
    
    def test_get_summary_empty(self, stats_list):
        summary = stats_list.get_summary()
        
        expected = {
            "dataset": "test_dataset",
            "action": "test_action",
            "total_workspaces": 0,
            "successful_processing": 0,
            "failed_processing": 0,
            "success_rate": 0.0,
            "total_files_processed": 0,
            "total_rows_processed": 0,
            "total_processing_time": 0.0,
            "average_processing_rate": 0.0,
            "successful_workspaces": [],
            "failed_workspaces": []
        }
        
        assert summary == expected
    
    def test_get_summary_with_data(self, stats_list, successful_process_stats, failed_process_stats):
        stats_list.add_stats(successful_process_stats)
        stats_list.add_stats(failed_process_stats)
        
        summary = stats_list.get_summary()
        
        assert summary["dataset"] == "test_dataset"
        assert summary["action"] == "test_action"
        assert summary["total_workspaces"] == 2
        assert summary["successful_processing"] == 1
        assert summary["failed_processing"] == 1
        assert summary["success_rate"] == 50.0
        assert summary["total_files_processed"] == 3
        assert summary["total_rows_processed"] == 350
        assert summary["total_processing_time"] > 0
        assert summary["average_processing_rate"] >= 0
        assert summary["successful_workspaces"] == ["success_ws"]
        assert summary["failed_workspaces"] == ["failed_ws"]
    
    def test_multiple_operations_consistency(self, stats_list):
        """Test that multiple operations maintain consistency."""
        workspaces_data = [
            ("ws1", True),   # successful
            ("ws2", False),  # failed
            ("ws3", True),   # successful
            ("ws4", False),  # failed
            ("ws5", True),   # successful
        ]
        
        for ws_code, should_succeed in workspaces_data:
            ws = Workspace(code=ws_code, active=True, host="host", token="token", vendor="vendor")
            process_stats = ProcessStats(ws, "/output", continue_processing=False)
            
            # Simulate some processing
            process_stats.start_file_processing()
            process_stats.end_file_processing(100)
            
            if should_succeed:
                process_stats.record_success()
            else:
                process_stats.record_failure("Test error")
            
            stats_list.add_stats(process_stats)
        
        # Verify all counts are consistent
        assert stats_list.get_total_count() == 5
        assert stats_list.get_success_count() == 3
        assert stats_list.get_failure_count() == 2
        assert stats_list.get_success_rate() == 60.0
        
        # Verify workspace lists
        successful = stats_list.get_successful_workspaces()
        failed = stats_list.get_failed_workspaces()
        
        assert len(successful) == 3
        assert len(failed) == 2
        assert set(successful) == {"ws1", "ws3", "ws5"}
        assert set(failed) == {"ws2", "ws4"}
        
        # Verify aggregate metrics
        assert stats_list.get_total_files_processed() == 5
        assert stats_list.get_total_rows_processed() == 500
        
        # Verify summary
        summary = stats_list.get_summary()
        assert summary["total_workspaces"] == 5
        assert summary["successful_processing"] == 3
        assert summary["failed_processing"] == 2
        assert summary["success_rate"] == 60.0
    
    def test_edge_case_single_successful_processing(self, stats_list, successful_process_stats):
        stats_list.add_stats(successful_process_stats)
        
        assert stats_list.get_success_rate() == 100.0
        assert stats_list.get_total_count() == 1
        assert stats_list.get_success_count() == 1
        assert stats_list.get_failure_count() == 0
    
    def test_edge_case_single_failed_processing(self, stats_list, failed_process_stats):
        stats_list.add_stats(failed_process_stats)
        
        assert stats_list.get_success_rate() == 0.0
        assert stats_list.get_total_count() == 1
        assert stats_list.get_success_count() == 0
        assert stats_list.get_failure_count() == 1
    
    def test_workspace_stats_preservation(self, stats_list, successful_process_stats, failed_process_stats):
        """Test that original ProcessStats objects are preserved correctly."""
        stats_list.add_stats(successful_process_stats)
        stats_list.add_stats(failed_process_stats)
        
        # Verify that the original objects are stored
        assert len(stats_list.workspace_stats) == 2
        assert stats_list.workspace_stats[0] is successful_process_stats
        assert stats_list.workspace_stats[1] is failed_process_stats
        
        # Verify that we can still access the original functionality
        assert stats_list.workspace_stats[0].completed is True
        assert stats_list.workspace_stats[1].completed is False
        assert stats_list.workspace_stats[0].ws_code == "success_ws"
        assert stats_list.workspace_stats[1].ws_code == "failed_ws"
    
    def test_dataset_action_immutability(self):
        """Test that dataset and action are set correctly and remain unchanged."""
        dataset = "contacts"
        action = "process_update"
        
        stats_list = ProcessStatsList(dataset, action)
        
        assert stats_list.dataset == dataset
        assert stats_list.action == action
        
        # Verify they appear in summary
        summary = stats_list.get_summary()
        assert summary["dataset"] == dataset
        assert summary["action"] == action
    
    def test_get_top_performers_empty(self, stats_list):
        result = stats_list.get_top_performers(3)
        
        assert result == []
        assert isinstance(result, list)
    
    def test_get_top_performers_with_data(self, stats_list):
        # Create workspaces with different processing rates
        rates_data = [("fast_ws", 1000), ("medium_ws", 500), ("slow_ws", 100)]
        
        for ws_code, expected_rate in rates_data:
            ws = Workspace(code=ws_code, active=True, host="host", token="token", vendor="vendor")
            process_stats = ProcessStats(ws, "/output", continue_processing=False)
            # Mock processing rate by setting appropriate stats
            process_stats.stats.count("rows_processed", expected_rate)
            process_stats.stats.start_timer("total_processing_time")
            # Simulate 1 second processing time for predictable rates
            process_stats.stats._timers["total_processing_time"]["end"] = (
                process_stats.stats._timers["total_processing_time"]["start"] + 1.0
            )
            process_stats.record_success()
            stats_list.add_stats(process_stats)
        
        top_performers = stats_list.get_top_performers(2)
        
        assert len(top_performers) == 2
        # Should be sorted by processing rate (descending)
        assert top_performers[0]["workspace_code"] == "fast_ws"
        assert top_performers[1]["workspace_code"] == "medium_ws"
    
    def test_get_slowest_performers_empty(self, stats_list):
        result = stats_list.get_slowest_performers(3)
        
        assert result == []
        assert isinstance(result, list)
    
    def test_get_slowest_performers_with_data(self, stats_list):
        # Create workspaces with different processing rates
        rates_data = [("fast_ws", 1000), ("medium_ws", 500), ("slow_ws", 100)]
        
        for ws_code, expected_rate in rates_data:
            ws = Workspace(code=ws_code, active=True, host="host", token="token", vendor="vendor")
            process_stats = ProcessStats(ws, "/output", continue_processing=False)
            # Mock processing rate by setting appropriate stats
            process_stats.stats.count("rows_processed", expected_rate)
            process_stats.stats.start_timer("total_processing_time")
            # Simulate 1 second processing time for predictable rates
            process_stats.stats._timers["total_processing_time"]["end"] = (
                process_stats.stats._timers["total_processing_time"]["start"] + 1.0
            )
            process_stats.record_success()
            stats_list.add_stats(process_stats)
        
        slowest_performers = stats_list.get_slowest_performers(2)
        
        assert len(slowest_performers) == 2
        # Should be sorted by processing rate (ascending)
        assert slowest_performers[0]["workspace_code"] == "slow_ws"
        assert slowest_performers[1]["workspace_code"] == "medium_ws"
    
    @patch('rapidpro_api.stats.process_stats_list.write_deltalake')
    def test_save_stats_integration_with_real_data(self, mock_write_deltalake, stats_list):
        """Test save_stats_to_delta with real ProcessStats data."""
        # Create real workspace and stats
        ws = Workspace(code="integration_test", active=True, host="test.host", token="token", vendor="test")
        process_stats = ProcessStats(ws, "/integration/output", continue_processing=True)
        
        # Simulate processing workflow
        process_stats.start_file_processing()
        process_stats.end_file_processing(150)
        process_stats.set_comment("Integration test processing")
        process_stats.record_success("Integration test completed")
        
        stats_list.add_stats(process_stats)
        delta_path = "/test/delta/path"
        
        # Call the method
        stats_list.save_stats_to_delta(delta_path)
        
        # Verify write_deltalake was called
        mock_write_deltalake.assert_called_once()
        call_args, call_kwargs = mock_write_deltalake.call_args
        
        # Verify the DataFrame contains expected data
        df_data = call_kwargs['data']
        assert isinstance(df_data, pd.DataFrame)
        assert len(df_data) == 1
        
        # Verify some key columns exist
        row = df_data.iloc[0]
        assert row['workspace_code'] == 'integration_test'
        assert row['completed_processing'] == 'True'
        assert row['continue_processing'] == 'True'
        assert row['output_path'] == '/integration/output'
        assert row['rows_processed'] == 150
        assert row['files_processed'] == 1
    
    def test_str_representation(self, stats_list, successful_process_stats, failed_process_stats):
        """Test the string representation of ProcessStatsList."""
        stats_list.add_stats(successful_process_stats)
        stats_list.add_stats(failed_process_stats)
        
        str_repr = str(stats_list)
        
        assert "ProcessStatsList" in str_repr
        assert "test_dataset" in str_repr
        assert "test_action" in str_repr
        assert "total=2" in str_repr
        assert "successful=1" in str_repr
        assert "failed=1" in str_repr
        assert "success_rate=50.0%" in str_repr