"""
Pytest configuration for xSystem core tests.
"""

import pytest
import sys
from pathlib import Path

# Path setup - navigate to project root then to src
src_path = str(Path(__file__).parent.parent.parent.parent.parent.parent / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

@pytest.fixture
def xwsystem_module():
    """Provide xwsystem module for testing."""
    try:
        import exonware.xwsystem as xwsystem
        return xwsystem
    except ImportError as e:
        pytest.skip(f"xSystem module import failed: {e}")

@pytest.fixture
def test_data_path():
    """Provide path to test data."""
    return Path(__file__).parent / "data" 