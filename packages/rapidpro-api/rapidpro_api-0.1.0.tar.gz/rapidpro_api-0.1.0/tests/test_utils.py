import pytest
import polars as pl
from rapidpro_api.utils import anonymize_uuid, flatten_pl_struct



def test_anonymize_uuid_valid():
  """Test anonymizing a valid UUID."""
  uuid = "12341234-1234-1234-123412341234"
  expected = "********-1234-1234-************"
  assert anonymize_uuid(uuid) == expected

def test_anonymize_uuid_empty_string():
  """Test anonymizing an empty string."""
  uuid = ""
  expected = "************"
  assert anonymize_uuid(uuid) == expected

def test_anonymize_uuid_none():
  """Test anonymizing None."""
  assert anonymize_uuid(None) is None

def test_anonymize_uuid_short():
  """Test anonymizing a short string."""
  uuid = "1234"
  expected = "************"
  assert anonymize_uuid(uuid) == expected

def test_anonymize_uuid_exact_12_chars():
  """Test anonymizing a string with exactly 12 characters."""
  uuid = "123456789012"
  expected = "************"
  assert anonymize_uuid(uuid) == expected

def test_anonymize_uuid_non_string():
  """Test anonymizing a non-string value."""
  assert anonymize_uuid(12345) is None
  assert anonymize_uuid([]) is None
  assert anonymize_uuid({}) is None

#
# Test flatten_pl_struct function
#
@pytest.fixture
def sample_df():
    """Create a sample Polars DataFrame with a struct column."""
    return pl.DataFrame({
        "id": [1, 2],
        "info": pl.Series([
            {"name": "Alice", "age": 30},
            {"name": "Bob", "age": 25}
        ], dtype=pl.Struct([pl.Field("name", pl.Utf8), pl.Field("age", pl.Int64)]))
    })


def test_flatten_pl_struct(sample_df):
    """Test flattening a struct column in a Polars DataFrame."""
    df = sample_df
    struct_col = "info"

    # Flatten the struct column
    flattened_df = flatten_pl_struct(df, struct_col)

    # Check if the new columns are created correctly
    assert "info_name" in flattened_df.columns
    assert "info_age" in flattened_df.columns
    
    # Check the values in the new columns
    assert flattened_df["info_name"].to_list() == ["Alice", "Bob"]
    assert flattened_df["info_age"].to_list() == [30, 25]
    
    # Original struct column should not be dropped
    assert struct_col in flattened_df.columns


def test_flatten_pl_struct_remove_struct(sample_df):
    """Test flattening a struct column and removing the original struct column."""
    df = sample_df
    struct_col = "info"

    # Flatten the struct column and remove the original struct column
    flattened_df = flatten_pl_struct(df, struct_col, remove_struct=True)

    # Check if the new columns are created correctly
    assert "info_name" in flattened_df.columns
    assert "info_age" in flattened_df.columns
    
    # Check the values in the new columns
    assert flattened_df["info_name"].to_list() == ["Alice", "Bob"]
    assert flattened_df["info_age"].to_list() == [30, 25]
    
    # Original struct column should be dropped
    assert struct_col not in flattened_df.columns 


def test_flatten_pl_struct_no_struct_col(sample_df):
    """Test flattening when struct column does not exist."""
    df = sample_df
    
    # Try flattening a non-existent struct column
    flattened_df = flatten_pl_struct(df, "non_existent")
    
    # Should return the original DataFrame unchanged
    assert flattened_df.equals(df)


def test_flatten_pl_struct_with_fields(sample_df):
    """Test flattening a struct column with specific fields."""
    df = sample_df
    struct_col = "info"
    struct_fields = ["name"]  # Only flatten the 'name' field
    
    # Flatten the struct column with specified fields
    flattened_df = flatten_pl_struct(df, struct_col, struct_fields)
    
    # Check if the new column is created correctly
    assert "info_name" in flattened_df.columns
    assert "info_age" not in flattened_df.columns  # 'age' should not be included
    
    # Check the values in the new column
    assert flattened_df["info_name"].to_list() == ["Alice", "Bob"]
    
    # Original struct column should still be present
    assert struct_col in flattened_df.columns 


def test_flatten_pl_struct_invalid_fields(sample_df):
    """Test flattening with invalid struct fields."""
    df = sample_df
    struct_col = "info"
    
    # Pass an invalid struct_fields type
    with pytest.raises(ValueError, match="struct_fields must be a list of field names."):
        flatten_pl_struct(df, struct_col, struct_fields="invalid_type")
    
    # Pass a list with non-existent fields
    flattened_df = flatten_pl_struct(df, struct_col, struct_fields=["non_existent"])
    
    # Should return the original DataFrame unchanged
    assert flattened_df.equals(df)


def test_flattern_pl_struct_with_prefix(sample_df):
    """Test flattening a struct column with a prefix."""
    df = sample_df
    struct_col = "info"
    prefix = "user"

    # Flatten the struct column with a prefix
    flattened_df = flatten_pl_struct(df, struct_col, prefix=prefix)

    # Check if the new columns are created with the prefix
    assert f"{prefix}_name" in flattened_df.columns
    assert f"{prefix}_age" in flattened_df.columns

    # Check the values in the new columns
    assert flattened_df[f"{prefix}_name"].to_list() == ["Alice", "Bob"]
    assert flattened_df[f"{prefix}_age"].to_list() == [30, 25]

    # Original struct column should be dropped
    assert struct_col in flattened_df.columns 

def test_flattern_pl_struct_with_prefix_and_separator(sample_df):
    """Test flattening a struct column with a prefix and custom separator."""
    df = sample_df
    struct_col = "info"
    prefix = "user"
    prefix_separator = "__"

    # Flatten the struct column with a prefix and custom separator
    flattened_df = flatten_pl_struct(df, struct_col, prefix=prefix, prefix_separator=prefix_separator)

    # Check if the new columns are created with the prefix and separator
    assert f"{prefix}{prefix_separator}name" in flattened_df.columns
    assert f"{prefix}{prefix_separator}age" in flattened_df.columns

    # Check the values in the new columns
    assert flattened_df[f"{prefix}{prefix_separator}name"].to_list() == ["Alice", "Bob"]
    assert flattened_df[f"{prefix}{prefix_separator}age"].to_list() == [30, 25]

    # Original struct column should be dropped
    assert struct_col in flattened_df.columns