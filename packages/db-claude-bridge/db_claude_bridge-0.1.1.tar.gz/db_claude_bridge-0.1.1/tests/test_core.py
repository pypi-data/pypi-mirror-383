"""Tests for the core functionality."""

import json
import subprocess
from pathlib import Path
from unittest.mock import Mock

import pytest

from db_claude_bridge.core import DatabricksClaudeCore
from db_claude_bridge.exceptions import AuthenticationError


class TestDatabricksClaudeCore:
    """Test cases for DatabricksClaudeCore class."""

    def test_init_default_values(self, temp_home):
        """Test initialization with default values."""
        core = DatabricksClaudeCore(databricks_host="https://test.databricks.com")

        assert core.databricks_host == "https://test.databricks.com"
        assert core.claude_config_path == Path.home() / '.claude' / 'settings.json'
        assert core.debug is False
        assert core.config_dir.exists()
        assert core.config_dir.name == '.db-claude-bridge'

    def test_init_custom_values(self, temp_home):
        """Test initialization with custom values."""
        custom_host = "https://example-workspace.databricks.com"
        custom_config = "/custom/path/settings.json"

        core = DatabricksClaudeCore(
            databricks_host=custom_host, claude_config_path=custom_config, debug=True
        )

        assert core.databricks_host == custom_host
        assert core.claude_config_path == Path(custom_config)
        assert core.debug is True

    def test_load_config_default(self, temp_home):
        """Test loading default configuration when no config file exists."""
        core = DatabricksClaudeCore(databricks_host="https://test.databricks.com")

        assert core.config["databricks_host"] is None  # Config file default
        assert core.config["last_login"] is None
        assert core.config["user_email"] is None

    def test_load_config_existing(self, temp_home):
        """Test loading existing configuration file."""
        config_data = {
            "databricks_host": "https://example-workspace.databricks.com",
            "last_login": 1234567890,
            "user_email": "user@example.com",
        }

        # Create config file
        config_dir = temp_home / '.db-claude-bridge'
        config_dir.mkdir()
        config_file = config_dir / 'config.json'
        with open(config_file, 'w') as f:
            json.dump(config_data, f)

        core = DatabricksClaudeCore(databricks_host="https://test.databricks.com")

        assert core.config["last_login"] == 1234567890
        assert core.config["user_email"] == "user@example.com"

    def test_save_config(self, temp_home):
        """Test saving configuration."""
        core = DatabricksClaudeCore(databricks_host="https://test.databricks.com")
        core.config["test_key"] = "test_value"

        core.save_config()

        # Verify file was created with correct content
        assert core.config_file.exists()
        with open(core.config_file, 'r') as f:
            saved_config = json.load(f)

        assert saved_config["test_key"] == "test_value"

        # Verify file permissions (on Unix systems)
        import stat

        file_mode = core.config_file.stat().st_mode
        assert stat.filemode(file_mode)[-3:] == '---'  # No group/other permissions

    def test_get_databricks_token_success(self, mock_subprocess, sample_token_response):
        """Test successful token retrieval."""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps(sample_token_response)
        mock_subprocess.return_value = mock_result

        core = DatabricksClaudeCore(databricks_host="https://test.databricks.com")
        token = core.get_databricks_token()

        assert token == sample_token_response["access_token"]
        mock_subprocess.assert_called_once_with(
            [
                'databricks',
                'auth',
                'token',
                '--host',
                'https://test.databricks.com',
                '--profile',
                'default',
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )

    def test_get_databricks_token_not_configured(self, mock_subprocess):
        """Test token retrieval when not configured."""
        mock_result = Mock()
        mock_result.returncode = 1
        mock_result.stderr = "not configured for this host"
        mock_subprocess.return_value = mock_result

        core = DatabricksClaudeCore(databricks_host="https://test.databricks.com")
        token = core.get_databricks_token()

        assert token is None

    def test_get_databricks_token_timeout(self, mock_subprocess):
        """Test token retrieval timeout."""
        mock_subprocess.side_effect = subprocess.TimeoutExpired("databricks", 30)

        core = DatabricksClaudeCore(databricks_host="https://test.databricks.com")

        with pytest.raises(AuthenticationError, match="timed out"):
            core.get_databricks_token()

    def test_get_databricks_token_invalid_json(self, mock_subprocess):
        """Test token retrieval with invalid JSON response."""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "invalid json"
        mock_subprocess.return_value = mock_result

        core = DatabricksClaudeCore(databricks_host="https://test.databricks.com")

        with pytest.raises(AuthenticationError, match="Invalid JSON"):
            core.get_databricks_token()

    def test_update_claude_config_new_file(self, temp_home, sample_token):
        """Test updating Claude config when file doesn't exist."""
        core = DatabricksClaudeCore(databricks_host="https://test.databricks.com")
        core.update_claude_config(sample_token)

        # Verify config file was created
        assert core.claude_config_path.exists()

        with open(core.claude_config_path, 'r') as f:
            config = json.load(f)

        assert config["env"]["ANTHROPIC_AUTH_TOKEN"] == sample_token
        assert (
            config["env"]["ANTHROPIC_BASE_URL"]
            == f"{core.databricks_host}/serving-endpoints/anthropic"
        )
        assert config["env"]["ANTHROPIC_MODEL"] == "databricks-claude-sonnet-4-5"

    def test_update_claude_config_existing_file(self, temp_home, sample_token):
        """Test updating Claude config when file exists."""
        # Create existing config
        core = DatabricksClaudeCore(databricks_host="https://test.databricks.com")
        core.claude_config_path.parent.mkdir(parents=True, exist_ok=True)

        existing_config = {
            "env": {"EXISTING_KEY": "existing_value"},
            "other_section": {"key": "value"},
        }

        with open(core.claude_config_path, 'w') as f:
            json.dump(existing_config, f)

        core.update_claude_config(sample_token)

        # Verify existing config was preserved and new values added
        with open(core.claude_config_path, 'r') as f:
            config = json.load(f)

        assert config["env"]["EXISTING_KEY"] == "existing_value"
        assert config["env"]["ANTHROPIC_AUTH_TOKEN"] == sample_token
        assert config["other_section"]["key"] == "value"

    def test_is_authenticated_success(
        self, mock_subprocess, sample_token_response, sample_user_response
    ):
        """Test successful authentication check."""
        # Mock token request
        token_result = Mock()
        token_result.returncode = 0
        token_result.stdout = json.dumps(sample_token_response)

        # Mock user info request
        user_result = Mock()
        user_result.returncode = 0
        user_result.stdout = json.dumps(sample_user_response)

        mock_subprocess.side_effect = [token_result, user_result]

        core = DatabricksClaudeCore(databricks_host="https://test.databricks.com")
        is_auth, email = core.is_authenticated()

        assert is_auth is True
        assert email == "user@example.com"

    def test_is_authenticated_no_token(self, mock_subprocess):
        """Test authentication check when no token available."""
        mock_result = Mock()
        mock_result.returncode = 1
        mock_result.stderr = "not configured for this host"
        mock_subprocess.return_value = mock_result

        core = DatabricksClaudeCore(databricks_host="https://test.databricks.com")
        is_auth, email = core.is_authenticated()

        assert is_auth is False
        assert email is None

    def test_authenticate_success(self, mock_subprocess):
        """Test successful authentication."""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_subprocess.return_value = mock_result

        core = DatabricksClaudeCore(databricks_host="https://test.databricks.com")
        core.authenticate()  # Should not raise exception

        mock_subprocess.assert_called_once_with(
            [
                'databricks',
                'auth',
                'login',
                '--host',
                core.databricks_host,
                '--profile',
                'default',
            ],
            timeout=300,
        )

    def test_authenticate_failure(self, mock_subprocess):
        """Test authentication failure."""
        mock_result = Mock()
        mock_result.returncode = 1
        mock_subprocess.return_value = mock_result

        core = DatabricksClaudeCore(databricks_host="https://test.databricks.com")

        with pytest.raises(AuthenticationError, match="authentication failed"):
            core.authenticate()

    def test_authenticate_timeout(self, mock_subprocess):
        """Test authentication timeout."""
        mock_subprocess.side_effect = subprocess.TimeoutExpired("databricks", 300)

        core = DatabricksClaudeCore(databricks_host="https://test.databricks.com")

        with pytest.raises(AuthenticationError, match="timed out"):
            core.authenticate()

    def test_logout(self, temp_home):
        """Test logout functionality."""
        # Create test files
        databrickscfg = temp_home / '.databrickscfg'
        databrickscfg.write_text("test config")

        databricks_dir = temp_home / '.databricks'
        databricks_dir.mkdir()
        token_cache = databricks_dir / 'token-cache.json'
        token_cache.write_text('{"token": "test"}')

        # Create Claude config with Databricks settings
        core = DatabricksClaudeCore(databricks_host="https://test.databricks.com")
        core.claude_config_path.parent.mkdir(parents=True, exist_ok=True)
        claude_config = {
            "env": {
                "ANTHROPIC_AUTH_TOKEN": "fake_test_token",
                "ANTHROPIC_BASE_URL": "test_url",
                "OTHER_KEY": "should_remain",
            }
        }
        with open(core.claude_config_path, 'w') as f:
            json.dump(claude_config, f)

        # Set some config values
        core.config['last_login'] = 1234567890
        core.config['user_email'] = "user@example.com"

        # Perform logout
        core.logout()

        # Verify files were removed
        assert not databrickscfg.exists()
        assert not token_cache.exists()

        # Verify Claude config was cleaned but preserved other keys
        with open(core.claude_config_path, 'r') as f:
            config = json.load(f)

        assert "ANTHROPIC_AUTH_TOKEN" not in config["env"]
        assert "ANTHROPIC_BASE_URL" not in config["env"]
        assert config["env"]["OTHER_KEY"] == "should_remain"

        # Verify our config was cleared
        assert core.config['last_login'] is None
        assert core.config['user_email'] is None

    def test_refresh_token_and_execute_authenticated(
        self, mock_subprocess, sample_token_response
    ):
        """Test token refresh and execution when already authenticated."""
        # Mock authentication check (already authenticated)
        token_result = Mock()
        token_result.returncode = 0
        token_result.stdout = json.dumps(sample_token_response)

        user_result = Mock()
        user_result.returncode = 0
        user_result.stdout = '{"emails": [{"value": "user@example.com"}]}'

        # Mock Claude execution
        claude_result = Mock()
        claude_result.returncode = 0

        mock_subprocess.side_effect = [
            token_result,
            user_result,
            token_result,
            claude_result,
        ]

        core = DatabricksClaudeCore(databricks_host="https://test.databricks.com")
        exit_code = core.refresh_token_and_execute(["--print", "test"])

        assert exit_code == 0

        # Verify Claude was called with correct arguments
        claude_call = mock_subprocess.call_args_list[-1]
        assert claude_call[0][0] == ['claude', '--print', 'test']

    def test_refresh_token_and_execute_not_authenticated(
        self, mock_subprocess, sample_token_response
    ):
        """Test token refresh and execution when not authenticated."""
        # Mock authentication check (not authenticated initially)
        not_auth_result = Mock()
        not_auth_result.returncode = 1
        not_auth_result.stderr = "not configured"

        # Mock successful login
        login_result = Mock()
        login_result.returncode = 0

        # Mock post-login authentication check
        token_result = Mock()
        token_result.returncode = 0
        token_result.stdout = json.dumps(sample_token_response)

        user_result = Mock()
        user_result.returncode = 0
        user_result.stdout = '{"emails": [{"value": "user@example.com"}]}'

        # Mock Claude execution
        claude_result = Mock()
        claude_result.returncode = 0

        mock_subprocess.side_effect = [
            not_auth_result,  # Initial auth check
            login_result,  # Login
            token_result,  # Post-login auth check (token)
            user_result,  # Post-login auth check (user)
            token_result,  # Token refresh
            claude_result,  # Claude execution
        ]

        core = DatabricksClaudeCore(databricks_host="https://test.databricks.com")
        exit_code = core.refresh_token_and_execute(["test"])

        assert exit_code == 0
        assert core.config['user_email'] == "user@example.com"
        assert core.config['last_login'] is not None
