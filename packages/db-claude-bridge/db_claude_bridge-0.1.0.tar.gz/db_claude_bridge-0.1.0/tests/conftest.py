"""Test configuration and fixtures."""

import tempfile
from pathlib import Path
from unittest.mock import Mock
import pytest

from db_claude_bridge.core import DatabricksClaudeCore


@pytest.fixture
def temp_home(monkeypatch, tmp_path):
    """Create a temporary home directory for testing."""
    home_dir = tmp_path / "home"
    home_dir.mkdir()
    monkeypatch.setenv("HOME", str(home_dir))
    return home_dir


@pytest.fixture
def mock_subprocess(monkeypatch):
    """Mock subprocess calls."""
    mock = Mock()
    monkeypatch.setattr("subprocess.run", mock)
    return mock


@pytest.fixture
def core_instance(temp_home):
    """Create a DatabricksClaudeCore instance for testing."""
    return DatabricksClaudeCore(
        databricks_host="https://test.databricks.com",
        debug=True
    )


@pytest.fixture
def sample_token():
    """Sample JWT token for testing."""
    return "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiJ0ZXN0QGRhdGFicmlja3MuY29tIiwiZXhwIjo5OTk5OTk5OTk5fQ.test"


@pytest.fixture
def sample_token_response(sample_token):
    """Sample token response from Databricks CLI."""
    return {
        "access_token": sample_token,
        "token_type": "Bearer",
        "expiry": "2025-12-31T23:59:59.000000-08:00",
        "expires_in": 3600
    }


@pytest.fixture
def sample_user_response():
    """Sample user response from Databricks CLI."""
    return {
        "active": True,
        "displayName": "Test User",
        "emails": [
            {
                "primary": True,
                "type": "work",
                "value": "test@databricks.com"
            }
        ],
        "id": "123456789",
        "userName": "test@databricks.com"
    }


