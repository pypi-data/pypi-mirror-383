from rapidpro_api.version import get_version, __version__

def test_version_is_string():
  """Test that the version is a string."""
  assert isinstance(__version__, str)

def test_get_version_returns_version():
  """Test that get_version() returns the __version__ value."""
  assert get_version() == __version__

def test_version_format():
  """Test that version follows semantic versioning format (x.y.z)."""
  parts = __version__.split('.')
  assert len(parts) == 3
  for part in parts:
    assert part.isdigit()

def test_version_not_empty():
  """Test that version is not an empty string."""
  assert len(__version__) > 0
