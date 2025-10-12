"""Integration tests for the full CLI workflow."""

import json
import subprocess
import tempfile
from pathlib import Path

import pytest


@pytest.mark.integration
class TestIntegration:
    """Integration tests that test the full workflow."""

    def test_package_importable(self):
        """Test that the package can be imported."""
        import db_claude_bridge

        assert db_claude_bridge.__version__ == "0.1.0"

        # Test that core modules can be imported
        from db_claude_bridge.cli import cli  # noqa: F401
        from db_claude_bridge.core import DatabricksClaudeCore  # noqa: F401
        from db_claude_bridge.exceptions import DatabricksClaudeError  # noqa: F401

    def test_cli_help(self):
        """Test that CLI help works."""
        result = subprocess.run(
            ['python3', '-m', 'db_claude_bridge.cli', '--help'],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert "DB Claude Bridge" in result.stdout or "Usage:" in result.stdout

    def test_cli_version(self):
        """Test that CLI version works."""
        result = subprocess.run(
            ['python3', '-m', 'db_claude_bridge.cli', '--version'],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert "db-claude-bridge 0.1.0" in result.stdout

    @pytest.mark.skipif(
        not Path("/usr/bin/databricks").exists()
        and not Path("/opt/homebrew/bin/databricks").exists(),
        reason="Databricks CLI not installed",
    )
    def test_status_command_real_databricks_cli(self):
        """Test status command with real Databricks CLI (if available)."""
        result = subprocess.run(
            ['python3', '-m', 'db_claude_bridge.cli', 'status'],
            capture_output=True,
            text=True,
        )

        # Should either show not authenticated or show status
        # Don't assert on exit code since it depends on auth state
        assert "Databricks:" in result.stdout

    def test_configuration_file_handling(self):
        """Test that configuration files are handled correctly."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_home = Path(temp_dir)

            # Set up temporary home directory
            import os

            old_home = os.environ.get('HOME')
            os.environ['HOME'] = str(temp_home)

            try:
                from db_claude_bridge.core import DatabricksClaudeCore

                # Initialize core (should create config directory)
                core = DatabricksClaudeCore()

                # Check that config directory was created
                assert core.config_dir.exists()
                assert core.config_dir.name == '.db-claude-bridge'

                # Test config save/load
                core.config['test_key'] = 'test_value'
                core.save_config()

                assert core.config_file.exists()

                # Create new instance and verify config was loaded
                core2 = DatabricksClaudeCore()
                assert core2.config['test_key'] == 'test_value'

            finally:
                if old_home:
                    os.environ['HOME'] = old_home
                else:
                    del os.environ['HOME']

    def test_claude_config_update(self):
        """Test that Claude configuration is updated correctly."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_home = Path(temp_dir)

            import os

            old_home = os.environ.get('HOME')
            os.environ['HOME'] = str(temp_home)

            try:
                from db_claude_bridge.core import DatabricksClaudeCore

                core = DatabricksClaudeCore()
                test_token = "fake_test_token_for_testing"

                # Update Claude config
                core.update_claude_config(test_token)

                # Verify config file was created
                assert core.claude_config_path.exists()

                # Verify content
                with open(core.claude_config_path, 'r') as f:
                    config = json.load(f)

                assert config['env']['ANTHROPIC_AUTH_TOKEN'] == test_token
                assert config['env']['ANTHROPIC_BASE_URL'].endswith(
                    '/serving-endpoints/anthropic'
                )
                assert (
                    config['env']['ANTHROPIC_MODEL'] == 'databricks-claude-sonnet-4-5'
                )

                # Verify file permissions (on Unix systems)
                import stat

                file_mode = core.claude_config_path.stat().st_mode
                # Should be readable/writable by owner only
                assert (file_mode & 0o077) == 0

            finally:
                if old_home:
                    os.environ['HOME'] = old_home
                else:
                    del os.environ['HOME']
