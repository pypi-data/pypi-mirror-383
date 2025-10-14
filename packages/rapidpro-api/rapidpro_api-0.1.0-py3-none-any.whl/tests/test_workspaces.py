import pytest
import pandas as pd
import os
import tempfile
from unittest.mock import patch, mock_open
from io import StringIO
from rapidpro_api.workspaces import Workspace, WorkspaceList


class TestWorkspace:
    def test_workspace_initialization(self):
        # Test basic initialization
        ws = Workspace("test", "example.com", "token123")
        assert ws.code == "test"
        assert ws.host == "example.com"
        assert ws.token == "token123"
        assert ws.active is True
        assert ws.metadata == {}

        # Test with inactive state and metadata
        metadata = {"name": "Test Workspace", "country": "TestLand"}
        ws = Workspace("test2", "example2.com", "token456", active=False, metadata=metadata)
        assert ws.code == "test2"
        assert ws.host == "example2.com"
        assert ws.token == "token456"
        assert ws.active is False
        assert ws.metadata == metadata

    def test_workspace_str_repr(self):
        ws = Workspace("test", "example.com", "token123")
        assert str(ws) == "Workspace(test, example.com, active=True)"
        assert repr(ws) == "Workspace(test, example.com, active=True, metadata={})"

        ws = Workspace("test", "example.com", "token123", metadata={"region": "Africa"})
        assert repr(ws) == "Workspace(test, example.com, active=True, metadata={'region': 'Africa'})"

    def test_get_metadata_basic(self):
        """Test basic get_metadata functionality"""
        ws = Workspace("test", "example.com", "token123")
        metadata = ws.get_metadata()
        
        expected = {
            'workspace_code': 'test',
            'workspace_host': 'example.com',
            'workspace_active': True,
            'workspace_vendor': 'Unknown'
        }
        assert metadata == expected

    def test_get_metadata_with_custom_metadata(self):
        """Test get_metadata with custom metadata"""
        custom_metadata = {
            "name": "Test Workspace",
            "country": "TestLand",
            "region": "Africa",
            "business_unit": "Sales"
        }
        ws = Workspace("test", "example.com", "token123", metadata=custom_metadata)
        metadata = ws.get_metadata()
        
        expected = {
            'workspace_code': 'test',
            'workspace_host': 'example.com',
            'workspace_active': True,
            'workspace_vendor': 'Unknown',
            'name': 'Test Workspace',
            'country': 'TestLand',
            'region': 'Africa',
            'business_unit': 'Sales'
        }
        assert metadata == expected

    def test_get_metadata_with_fields_and_labels(self):
        """Test get_metadata with _field and _label metadata (default behavior)"""
        custom_metadata = {
            "name": "Test Workspace",
            "country_field": "nation",
            "gender_field": "sex",
            "status_label": "active_status",
            "type_label": "workspace_type",
            "region": "Africa"
        }
        ws = Workspace("test", "example.com", "token123", metadata=custom_metadata)
        
        # Test default behavior (include fields and labels)
        metadata = ws.get_metadata()
        expected = {
            'workspace_code': 'test',
            'workspace_host': 'example.com',
            'workspace_active': True,
            'workspace_vendor': 'Unknown',
            'name': 'Test Workspace',
            'country_field': 'nation',
            'gender_field': 'sex',
            'status_label': 'active_status',
            'type_label': 'workspace_type',
            'region': 'Africa'
        }
        assert metadata == expected

    def test_get_metadata_with_labels_false(self):
        """Test get_metadata with with_fields=True"""
        custom_metadata = {
            "name": "Test Workspace",
            "country_field": "nation",
            "gender_field": "sex",
            "status_label": "active_status",
            "region": "Africa"
        }
        ws = Workspace("test", "example.com", "token123", metadata=custom_metadata)
        
        metadata = ws.get_metadata(with_labels=False)
        expected = {
            'workspace_code': 'test',
            'workspace_host': 'example.com',
            'workspace_active': True,
            'workspace_vendor': 'Unknown',
            'name': 'Test Workspace',
            'country_field': 'nation',
            'gender_field': 'sex',
            'region': 'Africa'
        }
        assert metadata == expected

    def test_get_metadata_with_fields_false(self):
        """Test get_metadata with with_labels=True"""
        custom_metadata = {
            "name": "Test Workspace",
            "country_field": "nation",
            "status_label": "active_status",
            "type_label": "workspace_type",
            "region": "Africa"
        }
        ws = Workspace("test", "example.com", "token123", metadata=custom_metadata)
        
        metadata = ws.get_metadata(with_fields=False)
        expected = {
            'workspace_code': 'test',
            'workspace_host': 'example.com',
            'workspace_active': True,
            'workspace_vendor': 'Unknown',
            'name': 'Test Workspace',
            'status_label': 'active_status',
            'type_label': 'workspace_type',
            'region': 'Africa'
        }
        assert metadata == expected

    def test_get_metadata_with_both_fields_and_labels_false(self):
        """Test get_metadata with both with_fields=True and with_labels=True"""
        custom_metadata = {
            "name": "Test Workspace",
            "country_field": "nation",
            "gender_field": "sex",
            "status_label": "active_status",
            "type_label": "workspace_type",
            "region": "Africa"
        }
        ws = Workspace("test", "example.com", "token123", metadata=custom_metadata)
        
        metadata = ws.get_metadata(with_fields=False, with_labels=False)
        expected = {
            'workspace_code': 'test',
            'workspace_host': 'example.com',
            'workspace_active': True,
            'workspace_vendor': 'Unknown',
            'name': 'Test Workspace',
            'region': 'Africa'
        }
        assert metadata == expected

    def test_get_metadata_inactive_workspace(self):
        """Test get_metadata with inactive workspace"""
        ws = Workspace("test", "example.com", "token123", active=False)
        metadata = ws.get_metadata()
        
        expected = {
            'workspace_code': 'test',
            'workspace_host': 'example.com',
            'workspace_active': False,
            'workspace_vendor': 'Unknown'
        }
        assert metadata == expected

    def test_get_metadata_with_vendor(self):
        """Test get_metadata with different vendors"""
        ws = Workspace("test", "rapidpro.io", "token123")
        metadata = ws.get_metadata()
        assert metadata['workspace_vendor'] == 'TextIt'
        
        ws = Workspace("test", "ilhasoft.mobi", "token123")
        metadata = ws.get_metadata()
        assert metadata['workspace_vendor'] == 'Weni'
        
        ws = Workspace("test", "ona.io", "token123")
        metadata = ws.get_metadata()
        assert metadata['workspace_vendor'] == 'Ona'

    def test_get_metadata_does_not_modify_original(self):
        """Test that get_metadata doesn't modify the original metadata"""
        original_metadata = {
            "name": "Test Workspace",
            "country_field": "nation",
            "status_label": "active_status"
        }
        ws = Workspace("test", "example.com", "token123", metadata=original_metadata.copy())
        
        # Get metadata with default settings (should exclude fields and labels)
        metadata = ws.get_metadata(with_fields=False, with_labels=False)
        
        # Original metadata should remain unchanged
        assert ws.metadata == original_metadata
        assert "country_field" in ws.metadata
        assert "status_label" in ws.metadata
        
        # Returned metadata should not contain fields and labels
        assert "country_field" not in metadata
        assert "status_label" not in metadata

    def test_get_metadata_empty_metadata(self):
        """Test get_metadata with empty metadata dictionary"""
        ws = Workspace("test", "example.com", "token123", metadata={})
        metadata = ws.get_metadata()
        
        expected = {
            'workspace_code': 'test',
            'workspace_host': 'example.com',
            'workspace_active': True,
            'workspace_vendor': 'Unknown'
        }
        assert metadata == expected

  


class TestWorkspaceList:
    @pytest.fixture
    def workspace_list(self):
        wl = WorkspaceList()
    
        # Create sample workspaces
        workspace1 = Workspace("ws1", "example1.com", "token1", True, metadata={"name": "Workspace 1"})
        workspace2 = Workspace("ws2", "example2.com", "token2", False, metadata={"name": "Workspace 2"})
        workspace3 = Workspace("ws3", "example3.com", "token3", True, metadata={"name": "Workspace 3"})
    
        # Add workspaces to list
        wl.workspaces = [workspace1, workspace2, workspace3]
        return wl, workspace1, workspace2, workspace3
  
    def test_get_workspace(self, workspace_list):
        wl, workspace1, workspace2, _ = workspace_list
    
        # Test finding an existing workspace
        ws = wl.get_workspace("ws1")
        assert ws == workspace1

        # Test finding another existing workspace
        ws = wl.get_workspace("ws2")
        assert ws == workspace2
    
        # Test with non-existent workspace
        ws = wl.get_workspace("nonexistent")
        assert ws is None

    def test_get_active_workspaces(self, workspace_list):
        wl, workspace1, workspace2, workspace3 = workspace_list
    
        active_workspaces = wl.get_active_workspaces()
        assert len(active_workspaces) == 2
        assert workspace1 in active_workspaces
        assert workspace3 in active_workspaces
        assert workspace2 not in active_workspaces

    def test_get_inactive_workspaces(self, workspace_list):
        wl, workspace1, workspace2, workspace3 = workspace_list
    
        inactive_workspaces = wl.get_inactive_workspaces()
        assert len(inactive_workspaces) == 1
        assert workspace2 in inactive_workspaces
        assert workspace1 not in inactive_workspaces
        assert workspace3 not in inactive_workspaces

    def test_len_methods(self, workspace_list):
        wl, _, _, _ = workspace_list
    
        assert len(wl) == 3
        assert wl.len_active_workspaces() == 2
        assert wl.len_inactive_workspaces() == 1

    def test_iteration(self, workspace_list):
        wl, workspace1, workspace2, workspace3 = workspace_list
    
        workspaces = [ws for ws in wl]
        assert len(workspaces) == 3
        assert workspace1 in workspaces
        assert workspace2 in workspaces
        assert workspace3 in workspaces

    @patch("builtins.open", new_callable=mock_open)
    @patch("pandas.read_csv")
    def test_load_workspaces(self, mock_read_csv, mock_open):
        # Create mock DataFrames
        secrets_data = {
            "workspace_code": ["ws1", "ws2"], 
            "host": ["example1.com", "example2.com"],
            "token": ["token1", "token2"],
            "active": [True, False]
        }
        secrets_df = pd.DataFrame(secrets_data)
    
        metadata_data = {
        "workspace_code": ["ws1", "ws2"],
        "name": ["Workspace 1", "Workspace 2"],
        "country": ["Country1", "Country2"]
        }
        metadata_df = pd.DataFrame(metadata_data)
        
        # Set up the mock to return our test data
        mock_read_csv.side_effect = [secrets_df, metadata_df]
        
        # Load workspaces
        wl = WorkspaceList()
        wl.load_workspaces("test_secrets.csv", "test_metadata.csv")
        
        # Verify results
        assert len(wl) == 2
        
        ws1 = wl.get_workspace("ws1")
        assert ws1 is not None
        assert ws1.host == "example1.com"
        assert ws1.token == "token1"
        assert ws1.active is True
        assert ws1.metadata == {"name": "Workspace 1", "country": "Country1"}
        
        ws2 = wl.get_workspace("ws2")
        assert ws2 is not None
        assert ws2.host == "example2.com"
        assert ws2.token == "token2"
        assert ws2.active is False
        assert ws2.metadata == {"name": "Workspace 2", "country": "Country2"}

    @patch("pandas.read_csv")
    def test_load_workspaces_missing_columns(self, mock_read_csv):
        # Create a DataFrame missing required columns
        secrets_data = {
            "workspace_code": ["ws1", "ws2"],
            # Missing 'host' column
            "token": ["token1", "token2"],
            "active": [True, False]
        }
        secrets_df = pd.DataFrame(secrets_data)
    
        # Set up the mock to return our test data
        mock_read_csv.return_value = secrets_df
    
        # Load workspaces should raise ValueError
        wl = WorkspaceList()
        with pytest.raises(ValueError):
            wl.load_workspaces("test_secrets.csv")

    @patch("pandas.read_csv")
    def test_load_workspaces_no_metadata(self, mock_read_csv):
        # Create a secrets DataFrame
        secrets_data = {
        "workspace_code": ["ws1", "ws2"],
        "host": ["example1.com", "example2.com"],
        "token": ["token1", "token2"],
        "active": [True, False]
        }
        secrets_df = pd.DataFrame(secrets_data)

        # Set up the mock to raise FileNotFoundError for metadata file
        mock_read_csv.side_effect = [secrets_df, FileNotFoundError]

        wl = WorkspaceList()
        # By default, should raise ValueError when metadata file is missing
        with pytest.raises(ValueError):
            wl.load_workspaces("test_secrets.csv", "nonexistent.csv")

    @patch("pandas.read_csv")
    def test_load_workspaces_no_metadata_flag_false(self, mock_read_csv):
        # Create a secrets DataFrame
        secrets_data = {
            "workspace_code": ["ws1", "ws2"],
            "host": ["example1.com", "example2.com"],
            "token": ["token1", "token2"],
            "active": [True, False]
        }
        secrets_df = pd.DataFrame(secrets_data)

        # Set up the mock to raise FileNotFoundError for metadata file
        mock_read_csv.side_effect = [secrets_df, FileNotFoundError]

        wl = WorkspaceList()
        # Should not raise if ignore_missing_metadata=True
        wl.load_workspaces("test_secrets.csv", "nonexistent.csv", error_on_code_missing_in_metadata=False)
        assert len(wl) == 2
        assert wl.get_workspace("ws1") is not None
        assert wl.get_workspace("ws2") is not None
        assert wl.get_workspace("ws1").metadata == {}
        assert wl.get_workspace("ws2").metadata == {}
    
    def test_load_nonexistent_file(self):
        # Test loading from a nonexistent file
        wl = WorkspaceList()
        with pytest.raises(ValueError):
            wl.load_workspaces("nonexistent.csv")

    @patch("pandas.read_csv")
    def test_load_workspaces_workspace_code_missing_in_metadata(self, mock_read_csv):
        # secrets contains a workspace_code not present in metadata
        secrets_data = {
            "workspace_code": ["ws1", "ws2"],
            "host": ["example1.com", "example2.com"],
            "token": ["token1", "token2"],
            "active": [True, False]
        }
        secrets_df = pd.DataFrame(secrets_data)

        metadata_data = {
            "workspace_code": ["ws1", "ws3"],  # ws2 is missing
            "name": ["Workspace 1", "Workspace 3"],
            "country": ["Country1", "Country3"]
        }
        metadata_df = pd.DataFrame(metadata_data)

        mock_read_csv.side_effect = [secrets_df, metadata_df]

        wl = WorkspaceList()
        with pytest.raises(ValueError) as excinfo:
            wl.load_workspaces("test_secrets.csv", "test_metadata.csv", error_on_code_missing_in_metadata=True)
        assert "Workspace code ws2 not found in metadata file." in str(excinfo.value)

    def test_workspace_equality(self):
        """Test the equality comparison between Workspace objects."""
        # Test equality with identical workspaces
        ws1 = Workspace("test", "example.com", "token123", True, metadata={"name": "Test"})
        ws2 = Workspace("test", "example.com", "token123", True, metadata={"name": "Test"})
        assert ws1 == ws2
        
        # Test inequality with different code
        ws3 = Workspace("different", "example.com", "token123", True, metadata={"name": "Test"})
        assert ws1 != ws3
        
        # Test inequality with different host
        ws4 = Workspace("test", "different.com", "token123", True, metadata={"name": "Test"})
        assert ws1 != ws4
        
        # Test inequality with different token
        ws5 = Workspace("test", "example.com", "different", True, metadata={"name": "Test"})
        assert ws1 != ws5
        
        # Test inequality with different active status
        ws6 = Workspace("test", "example.com", "token123", False, metadata={"name": "Test"})
        assert ws1 != ws6
        
        # Test inequality with different active vendor
        ws7 = Workspace("test", "example.com", "token123", False, vendor="MyVendor", metadata={"name": "Test"})
        assert ws1 != ws7
        
        # Test inequality with different metadata
        ws8 = Workspace("test", "example.com", "token123", True, metadata={"name": "Test", "extra": "Value"})
        assert ws1 != ws8
        
        # Test with non-Workspace object
        assert ws1 != "not a workspace"
        assert ws1 != None
        
    def test_workspace_vendor(self):
        # Test vendor method
        ws = Workspace("test", "example.com", "token123")
        assert ws.vendor == "Unknown"
        ws = Workspace("test", "ilhasoft.mobi", "token123")
        assert ws.vendor == "Weni"
        ws = Workspace("test", "rapidpro.io", "token123")
        assert ws.vendor == "TextIt"
        ws = Workspace("test", "rapidpro.ona.io", "token123")
        assert ws.vendor == "Ona"
        ws = Workspace("test", "rapidpro.ona.io", "token123", vendor="OtherVendor")
        assert ws.vendor == "OtherVendor"
    
    
    def test_get_metadata(self):
        ws = Workspace("test", "example.com", "token123")
        metadata = ws.get_metadata()
        assert metadata == {
            'workspace_code': 'test',
            'workspace_host': 'example.com',
            'workspace_active': True,
            'workspace_vendor': 'Unknown'
        }
  
        ws.metadata = {"name": "Test Workspace", "country": "TestLand"}
        metadata = ws.get_metadata()
        assert metadata == {
            'workspace_code': 'test',
            'workspace_host': 'example.com',
            'workspace_active': True,
            'workspace_vendor': 'Unknown',
            'name': 'Test Workspace',
            'country': 'TestLand'
        }
    def test_to_pandas(self, workspace_list):
        wl, workspace1, workspace2, workspace3 = workspace_list
    
        # Test converting workspace list to pandas DataFrame
        df = wl.to_pandas()
        
        # Check DataFrame structure
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 3
        
        # Check required columns exist
        required_columns = ['workspace_code', 'workspace_host', 'workspace_active', 'workspace_vendor']
        for col in required_columns:
            assert col in df.columns
    
        # Check data integrity
        codes = df['workspace_code'].tolist()
        assert 'ws1' in codes
        assert 'ws2' in codes
        assert 'ws3' in codes
        
        # Check active status
        ws1_row = df[df['workspace_code'] == 'ws1'].iloc[0]
        assert ws1_row['workspace_active'] == True
        assert ws1_row['workspace_host'] == 'example1.com'
        assert ws1_row['name'] == 'Workspace 1'
        
        ws2_row = df[df['workspace_code'] == 'ws2'].iloc[0]
        assert ws2_row['workspace_active'] == False
        assert ws2_row['workspace_host'] == 'example2.com'
        assert ws2_row['name'] == 'Workspace 2'

    def test_to_pandas_empty_list(self):
        # Test with empty workspace list
        wl = WorkspaceList()
        df = wl.to_pandas()
        
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 0
        assert df.empty

    def test_to_pandas_with_various_metadata(self):
        # Test with workspaces having different metadata structures
        wl = WorkspaceList()
        
        ws1 = Workspace("ws1", "example1.com", "token1", True, 
                metadata={"name": "WS1", "country": "US", "region": "North"})
        ws2 = Workspace("ws2", "example2.com", "token2", False, 
                metadata={"name": "WS2", "department": "IT"})
        ws3 = Workspace("ws3", "rapidpro.io", "token3", True, 
                metadata={})  # No additional metadata
        
        wl.workspaces = [ws1, ws2, ws3]
        df = wl.to_pandas()
        
        # Check DataFrame structure
        assert len(df) == 3
        
        # Check that all metadata fields are present as columns
        assert 'name' in df.columns
        assert 'country' in df.columns
        assert 'region' in df.columns
        assert 'department' in df.columns
        assert 'workspace_vendor' in df.columns
        
        # Check NaN values for missing metadata
        assert pd.isna(df[df['workspace_code'] == 'ws2']['country'].iloc[0])
        assert pd.isna(df[df['workspace_code'] == 'ws3']['name'].iloc[0])
        assert df[df['workspace_code'] == 'ws3']['workspace_vendor'].iloc[0] == 'TextIt'
        
        # Check existing values
        assert df[df['workspace_code'] == 'ws1']['country'].iloc[0] == 'US'
        assert df[df['workspace_code'] == 'ws2']['department'].iloc[0] == 'IT'
        