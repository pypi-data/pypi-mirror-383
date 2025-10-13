"""
Pytest configuration and fixtures
"""

import pytest
import tempfile
import shutil
from pathlib import Path


@pytest.fixture
def temp_storage_path():
    """Create a temporary directory for testing storage"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    # Cleanup after test
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def mock_llm():
    """Mock LLM for testing without API calls"""
    from unittest.mock import MagicMock
    
    llm = MagicMock()
    llm.invoke = MagicMock(return_value="Mock response")
    return llm


@pytest.fixture
def sample_files():
    """Sample files for testing"""
    return {
        "test.txt": "Hello, World!",
        "data/sales.csv": "product,revenue\nA,1000\nB,2000",
        "reports/summary.md": "# Summary\n\nTest report"
    }
