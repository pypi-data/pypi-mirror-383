import pytest
from rapidpro_api.stats import DownloadStats
from rapidpro_api.stats import Stats
from rapidpro_api.workspaces import Workspace  # Import the actual Workspace class


class TestDownloadStats:
    
    @pytest.fixture
    def workspace(self):
        # Use actual Workspace class instead of Mock
        ws = Workspace(code="test_ws_001", active=True, host="host.com", token="token", vendor="test_vendor")
        return ws
    
    @pytest.fixture
    def download_stats(self, workspace):
        ds = DownloadStats(workspace, 3, "/test/data/folder")
        return ds
    
    def test_init_default_values(self, workspace):
        retries = 5
        base_folder = "/custom/folder"
        
        stats = DownloadStats(workspace, retries, base_folder)
        
        assert stats.ws_code == "test_ws_001"
        assert stats.completed is False
        assert isinstance(stats.stats, Stats)
    
    def test_init_sets_attributes(self, workspace):
        retries = 3
        base_folder = "/test/folder"
        
        ds = DownloadStats(workspace, retries, base_folder)
        
        # Verify attributes are set in the actual Stats object
        stats_dict = ds.stats.to_dict()
        assert stats_dict["workspace_code"] == "test_ws_001"
        assert stats_dict["workspace_active"] is True
        assert stats_dict["workspace_vendor"] == "test_vendor"
        assert stats_dict["data_folder"] == base_folder
        assert stats_dict["max_retries"] == retries
        assert stats_dict["completed"] == "False"
        assert stats_dict["comments"] == ""
    
    def test_update_attempt(self, download_stats):
        attempt = 2
        
        download_stats.update_attempt(attempt)
        
        stats_dict = download_stats.stats.to_dict()
        assert stats_dict["download_attemps"] == attempt
    
    def test_update_attempt_multiple_calls(self, download_stats):
        download_stats.update_attempt(1)
        download_stats.update_attempt(2)
        download_stats.update_attempt(3)
        
        stats_dict = download_stats.stats.to_dict()
        assert stats_dict["download_attemps"] == 3  # Should have the last value
    
    def test_record_success(self, download_stats):
        download_stats.record_success()
        
        assert download_stats.completed is True
        stats_dict = download_stats.stats.to_dict()
        assert stats_dict["completed"] == "True"
        assert "download_time_elapsed" in stats_dict  # Timer should be stopped and recorded
    
    def test_record_failure_without_message(self, download_stats):
        download_stats.record_failure()
        
        assert download_stats.completed is False
        stats_dict = download_stats.stats.to_dict()
        assert stats_dict["completed"] == "False"
        assert "download_time_elapsed" in stats_dict  # Timer should be stopped and recorded
    
    def test_record_failure_with_message(self, download_stats):
        error_msg = "Connection timeout occurred"
        
        download_stats.record_failure(error_msg)
        
        assert download_stats.completed is False
        stats_dict = download_stats.stats.to_dict()
        assert stats_dict["completed"] == "False"
        assert stats_dict["exception"] == error_msg
        assert "download_time_elapsed" in stats_dict  # Timer should be stopped and recorded
    
    def test_record_failure_with_empty_message(self, download_stats):
        download_stats.record_failure("")
        
        assert download_stats.completed is False
        stats_dict = download_stats.stats.to_dict()
        assert stats_dict["completed"] == "False"
        assert "exception" in stats_dict  # Empty string should not be set
        assert "download_time_elapsed" in stats_dict  # Timer should be stopped and recorded
    
    def test_set_comment(self, download_stats):
        comment = "Download process initiated"
        
        download_stats.set_comment(comment)
        
        stats_dict = download_stats.stats.to_dict()
        assert stats_dict["comments"] == comment
    
    def test_set_comment_empty(self, download_stats):
        download_stats.set_comment("")
        
        stats_dict = download_stats.stats.to_dict()
        assert stats_dict["comments"] == ""
    
    def test_set_comment_special_characters(self, download_stats):
        comment = "Error: Failed to download 'flows.json' - HTTP 404"
        
        download_stats.set_comment(comment)
        
        stats_dict = download_stats.stats.to_dict()
        assert stats_dict["comments"] == comment
    
    def test_to_dict(self, download_stats):
        result = download_stats.to_dict()
        
        assert isinstance(result, dict)
        assert "workspace_code" in result
        assert result["workspace_code"] == "test_ws_001"
        assert "completed" in result
        assert result["completed"] == "False"
    
    def test_complete_download_workflow_success(self, download_stats):
        # Simulate complete successful workflow
        download_stats.update_attempt(1)
        download_stats.set_comment("Starting download")
        download_stats.record_success()
        download_stats.set_comment("Download completed successfully")
        
        assert download_stats.completed is True
        stats_dict = download_stats.stats.to_dict()
        assert stats_dict["download_attemps"] == 1
        assert stats_dict["completed"] == "True"
        assert stats_dict["comments"] == "Download completed successfully"
        assert "download_time_elapsed" in stats_dict
    
    def test_complete_download_workflow_failure_with_retries(self, download_stats):
        # Simulate workflow with retries and final failure
        download_stats.update_attempt(1)
        download_stats.update_attempt(2)
        download_stats.update_attempt(3)
        download_stats.record_failure("Max retries exceeded")
        download_stats.set_comment("Failed after 3 attempts")
        
        assert download_stats.completed is False
        stats_dict = download_stats.stats.to_dict()
        assert stats_dict["download_attemps"] == 3
        assert stats_dict["completed"] == "False"
        assert stats_dict["exception"] == "Max retries exceeded"
        assert stats_dict["comments"] == "Failed after 3 attempts"
        assert "download_time_elapsed" in stats_dict
    
    def test_workspace_properties_integration(self):
        # Test different workspace configurations
        workspace = Workspace(code="prod_ws_999", active=False, host="host", token="token", vendor="custom_vendor")
        
        stats = DownloadStats(workspace, 1, "/prod/data")
        
        assert stats.ws_code == "prod_ws_999"
        stats_dict = stats.stats.to_dict()
        assert stats_dict["workspace_code"] == "prod_ws_999"
        assert stats_dict["workspace_active"] is False
        assert stats_dict["workspace_vendor"] == "custom_vendor"
    
    def test_state_persistence_after_operations(self, download_stats):
        # Verify state is maintained correctly through operations
        initial_completed = download_stats.completed
        
        download_stats.update_attempt(1)
        assert download_stats.completed == initial_completed
        
        download_stats.set_comment("Processing")
        assert download_stats.completed == initial_completed
        
        download_stats.record_success()
        assert download_stats.completed is True
        
        # Reset and test failure path
        download_stats.record_failure("Test error")
        assert download_stats.completed is False
