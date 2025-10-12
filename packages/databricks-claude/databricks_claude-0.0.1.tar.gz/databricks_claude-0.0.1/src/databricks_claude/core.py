"""Core functionality for Databricks Claude CLI."""

import json
import logging
import subprocess
import sys
import time
import os
import platform
import tempfile
from pathlib import Path
from typing import Dict, Optional, Tuple, Any
from urllib.request import urlretrieve

from .exceptions import DatabricksClaudeError, AuthenticationError, ConfigurationError


class DatabricksClaudeCore:
    """Core functionality for Databricks Claude integration."""

    def __init__(
        self,
        databricks_host: Optional[str] = None,
        claude_config_path: Optional[str] = None,
        debug: bool = False,
        auto_install_claude: bool = True,
    ) -> None:
        """Initialize the core functionality.
        
        Args:
            databricks_host: Databricks workspace host URL (will prompt if not provided)
            claude_config_path: Path to Claude configuration file
            debug: Enable debug logging
            auto_install_claude: Automatically install Claude CLI if missing
        """
        self.databricks_host = databricks_host
        self.claude_config_path = Path(
            claude_config_path or Path.home() / '.claude' / 'settings.json'
        )
        self.debug = debug
        self.auto_install_claude = auto_install_claude
        
        self.config_dir = Path.home() / '.databricks-claude'
        self.config_dir.mkdir(exist_ok=True)
        
        self.config_file = self.config_dir / 'config.json'
        self.config = self._load_config()
        
        # Use saved host if no host provided via CLI
        if not self.databricks_host and self.config.get('databricks_host'):
            self.databricks_host = self.config['databricks_host']
        
        self.logger = self._setup_logging()

    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration."""
        logger = logging.getLogger('databricks-claude')
        
        if self.debug:
            logger.setLevel(logging.DEBUG)
            if not logger.handlers:
                handler = logging.StreamHandler()
                formatter = logging.Formatter(
                    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                )
                handler.setFormatter(formatter)
                logger.addHandler(handler)
        else:
            logger.setLevel(logging.ERROR)
        
        return logger

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration with defaults."""
        default_config = {
            "databricks_host": None,
            "claude_config_path": str(self.claude_config_path),
            "debug": self.debug,
            "last_login": None,
            "user_email": None,
            "claude_base_url": None,
            "claude_model": None,
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    user_config = json.load(f)
                return {**default_config, **user_config}
            except (json.JSONDecodeError, IOError) as e:
                self.logger.warning(f"Failed to load config: {e}")
        
        return default_config

    def save_config(self) -> None:
        """Save current configuration."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=4)
            self.config_file.chmod(0o600)
        except IOError as e:
            raise ConfigurationError(f"Failed to save config: {e}")

    def is_claude_cli_installed(self) -> bool:
        """Check if Claude CLI is installed."""
        try:
            result = subprocess.run(['claude', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    def install_claude_cli(self) -> bool:
        """Install Claude CLI automatically."""
        if self.is_claude_cli_installed():
            self.logger.debug("Claude CLI already installed")
            return True

        if not self.auto_install_claude:
            return False

        print("🔧 Claude CLI not found. Installing...")
        
        try:
            system = platform.system().lower()
            
            if system == "darwin":  # macOS
                return self._install_claude_macos()
            elif system == "linux":
                return self._install_claude_linux()
            elif system == "windows":
                return self._install_claude_windows()
            else:
                print(f"❌ Unsupported platform: {system}")
                return False
                
        except Exception as e:
            print(f"❌ Failed to install Claude CLI: {e}")
            return False

    def _install_claude_macos(self) -> bool:
        """Install Claude CLI on macOS."""
        try:
            # Try to install via curl (Claude's recommended method)
            print("  📥 Downloading Claude CLI for macOS...")
            
            # Download the installer script
            installer_url = "https://storage.googleapis.com/claude-release/claude-installer.sh"
            
            with tempfile.NamedTemporaryFile(mode='w+', suffix='.sh', delete=False) as temp_file:
                try:
                    urlretrieve(installer_url, temp_file.name)
                    os.chmod(temp_file.name, 0o755)
                    
                    # Run installer
                    result = subprocess.run(['bash', temp_file.name], 
                                          capture_output=True, text=True, timeout=300)
                    
                    if result.returncode == 0:
                        print("  ✅ Claude CLI installed successfully")
                        return True
                    else:
                        print(f"  ❌ Installation failed: {result.stderr}")
                        return False
                        
                finally:
                    os.unlink(temp_file.name)
                    
        except Exception as e:
            # Fallback: Try Homebrew if available
            try:
                print("  🍺 Trying Homebrew installation...")
                result = subprocess.run(['brew', 'install', 'claude'], 
                                      capture_output=True, text=True, timeout=300)
                if result.returncode == 0:
                    print("  ✅ Claude CLI installed via Homebrew")
                    return True
            except (FileNotFoundError, subprocess.TimeoutExpired):
                pass
            
            print(f"  ❌ Auto-installation failed: {e}")
            print("  📝 Please install Claude CLI manually from: https://claude.ai/download")
            return False

    def _install_claude_linux(self) -> bool:
        """Install Claude CLI on Linux."""
        try:
            print("  📥 Downloading Claude CLI for Linux...")
            
            # Download and install
            installer_url = "https://storage.googleapis.com/claude-release/claude-installer.sh"
            
            with tempfile.NamedTemporaryFile(mode='w+', suffix='.sh', delete=False) as temp_file:
                try:
                    urlretrieve(installer_url, temp_file.name)
                    os.chmod(temp_file.name, 0o755)
                    
                    result = subprocess.run(['bash', temp_file.name], 
                                          capture_output=True, text=True, timeout=300)
                    
                    if result.returncode == 0:
                        print("  ✅ Claude CLI installed successfully")
                        return True
                    else:
                        print(f"  ❌ Installation failed: {result.stderr}")
                        return False
                        
                finally:
                    os.unlink(temp_file.name)
                    
        except Exception as e:
            print(f"  ❌ Auto-installation failed: {e}")
            print("  📝 Please install Claude CLI manually from: https://claude.ai/download")
            return False

    def _install_claude_windows(self) -> bool:
        """Install Claude CLI on Windows."""
        try:
            print("  📥 Downloading Claude CLI for Windows...")
            
            # Try winget first
            result = subprocess.run(['winget', 'install', 'Anthropic.Claude'], 
                                  capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                print("  ✅ Claude CLI installed via winget")
                return True
            else:
                print("  ❌ winget installation failed")
                print("  📝 Please install Claude CLI manually from: https://claude.ai/download")
                return False
                
        except (FileNotFoundError, subprocess.TimeoutExpired) as e:
            print(f"  ❌ Auto-installation failed: {e}")
            print("  📝 Please install Claude CLI manually from: https://claude.ai/download")
            return False

    def get_databricks_token(self) -> Optional[str]:
        """Get Databricks OAuth token.
        
        Returns:
            Access token if successful, None otherwise
            
        Raises:
            AuthenticationError: If token retrieval fails
        """
        # Prompt for host if not configured
        if not self.databricks_host:
            self._prompt_for_host()
            
        try:
            result = subprocess.run([
                'databricks', 'auth', 'token',
                '--host', self.databricks_host,
                '--profile', 'default'
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                token_data = json.loads(result.stdout.strip())
                access_token = token_data.get('access_token')
                if access_token:
                    self.logger.debug("Successfully obtained Databricks token")
                    return access_token
                else:
                    raise AuthenticationError("Token response missing access_token")
            else:
                error_msg = result.stderr.strip()
                if "not configured" in error_msg.lower():
                    return None  # Not authenticated, will trigger login
                raise AuthenticationError(f"Databricks CLI error: {error_msg}")
                
        except subprocess.TimeoutExpired:
            raise AuthenticationError("Databricks token request timed out")
        except json.JSONDecodeError as e:
            raise AuthenticationError(f"Invalid JSON response: {e}")
        except Exception as e:
            raise AuthenticationError(f"Unexpected error getting token: {e}")

    def update_claude_config(self, token: str, base_url: Optional[str] = None, model: Optional[str] = None) -> None:
        """Update Claude configuration with Databricks token.
        
        Args:
            token: Databricks OAuth access token
            base_url: Base URL for Anthropic API (optional)
            model: Default model to use (optional)
            
        Raises:
            ConfigurationError: If configuration update fails
        """
        try:
            claude_config_path = Path(self.claude_config_path).expanduser()
            claude_config_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Load existing config or create new one
            if claude_config_path.exists():
                with open(claude_config_path, 'r') as f:
                    config = json.load(f)
            else:
                config = {"env": {}}
            
            if 'env' not in config:
                config['env'] = {}
            
            # Use provided values or defaults
            if base_url is None:
                base_url = f"{self.databricks_host}/serving-endpoints/anthropic"
            if model is None:
                model = "databricks-claude-sonnet-4-5"
            
            # Update with Databricks authentication (simplified format)
            config['env'].update({
                'ANTHROPIC_MODEL': model,
                'ANTHROPIC_BASE_URL': base_url,
            })
            
            # Only add token if provided (for when we have valid auth)
            if token:
                config['env']['ANTHROPIC_AUTH_TOKEN'] = token
            
            # Write config with secure permissions
            with open(claude_config_path, 'w') as f:
                json.dump(config, f, indent=4)
            claude_config_path.chmod(0o600)
            
            self.logger.debug("Successfully updated Claude configuration")
            
        except (IOError, json.JSONDecodeError) as e:
            raise ConfigurationError(f"Failed to update Claude config: {e}")

    def prompt_for_configuration(self) -> Tuple[str, str]:
        """Prompt user for configuration if not available.
        
        Returns:
            Tuple of (base_url, model)
        """
        print("🔧 Configuration Setup")
        print("=" * 30)
        
        # Ensure we have a host first
        if not self.databricks_host:
            self._prompt_for_host()
        
        # Get base URL
        default_base_url = f"{self.databricks_host}/serving-endpoints/anthropic"
        print(f"\n📡 Base URL for Claude API:")
        print(f"   Default: {default_base_url}")
        
        base_url = input("   Enter Base URL (press Enter for default): ").strip()
        if not base_url:
            base_url = default_base_url
        
        # Get model
        default_model = "databricks-claude-sonnet-4-5"
        print(f"\n🤖 Default Model:")
        print(f"   Default: {default_model}")
        print("   Other options: databricks-claude-opus-4-1, databricks-claude-sonnet-4")
        
        model = input("   Enter Model (press Enter for default): ").strip()
        if not model:
            model = default_model
        
        return base_url, model

    def _prompt_for_host(self) -> None:
        """Prompt user for Databricks workspace URL."""
        print("🏢 Databricks Workspace Setup")
        print("=" * 30)
        print("\n📍 Databricks workspace URL is required")
        print("   Example: https://your-workspace.cloud.databricks.com")
        print("   Example: https://dbc-12345678-9abc.cloud.databricks.com")
        
        while True:
            host = input("\n   Enter your Databricks workspace URL: ").strip()
            if host:
                if not host.startswith('http'):
                    host = f"https://{host}"
                self.databricks_host = host
                
                # Save host to config for future use
                self.config['databricks_host'] = host
                self.save_config()
                
                print(f"✅ Workspace URL saved: {host}")
                print("   (You won't be asked again)")
                break
            else:
                print("   ❌ Workspace URL is required! Please enter your URL.")

    def setup_claude_cli(self) -> bool:
        """Set up Claude CLI with installation and configuration.
        
        Returns:
            True if setup successful, False otherwise
        """
        print("🔧 Setting up Claude CLI...")
        
        # Check if Claude CLI is installed
        if not self.is_claude_cli_installed():
            print("❌ Claude CLI not found")
            
            if self.auto_install_claude:
                if not self.install_claude_cli():
                    print("❌ Failed to install Claude CLI")
                    print("   Please install manually from: https://claude.ai/download")
                    return False
            else:
                print("   Please install Claude CLI from: https://claude.ai/download")
                return False
        
        # Verify installation
        if not self.is_claude_cli_installed():
            print("❌ Claude CLI installation verification failed")
            return False
        
        # Check if configuration already exists
        if self.claude_config_path.exists():
            try:
                with open(self.claude_config_path, 'r') as f:
                    config = json.load(f)
                
                env = config.get('env', {})
                if env.get('ANTHROPIC_BASE_URL') and env.get('ANTHROPIC_MODEL'):
                    print("✅ Claude CLI configuration already exists")
                    return True
            except (json.JSONDecodeError, IOError):
                pass
        
        # Prompt for configuration
        print("\n📋 Claude CLI needs configuration...")
        base_url, model = self.prompt_for_configuration()
        
        # Update configuration (without token for now)
        self.update_claude_config("", base_url, model)
        
        print("✅ Claude CLI configured successfully")
        print(f"   Base URL: {base_url}")
        print(f"   Model: {model}")
        
        return True

    def is_authenticated(self) -> Tuple[bool, Optional[str]]:
        """Check if authenticated with Databricks.
        
        Returns:
            Tuple of (is_authenticated, user_email)
        """
        try:
            token = self.get_databricks_token()
            if not token:
                return False, None
            
            # Try to get user info
            result = subprocess.run([
                'databricks', 'current-user', 'me',
                '--host', self.databricks_host,
                '--profile', 'default'
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                user_data = json.loads(result.stdout.strip())
                email = None
                if 'emails' in user_data and user_data['emails']:
                    email = user_data['emails'][0].get('value')
                return True, email
            else:
                # Token exists but might be invalid
                return True, None
                
        except Exception as e:
            self.logger.debug(f"Authentication check failed: {e}")
            return False, None

    def authenticate(self) -> None:
        """Perform Databricks authentication.
        
        Raises:
            AuthenticationError: If authentication fails
        """
        # Prompt for host if not configured
        if not self.databricks_host:
            self._prompt_for_host()
            
        try:
            result = subprocess.run([
                'databricks', 'auth', 'login',
                '--host', self.databricks_host,
                '--profile', 'default'
            ], timeout=300)  # 5 minute timeout
            
            if result.returncode != 0:
                raise AuthenticationError("Databricks authentication failed")
                
        except subprocess.TimeoutExpired:
            raise AuthenticationError("Authentication timed out")
        except KeyboardInterrupt:
            raise AuthenticationError("Authentication cancelled by user")

    def logout(self) -> None:
        """Clear all authentication data."""
        # Clear Databricks authentication
        databrickscfg = Path.home() / '.databrickscfg'
        token_cache = Path.home() / '.databricks' / 'token-cache.json'
        
        removed_files = []
        for file_path in [databrickscfg, token_cache]:
            if file_path.exists():
                try:
                    file_path.unlink()
                    removed_files.append(str(file_path))
                except OSError as e:
                    self.logger.warning(f"Failed to remove {file_path}: {e}")
        
        # Clear Claude configuration (only Databricks-specific parts)
        try:
            if self.claude_config_path.exists():
                with open(self.claude_config_path, 'r') as f:
                    config = json.load(f)
                
                env = config.get('env', {})
                databricks_keys = [
                    'ANTHROPIC_AUTH_TOKEN',
                    'ANTHROPIC_BASE_URL', 
                    'ANTHROPIC_MODEL'
                ]
                
                for key in databricks_keys:
                    env.pop(key, None)
                
                with open(self.claude_config_path, 'w') as f:
                    json.dump(config, f, indent=4)
                    
        except (IOError, json.JSONDecodeError) as e:
            self.logger.warning(f"Failed to clear Claude config: {e}")
        
        # Clear our config
        self.config['last_login'] = None
        self.config['user_email'] = None
        self.save_config()

    def refresh_token_and_execute(self, claude_args: list) -> int:
        """Refresh token and execute Claude CLI.
        
        Args:
            claude_args: Arguments to pass to Claude CLI
            
        Returns:
            Exit code from Claude CLI
            
        Raises:
            AuthenticationError: If authentication fails
            ConfigurationError: If configuration update fails
        """
        # Check authentication and auto-login if needed
        is_auth, _ = self.is_authenticated()
        if not is_auth:
            print("🔐 Not authenticated with Databricks")
            print("Starting authentication flow...")
            print()
            
            self.authenticate()
            
            # Verify authentication worked
            is_auth, email = self.is_authenticated()
            if not is_auth:
                raise AuthenticationError("Authentication verification failed")
            
            if email:
                self.config['user_email'] = email
            self.config['last_login'] = time.time()
            self.save_config()
            
            print("✅ Authentication successful!")
            print("🚀 Running your Claude command...")
            print()
        
        # Get fresh token and update Claude config
        token = self.get_databricks_token()
        if not token:
            raise AuthenticationError("Failed to get authentication token")
        
        self.update_claude_config(token)
        
        # Execute Claude CLI
        self.logger.debug(f"Executing: claude {' '.join(claude_args)}")
        
        try:
            # For interactive mode (no args), ensure we use proper TTY
            if not claude_args:
                # Run Claude in interactive mode
                result = subprocess.run(['claude'], stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr)
            else:
                result = subprocess.run(['claude'] + claude_args)
            return result.returncode
        except KeyboardInterrupt:
            return 130
        except FileNotFoundError:
            raise ConfigurationError(
                "Claude CLI not found. Please install from https://claude.ai/download"
            )
        except Exception as e:
            raise DatabricksClaudeError(f"Error running Claude: {e}")
