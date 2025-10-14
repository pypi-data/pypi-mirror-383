import pytest
import pandas as pd
from unittest.mock import Mock, patch, MagicMock
from rapidpro_api.stats import DownloadStatsList, DownloadStats
from rapidpro_api.workspaces import Workspace


class TestDownloadStatsList:
    
    @pytest.fixture
    def workspace_successful(self):
        """Create a workspace for successful downloads."""
        return Workspace(code="success_ws", active=True, host="host.com", token="token", vendor="vendor1")
    
    @pytest.fixture
    def workspace_failed(self):
        """Create a workspace for failed downloads."""
        return Workspace(code="failed_ws", active=True, host="host.com", token="token", vendor="vendor2")
    
    @pytest.fixture
    def successful_download_stats(self, workspace_successful):
        """Create a successful DownloadStats instance."""
        stats = DownloadStats(workspace_successful, 3, "/data/folder")
        stats.record_success()
        return stats
    
    @pytest.fixture
    def failed_download_stats(self, workspace_failed):
        """Create a failed DownloadStats instance."""
        stats = DownloadStats(workspace_failed, 3, "/data/folder")
        stats.record_failure("Connection timeout")
        return stats
    
    @pytest.fixture
    def stats_list(self):
        """Create a fresh DownloadStatsList instance."""
        return DownloadStatsList("test_dataset", "test_action")
    
    def test_init_default_values(self):
        dataset = "contacts"
        action = "download_all"
        
        stats_list = DownloadStatsList(dataset, action)
        
        assert stats_list.dataset == dataset
        assert stats_list.action == action
        assert stats_list.workspace_stats == []
        assert stats_list.downloaded_ok == []
        assert stats_list.downloaded_error == []
    
    def test_add_stats_successful_download(self, stats_list, successful_download_stats):
        stats_list.add_stats(successful_download_stats)
        
        assert len(stats_list.workspace_stats) == 1
        assert len(stats_list.downloaded_ok) == 1
        assert len(stats_list.downloaded_error) == 0
        assert stats_list.downloaded_ok[0] == "success_ws"
    
    def test_add_stats_failed_download(self, stats_list, failed_download_stats):
        stats_list.add_stats(failed_download_stats)
        
        assert len(stats_list.workspace_stats) == 1
        assert len(stats_list.downloaded_ok) == 0
        assert len(stats_list.downloaded_error) == 1
        assert stats_list.downloaded_error[0] == "failed_ws"
    
    def test_add_stats_mixed_downloads(self, stats_list, successful_download_stats, failed_download_stats):
        stats_list.add_stats(successful_download_stats)
        stats_list.add_stats(failed_download_stats)
        
        assert len(stats_list.workspace_stats) == 2
        assert len(stats_list.downloaded_ok) == 1
        assert len(stats_list.downloaded_error) == 1
        assert "success_ws" in stats_list.downloaded_ok
        assert "failed_ws" in stats_list.downloaded_error
    
    def test_get_successful_workspaces_empty(self, stats_list):
        result = stats_list.get_successful_workspaces()
        
        assert result == []
        assert isinstance(result, list)
    
    def test_get_successful_workspaces_with_data(self, stats_list, successful_download_stats):
        stats_list.add_stats(successful_download_stats)
        
        result = stats_list.get_successful_workspaces()
        
        assert result == ["success_ws"]
        # Verify it returns a copy, not the original list
        result.append("modified")
        assert len(stats_list.downloaded_ok) == 1
    
    def test_get_failed_workspaces_empty(self, stats_list):
        result = stats_list.get_failed_workspaces()
        
        assert result == []
        assert isinstance(result, list)
    
    def test_get_failed_workspaces_with_data(self, stats_list, failed_download_stats):
        stats_list.add_stats(failed_download_stats)
        
        result = stats_list.get_failed_workspaces()
        
        assert result == ["failed_ws"]
        # Verify it returns a copy, not the original list
        result.append("modified")
        assert len(stats_list.downloaded_error) == 1
    
    def test_get_total_count_empty(self, stats_list):
        assert stats_list.get_total_count() == 0
    
    def test_get_total_count_with_data(self, stats_list, successful_download_stats, failed_download_stats):
        stats_list.add_stats(successful_download_stats)
        stats_list.add_stats(failed_download_stats)
        
        assert stats_list.get_total_count() == 2
    
    def test_get_success_count_empty(self, stats_list):
        assert stats_list.get_success_count() == 0
    
    def test_get_success_count_with_data(self, stats_list, successful_download_stats, failed_download_stats):
        stats_list.add_stats(successful_download_stats)
        stats_list.add_stats(failed_download_stats)
        
        assert stats_list.get_success_count() == 1
    
    def test_get_failure_count_empty(self, stats_list):
        assert stats_list.get_failure_count() == 0
    
    def test_get_failure_count_with_data(self, stats_list, successful_download_stats, failed_download_stats):
        stats_list.add_stats(successful_download_stats)
        stats_list.add_stats(failed_download_stats)
        
        assert stats_list.get_failure_count() == 1
    
    def test_get_success_rate_empty(self, stats_list):
        assert stats_list.get_success_rate() == 0.0
    
    def test_get_success_rate_all_successful(self, stats_list):
        # Create multiple successful downloads
        for i in range(3):
            ws = Workspace(code=f"ws_{i}", active=True, host="host", token="token", vendor="vendor")
            download_stats = DownloadStats(ws, 3, "/data")
            download_stats.record_success()
            stats_list.add_stats(download_stats)
        
        assert stats_list.get_success_rate() == 100.0
    
    def test_get_success_rate_all_failed(self, stats_list):
        # Create multiple failed downloads
        for i in range(3):
            ws = Workspace(code=f"ws_{i}", active=True, host="host", token="token", vendor="vendor")
            download_stats = DownloadStats(ws, 3, "/data")
            download_stats.record_failure("Error")
            stats_list.add_stats(download_stats)
        
        assert stats_list.get_success_rate() == 0.0
    
    def test_get_success_rate_mixed(self, stats_list):
        # Create 2 successful and 3 failed downloads (40% success rate)
        for i in range(2):
            ws = Workspace(code=f"success_{i}", active=True, host="host", token="token", vendor="vendor")
            download_stats = DownloadStats(ws, 3, "/data")
            download_stats.record_success()
            stats_list.add_stats(download_stats)
        
        for i in range(3):
            ws = Workspace(code=f"failed_{i}", active=True, host="host", token="token", vendor="vendor")
            download_stats = DownloadStats(ws, 3, "/data")
            download_stats.record_failure("Error")
            stats_list.add_stats(download_stats)
        
        assert stats_list.get_success_rate() == 40.0
    
    @patch('rapidpro_api.stats.download_stats_list.write_deltalake')
    @patch('rapidpro_api.stats.download_stats_list.logging')
    def test_save_stats_to_delta_empty(self, mock_logging, mock_write_deltalake, stats_list):
        delta_path = "/path/to/delta"
        
        stats_list.save_stats_to_delta(delta_path)
        
        mock_logging.warning.assert_called_once_with("No stats to save")
        mock_write_deltalake.assert_not_called()
    
    @patch('rapidpro_api.stats.download_stats_list.write_deltalake')
    @patch('rapidpro_api.stats.download_stats_list.logging')
    @patch('rapidpro_api.stats.download_stats_list.pd.DataFrame')
    def test_save_stats_to_delta_with_data(self, mock_dataframe, mock_logging, mock_write_deltalake, 
                                          stats_list, successful_download_stats):
        delta_path = "/path/to/delta"
        mock_df = Mock()
        mock_dataframe.return_value = mock_df
        
        stats_list.add_stats(successful_download_stats)
        stats_list.save_stats_to_delta(delta_path)
        
        # Verify DataFrame was created with correct data
        mock_dataframe.assert_called_once()
        call_args = mock_dataframe.call_args[0][0]
        assert len(call_args) == 1  # One stats dict
        assert isinstance(call_args[0], dict)
        
        # Verify logging and write_deltalake were called
        mock_logging.info.assert_called_once_with("Saving stats to %s...", delta_path)
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
            "successful_downloads": 0,
            "failed_downloads": 0,
            "success_rate": 0.0,
            "successful_workspaces": [],
            "failed_workspaces": []
        }
        
        assert summary == expected
    
    def test_get_summary_with_data(self, stats_list, successful_download_stats, failed_download_stats):
        stats_list.add_stats(successful_download_stats)
        stats_list.add_stats(failed_download_stats)
        
        summary = stats_list.get_summary()
        
        expected = {
            "dataset": "test_dataset",
            "action": "test_action",
            "total_workspaces": 2,
            "successful_downloads": 1,
            "failed_downloads": 1,
            "success_rate": 50.0,
            "successful_workspaces": ["success_ws"],
            "failed_workspaces": ["failed_ws"]
        }
        
        assert summary == expected
    
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
            download_stats = DownloadStats(ws, 3, "/data")
            
            if should_succeed:
                download_stats.record_success()
            else:
                download_stats.record_failure("Test error")
            
            stats_list.add_stats(download_stats)
        
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
        
        # Verify summary
        summary = stats_list.get_summary()
        assert summary["total_workspaces"] == 5
        assert summary["successful_downloads"] == 3
        assert summary["failed_downloads"] == 2
        assert summary["success_rate"] == 60.0
    
    def test_edge_case_single_successful_download(self, stats_list, successful_download_stats):
        stats_list.add_stats(successful_download_stats)
        
        assert stats_list.get_success_rate() == 100.0
        assert stats_list.get_total_count() == 1
        assert stats_list.get_success_count() == 1
        assert stats_list.get_failure_count() == 0
    
    def test_edge_case_single_failed_download(self, stats_list, failed_download_stats):
        stats_list.add_stats(failed_download_stats)
        
        assert stats_list.get_success_rate() == 0.0
        assert stats_list.get_total_count() == 1
        assert stats_list.get_success_count() == 0
        assert stats_list.get_failure_count() == 1
    
    def test_workspace_stats_preservation(self, stats_list, successful_download_stats, failed_download_stats):
        """Test that original DownloadStats objects are preserved correctly."""
        stats_list.add_stats(successful_download_stats)
        stats_list.add_stats(failed_download_stats)
        
        # Verify that the original objects are stored
        assert len(stats_list.workspace_stats) == 2
        assert stats_list.workspace_stats[0] is successful_download_stats
        assert stats_list.workspace_stats[1] is failed_download_stats
        
        # Verify that we can still access the original functionality
        assert stats_list.workspace_stats[0].completed is True
        assert stats_list.workspace_stats[1].completed is False
        assert stats_list.workspace_stats[0].ws_code == "success_ws"
        assert stats_list.workspace_stats[1].ws_code == "failed_ws"
    
    def test_dataset_action_immutability(self):
        """Test that dataset and action are set correctly and remain unchanged."""
        dataset = "flows"
        action = "download_update"
        
        stats_list = DownloadStatsList(dataset, action)
        
        assert stats_list.dataset == dataset
        assert stats_list.action == action
        
        # Verify they appear in summary
        summary = stats_list.get_summary()
        assert summary["dataset"] == dataset
        assert summary["action"] == action
    
    @patch('rapidpro_api.stats.download_stats_list.write_deltalake')
    def test_save_stats_integration_with_real_data(self, mock_write_deltalake, stats_list):
        """Test save_stats_to_delta with real DownloadStats data."""
        # Create real workspace and stats
        ws = Workspace(code="integration_test", active=True, host="test.host", token="token", vendor="test")
        download_stats = DownloadStats(ws, 5, "/integration/data")
        download_stats.update_attempt(2)
        download_stats.set_comment("Integration test")
        download_stats.record_success()
        
        stats_list.add_stats(download_stats)
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
        assert row['completed'] == 'True'
        assert row['download_attemps'] == 2
        assert row['comments'] == 'Integration test'