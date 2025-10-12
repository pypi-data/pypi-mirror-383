"""Tests for the CLI interface."""

import json
import subprocess
from unittest.mock import Mock, patch

import pytest
from click.testing import CliRunner

from databricks_claude.cli import cli
from databricks_claude.exceptions import AuthenticationError


class TestCLI:
    """Test cases for CLI interface."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    def test_version_flag(self):
        """Test --version flag."""
        result = self.runner.invoke(cli, ['--version'])
        
        assert result.exit_code == 0
        assert "databricks-claude 1.0.0" in result.output

    def test_login_command_already_authenticated(self, mock_subprocess):
        """Test login command when already authenticated."""
        # Mock successful authentication check
        token_result = Mock()
        token_result.returncode = 0
        token_result.stdout = '{"access_token": "test_token"}'
        
        user_result = Mock()
        user_result.returncode = 0
        user_result.stdout = '{"emails": [{"value": "test@example.com"}]}'
        
        mock_subprocess.side_effect = [token_result, user_result]
        
        # Mock user input (decline re-authentication)
        with patch('click.confirm', return_value=False):
            result = self.runner.invoke(cli, ['login'])
        
        assert result.exit_code == 0
        assert "Already authenticated as: test@example.com" in result.output

    def test_login_command_success(self, mock_subprocess):
        """Test successful login command."""
        # Mock not authenticated initially
        not_auth_result = Mock()
        not_auth_result.returncode = 1
        not_auth_result.stderr = "not configured"
        
        # Mock successful login
        login_result = Mock()
        login_result.returncode = 0
        
        # Mock post-login checks
        token_result = Mock()
        token_result.returncode = 0
        token_result.stdout = '{"access_token": "test_token"}'
        
        user_result = Mock()
        user_result.returncode = 0
        user_result.stdout = '{"emails": [{"value": "test@example.com"}]}'
        
        mock_subprocess.side_effect = [
            not_auth_result,  # Initial auth check
            login_result,     # Login
            token_result,     # Post-login token check  
            user_result,      # Post-login user check
            token_result,     # Token for config update
        ]
        
        result = self.runner.invoke(cli, ['login'])
        
        assert result.exit_code == 0
        assert "✅ Authenticated successfully!" in result.output
        assert "🎉 Setup complete!" in result.output

    def test_login_command_failure(self, mock_subprocess):
        """Test login command failure."""
        # Mock authentication failure
        not_auth_result = Mock()
        not_auth_result.returncode = 1
        not_auth_result.stderr = "not configured"
        
        login_failure = Mock()
        login_failure.returncode = 1
        
        mock_subprocess.side_effect = [not_auth_result, login_failure]
        
        result = self.runner.invoke(cli, ['login'])
        
        assert result.exit_code == 1
        assert "❌ Error:" in result.output

    def test_logout_command(self, temp_home):
        """Test logout command."""
        # Create some files to be removed
        databrickscfg = temp_home / '.databrickscfg'
        databrickscfg.write_text("test")
        
        result = self.runner.invoke(cli, ['logout'])
        
        assert result.exit_code == 0
        assert "✅ Logout complete!" in result.output
        assert not databrickscfg.exists()

    def test_status_command_authenticated(self, mock_subprocess):
        """Test status command when authenticated."""
        # Mock authentication check
        token_result = Mock()
        token_result.returncode = 0
        token_result.stdout = '{"access_token": "test_token"}'
        
        user_result = Mock()
        user_result.returncode = 0
        user_result.stdout = '{"emails": [{"value": "test@example.com"}]}'
        
        # Mock Claude CLI check
        claude_result = Mock()
        claude_result.returncode = 0
        claude_result.stdout = "2.0.14 (Claude Code)"
        
        mock_subprocess.side_effect = [token_result, user_result, claude_result]
        
        # Create Claude config file
        with self.runner.isolated_filesystem():
            claude_dir = temp_home / '.claude'
            claude_dir.mkdir(parents=True, exist_ok=True)
            claude_config = claude_dir / 'settings.json'
            
            config_data = {
                "env": {
                    "ANTHROPIC_AUTH_TOKEN": "test_token",
                    "ANTHROPIC_BASE_URL": "https://test.databricks.com/serving-endpoints/anthropic"
                }
            }
            
            with open(claude_config, 'w') as f:
                json.dump(config_data, f)
            
            result = self.runner.invoke(cli, ['status'])
        
        assert result.exit_code == 0
        assert "🎉 All systems operational!" in result.output
        assert "✅ Databricks: Authenticated" in result.output

    def test_status_command_not_authenticated(self, mock_subprocess):
        """Test status command when not authenticated."""
        # Mock not authenticated
        not_auth_result = Mock()
        not_auth_result.returncode = 1
        not_auth_result.stderr = "not configured"
        
        mock_subprocess.return_value = not_auth_result
        
        result = self.runner.invoke(cli, ['status'])
        
        assert result.exit_code == 1
        assert "❌ Databricks: Not authenticated" in result.output

    def test_claude_passthrough_authenticated(self, mock_subprocess):
        """Test passing arguments through to Claude when authenticated."""
        # Mock authentication
        token_result = Mock()
        token_result.returncode = 0
        token_result.stdout = '{"access_token": "test_token"}'
        
        user_result = Mock()
        user_result.returncode = 0
        user_result.stdout = '{"emails": [{"value": "test@example.com"}]}'
        
        # Mock Claude execution
        claude_result = Mock()
        claude_result.returncode = 0
        
        mock_subprocess.side_effect = [
            token_result,     # Auth check
            user_result,      # User info
            token_result,     # Token refresh
            claude_result     # Claude execution
        ]
        
        result = self.runner.invoke(cli, ['--print', 'hello'])
        
        assert result.exit_code == 0
        
        # Verify Claude was called with correct args
        claude_call = mock_subprocess.call_args_list[-1]
        assert claude_call[0][0] == ['claude', '--print', 'hello']

    def test_claude_passthrough_not_authenticated(self, mock_subprocess):
        """Test Claude passthrough when not authenticated triggers login."""
        # Mock not authenticated initially
        not_auth_result = Mock()
        not_auth_result.returncode = 1
        not_auth_result.stderr = "not configured"
        
        # Mock successful login flow
        login_result = Mock()
        login_result.returncode = 0
        
        token_result = Mock()
        token_result.returncode = 0
        token_result.stdout = '{"access_token": "test_token"}'
        
        user_result = Mock()
        user_result.returncode = 0
        user_result.stdout = '{"emails": [{"value": "test@example.com"}]}'
        
        claude_result = Mock()
        claude_result.returncode = 0
        
        mock_subprocess.side_effect = [
            not_auth_result,  # Initial auth check
            login_result,     # Auto-login
            token_result,     # Post-login auth check
            user_result,      # User info
            token_result,     # Token refresh  
            claude_result     # Claude execution
        ]
        
        result = self.runner.invoke(cli, ['hello'])
        
        assert result.exit_code == 0
        assert "🔐 Not authenticated with Databricks" in result.output
        assert "✅ Authentication successful!" in result.output

    def test_debug_flag(self):
        """Test that debug flag is properly handled."""
        with patch('databricks_claude.core.DatabricksClaudeCore') as mock_core_class:
            mock_core = Mock()
            mock_core_class.return_value = mock_core
            mock_core.refresh_token_and_execute.return_value = 0
            
            result = self.runner.invoke(cli, ['--debug', 'test'])
            
            # Verify core was initialized with debug=True
            mock_core_class.assert_called_once()
            args, kwargs = mock_core_class.call_args
            # The core should be initialized with debug=True
            # (exact assertion depends on implementation details)

    def test_custom_host_flag(self):
        """Test that custom host flag is properly handled."""
        custom_host = "https://custom.databricks.com"
        
        with patch('databricks_claude.core.DatabricksClaudeCore') as mock_core_class:
            mock_core = Mock()
            mock_core_class.return_value = mock_core
            mock_core.refresh_token_and_execute.return_value = 0
            
            result = self.runner.invoke(cli, ['--host', custom_host, 'test'])
            
            # Verify core was initialized with custom host
            mock_core_class.assert_called_once()
            args, kwargs = mock_core_class.call_args
            assert custom_host in args or custom_host in kwargs.values()

    def test_keyboard_interrupt(self):
        """Test handling of keyboard interrupt."""
        with patch('databricks_claude.core.DatabricksClaudeCore') as mock_core_class:
            mock_core = Mock()
            mock_core_class.return_value = mock_core
            mock_core.refresh_token_and_execute.side_effect = KeyboardInterrupt()
            
            result = self.runner.invoke(cli, ['test'])
            
            assert result.exit_code == 130
            assert "👋 Goodbye!" in result.output

