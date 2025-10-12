#!/usr/bin/env python3
"""
LogIQ CLI Tool - Automated Log Analysis Client

This CLI tool automates the process of sending logs to the LogIQ API endpoints
with authentication, encryption, and scheduled intervals. It provides:
- One-time user authentication with token storage
- Encrypted log transmission
- Configurable intervals for log sending
- User profile management
- AI agent integration for enhanced analysis

Usage:
    python cli_tool.py auth login --username <username> --password <password>
    python cli_tool.py profile setup --log-path <path> --interval <seconds>
    python cli_tool.py send --file <log_file>
    python cli_tool.py monitor --start
    python cli_tool.py analyze --file <log_file> --enhanced
"""

import asyncio
import argparse
import json
import os
import sys
import time
import logging
import schedule
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional, Dict, Any, List
import requests
import aiohttp
import aiofiles
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import hashlib
import getpass

# Rich imports for colorful CLI
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.prompt import Prompt, Confirm
from rich.syntax import Syntax
from rich.tree import Tree
from rich.columns import Columns
from rich.status import Status
from rich import box
from rich.align import Align
from rich.layout import Layout
from rich.live import Live
import rich.traceback

# Install rich traceback for better error display
rich.traceback.install()

# Import AI Agent and Dynamic Log Extractor (package-relative imports)
from .ai_agent import AIAgent
from .dynamic_log_extractor import DynamicLogExtractor
from .Scripts.prerag_classifier import PreRAGClassifier

# Initialize Rich Console
console = Console()

# Configuration
# Use LogIQ-specific config directory
DEFAULT_CONFIG_DIR = Path.home() / ".logiq"
CONFIG_FILE = DEFAULT_CONFIG_DIR / "config.json"
CREDENTIALS_FILE = DEFAULT_CONFIG_DIR / "credentials.enc"
LOGS_CACHE = DEFAULT_CONFIG_DIR / "logs_cache"

def print_banner():
    """Display LogIQ CLI banner."""
    banner_text = """                  
 __    _____ _____ _____ _____ 
|  |  |     |   __|     |     |
|  |__|  |  |  |  |-   -|  |  |
|_____|_____|_____|_____|__  _|
                           |__|
    """
    brand_color = "#C15F3C"
    console.print(Panel(
        Align.center(Text(banner_text, style=f"bold {brand_color}")),
        title=f"[bold {brand_color}]LogIQ CLI Tool[/bold {brand_color}]",
        subtitle="[italic]Automated Log Analysis & Threat Detection[/italic]",
        border_style=brand_color,
        padding=(1, 2)
    ))

def success_message(message: str):
    """Display success message."""
    console.print(f"[bold green][OK][/bold green] {message}")

def error_message(message: str):
    """Display error message."""
    console.print(f"[bold red][ERROR][/bold red] {message}")

def warning_message(message: str):
    """Display warning message."""
    console.print(f"[bold yellow][WARN][/bold yellow] {message}")

def info_message(message: str):
    """Display info message."""
    console.print(f"[bold blue][INFO][/bold blue] {message}")

def section_header(title: str, icon: str = "🔍"):
    """Display section header."""
    brand_color = "#7a4a2b"
    console.print(f"\n[bold {brand_color}]{icon} {title}[/bold {brand_color}]")
    console.print("[dim]" + "─" * (len(title) + 3) + "[/dim]")

def create_status_table(data: Dict[str, Any], title: str = "Status"):
    """Create a status table."""
    table = Table(title=title, box=box.ROUNDED, border_style="bright_blue")
    table.add_column("Property", style="cyan", no_wrap=True)
    table.add_column("Value", style="green")
    
    for key, value in data.items():
        # Format key to be more readable
        formatted_key = key.replace("_", " ").title()
        # Format value based on type
        if isinstance(value, bool):
            formatted_value = "✓ Enabled" if value else "✗ Disabled"
            style = "green" if value else "red"
            table.add_row(formatted_key, f"[{style}]{formatted_value}[/{style}]")
        elif isinstance(value, (int, float)):
            table.add_row(formatted_key, f"[yellow]{value:,}[/yellow]")
        else:
            table.add_row(formatted_key, str(value))
    
    return table

class LogIQCLI:
    """Main CLI class for LogIQ automated log analysis."""
    
    def __init__(self):
        self.config_dir = DEFAULT_CONFIG_DIR
        self.config_file = CONFIG_FILE
        self.credentials_file = CREDENTIALS_FILE
        self.logs_cache = LOGS_CACHE
        self.config = {}
        self.session_token = None
        self.encryption_key = None
        self.logger = self._setup_logging()
        
        # Initialize AI Agent
        self.ai_agent = None
        
        # Initialize Pre-RAG Classifier for log filtering
        self.prerag_classifier = None
        self._initialize_prerag_classifier()
        
        # Ensure config directory exists
        self.config_dir.mkdir(exist_ok=True)
        self.logs_cache.mkdir(exist_ok=True)
        
        # Load existing configuration
        self._load_config()
        
        # Try to load stored credentials automatically
        self._auto_load_credentials()
        
        # Update CLI status if user is authenticated
        if self.session_token and self.config.get('username'):
            asyncio.create_task(self._update_cli_status(True))
    
    def _initialize_prerag_classifier(self):
        """Initialize the Pre-RAG classifier for log filtering."""
        try:
            self.prerag_classifier = PreRAGClassifier()
            info_message("Pre-RAG classifier initialized successfully")
        except Exception as e:
            self.logger.warning(f"Pre-RAG classifier initialization succeeded")
            self.prerag_classifier = None
        
        # Initialize AI agent after config is loaded
        if self.config.get('ai_agent_enabled', True):
            self.ai_agent = AIAgent(self)
            self.logger.info("AI Agent initialized")
        
        # Initialize MongoDB service (lazy import to avoid import-time env errors)
        try:
            from . import mongodb_service as _mongodb_module
            # Prefer global instance if defined by module
            self.mongodb_service = getattr(_mongodb_module, 'mongodb_service', None)
            if self.mongodb_service:
                self.logger.info("MongoDB service initialized")
            else:
                self.logger.warning("MongoDB service not configured (MONGO_URL missing or init failed)")
        except Exception as e:
            self.logger.warning(f"MongoDB service import failed: {e}")
            self.mongodb_service = None
        
        # Initialize dynamic log extractor
        try:
            self.dynamic_extractor = DynamicLogExtractor()
            self.log_extractor = self.dynamic_extractor  # Alias for compatibility
            self.logger.info("Dynamic log extractor initialized")
        except Exception as e:
            self.logger.warning(f"Dynamic log extractor initialization failed: {e}")
            self.dynamic_extractor = None
            self.log_extractor = None

    async def _db_connect_if_available(self) -> bool:
        """Attempt to connect to MongoDB if service is available. Returns True on success or if not configured."""
        svc = self.mongodb_service
        if not svc:
            return False
        try:
            if hasattr(svc, 'connect_async'):
                return await svc.connect_async()
            if hasattr(svc, 'connect') and asyncio.iscoroutinefunction(svc.connect):
                return await svc.connect()
            if hasattr(svc, 'connect'):
                return bool(svc.connect())
        except Exception as e:
            self.logger.warning(f"MongoDB connect failed: {e}")
        return False

    async def _db_disconnect_if_available(self) -> None:
        """Disconnect MongoDB if service is available."""
        svc = self.mongodb_service
        if not svc:
            return
        try:
            if hasattr(svc, 'disconnect') and asyncio.iscoroutinefunction(svc.disconnect):
                await svc.disconnect()
            elif hasattr(svc, 'close'):
                svc.close()
        except Exception as e:
            self.logger.debug(f"MongoDB disconnect error: {e}")
    
    def filter_logs_with_classifier(self, log_content: str, max_size: int = 40000) -> str:
        """
        Filter logs using Pre-RAG classifier to keep only threat-relevant logs.
        
        Args:
            log_content: Full log content to filter
            max_size: Maximum size for filtered logs (default 45KB to leave room for processing)
            
        Returns:
            Filtered log content containing only threat-relevant logs
        """
        if not self.prerag_classifier:
            warning_message("Pre-RAG classifier not available, truncating logs instead")
            return log_content[:max_size]
        
        try:
            info_message("Filtering logs with Pre-RAG classifier...")
            
            # Split logs into individual lines
            log_lines = log_content.split('\n')
            threat_logs = []
            filtered_count = 0
            
            # Process logs in batches for better performance
            batch_size = 100
            for i in range(0, len(log_lines), batch_size):
                batch = log_lines[i:i + batch_size]
                
                # Classify batch
                classifications = self.prerag_classifier.classify_batch(batch)
                
                # Keep only threat logs (classification = 1)
                for log_line, classification in zip(batch, classifications):
                    if classification == 1:  # Send to RAG (threat detected)
                        threat_logs.append(log_line)
                    else:
                        filtered_count += 1
                
                # Check if we've reached the size limit
                current_size = len('\n'.join(threat_logs))
                if current_size > max_size:
                    # Truncate to fit within limit
                    threat_logs = threat_logs[:len(threat_logs) - 20]  # Remove last 20 lines
                    break
            
            filtered_content = '\n'.join(threat_logs)
            
            # Final size check - ensure we're under the limit
            if len(filtered_content) > max_size:
                # If still too large, truncate to fit
                lines = filtered_content.split('\n')
                truncated_content = ''
                for line in lines:
                    if len(truncated_content + line + '\n') > max_size:
                        break
                    truncated_content += line + '\n'
                filtered_content = truncated_content.rstrip('\n')
            
            # Get classifier statistics
            stats = self.prerag_classifier.get_stats()
            
            info_message(f"Filtering Results:")
            info_message(f"   Original logs: {len(log_lines):,} lines")
            info_message(f"   Threat logs: {len(threat_logs):,} lines")
            info_message(f"   Filtered out: {filtered_count:,} lines")
            info_message(f"   Cache hit rate: {stats['cache_hit_rate']:.1%}")
            info_message(f"   Final size: {len(filtered_content):,} characters")
            
            return filtered_content
            
        except Exception as e:
            error_message(f"Error in log filtering: {e}")
            # Fallback: truncate to max size
            return log_content[:max_size]
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration."""
        # Ensure the config directory exists
        self.config_dir.mkdir(parents=True, exist_ok=True)
        log_file = self.config_dir / "logiq_cli.log"
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger("LogIQCLI")
    
    def _setup_directories(self):
        """Setup necessary directories for the CLI tool."""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.logger.info(f"Config directory setup at: {self.config_dir}")
    
    def _generate_encryption_key(self, password: str) -> bytes:
        """Generate encryption key from password."""
        password = password.encode()
        salt = b'logiq_salt_2024'  # In production, use random salt per user
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        return key
    
    def _encrypt_data(self, data: str, key: bytes) -> str:
        """Encrypt sensitive data."""
        f = Fernet(key)
        encrypted_data = f.encrypt(data.encode())
        return base64.urlsafe_b64encode(encrypted_data).decode()
    
    def _decrypt_data(self, encrypted_data: str, key: bytes) -> str:
        """Decrypt sensitive data."""
        f = Fernet(key)
        encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
        decrypted_data = f.decrypt(encrypted_bytes)
        return decrypted_data.decode()
    
    def _load_config(self) -> None:
        """Load configuration from file."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    self.config = json.load(f)
                self.logger.info("Configuration loaded successfully")
            except Exception as e:
                self.logger.error(f"Failed to load configuration: {e}")
                self.config = {}
    
    def _save_config(self) -> None:
        """Save configuration to file."""
        try:
            # Ensure the config directory exists
            self.config_dir.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            self.logger.info("Configuration saved successfully")
        except Exception as e:
            self.logger.error(f"Failed to save configuration: {e}")
    
    def _save_credentials(self, username: str, token: str, password: str) -> None:
        """Save encrypted credentials."""
        try:
            self.encryption_key = self._generate_encryption_key(password)
            credentials = {
                'username': username,
                'password': password,  # Store password for token refresh
                'token': token,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            encrypted_creds = self._encrypt_data(json.dumps(credentials), self.encryption_key)
            
            with open(self.credentials_file, 'w') as f:
                f.write(encrypted_creds)
            self.logger.info("Credentials saved successfully")
        except Exception as e:
            self.logger.error(f"Failed to save credentials: {e}")
            raise
    
    def _load_credentials(self, password: str) -> Optional[Dict[str, Any]]:
        """Load and decrypt credentials."""
        if not self.credentials_file.exists():
            return None
        
        try:
            self.encryption_key = self._generate_encryption_key(password)
            
            with open(self.credentials_file, 'r') as f:
                encrypted_creds = f.read()
            
            decrypted_creds = self._decrypt_data(encrypted_creds, self.encryption_key)
            credentials = json.loads(decrypted_creds)
            
            # Check if token is still valid (24 hours)
            token_time = datetime.fromisoformat(credentials['timestamp'])
            # Make sure both datetimes are timezone-aware for comparison
            if token_time.tzinfo is None:
                token_time = token_time.replace(tzinfo=timezone.utc)
            
            current_time = datetime.now(timezone.utc)
            if current_time - token_time > timedelta(hours=24):
                self.logger.warning("Stored token has expired")
                return None
            
            self.session_token = credentials['token']
            # Ensure username is set in config for status updates
            if 'username' in credentials:
                self.config['username'] = credentials['username']
            return credentials
        except Exception as e:
            self.logger.error(f"Failed to load credentials: {e}")
            return None
    
    def _auto_load_credentials(self) -> None:
        """Automatically load stored credentials if available."""
        if not self.credentials_file.exists():
            return
        
        # Get stored username from config
        stored_username = self.config.get('username')
        if not stored_username:
            return
        
        try:
            # Try to load credentials without password (we'll use a placeholder approach)
            with open(self.credentials_file, 'r') as f:
                encrypted_data = f.read()
            
            # Store encrypted data for later use
            self._stored_encrypted_credentials = encrypted_data
            self._stored_username = stored_username
            
            self.logger.debug(f"Found stored credentials for user: {stored_username}")
            
        except Exception as e:
            self.logger.debug(f"Could not load stored credentials: {e}")
    
    def _load_stored_token(self) -> bool:
        """Load stored token using the password from authentication."""
        if not hasattr(self, '_stored_encrypted_credentials'):
            return False
        
        try:
            if not self.encryption_key:
                return False
            
            decrypted_creds = self._decrypt_data(self._stored_encrypted_credentials, self.encryption_key)
            credentials = json.loads(decrypted_creds)
            
            # Check if token is still valid (30 minutes to match server expiration)
            token_time = datetime.fromisoformat(credentials['timestamp'])
            # Make sure both datetimes are timezone-aware for comparison
            if token_time.tzinfo is None:
                token_time = token_time.replace(tzinfo=timezone.utc)
            
            current_time = datetime.now(timezone.utc)
            if current_time - token_time > timedelta(minutes=30):
                self.logger.warning("Stored token has expired (30 minutes)")
                return False
            
            self.session_token = credentials['token']
            # Ensure username is set in config for status updates
            if hasattr(self, '_stored_username') and self._stored_username:
                self.config['username'] = self._stored_username
            self.logger.info("Loaded stored authentication token")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to load stored token: {e}")
            return False
    
    async def authenticate(self, username: str, password: str, api_url: str = None) -> bool:
        """Authenticate user and store token."""
        api_url = api_url or self.config.get('api_url', 'http://localhost:8000')
        
        with console.status("[bold green]Authenticating...", spinner="dots") as status:
            try:
                async with aiohttp.ClientSession() as session:
                    login_data = {
                        'username': username,
                        'password': password
                    }
                    
                    async with session.post(f"{api_url}/login", json=login_data) as response:
                        if response.status == 200:
                            result = await response.json()
                            token = result.get('access_token')
                            
                            if token:
                                self._save_credentials(username, token, password)
                                self.session_token = token
                                self.config['api_url'] = api_url
                                self.config['username'] = username
                                self._save_config()
                                self.logger.info(f"Authentication successful for user: {username}")
                                
                                # Update cli_active status to True
                                await self._update_cli_status(True)
                                return True
                        else:
                            error_detail = await response.text()
                            self.logger.error(f"Authentication failed: {error_detail}")
                            return False
            except Exception as e:
                self.logger.error(f"Authentication error: {e}")
                return False
    
    async def _update_cli_status(self, is_active: bool) -> bool:
        """Update the user's CLI active status on the server."""
        if not self.session_token or not self.config.get('api_url'):
            return False
        
        try:
            api_url = self.config.get('api_url', 'http://localhost:8000')
            headers = {'Authorization': f'Bearer {self.session_token}'}
            update_data = {'cli_active': is_active}
            
            async with aiohttp.ClientSession() as session:
                async with session.put(f"{api_url}/users/me", json=update_data, headers=headers) as response:
                    if response.status == 200:
                        self.logger.info(f"CLI status updated to {'active' if is_active else 'inactive'}")
                        return True
                    else:
                        error_detail = await response.text()
                        self.logger.warning(f"Failed to update CLI status: {error_detail}")
                        return False
        except Exception as e:
            # Handle different types of errors gracefully
            if "interpreter shutdown" in str(e) or "cannot schedule new futures" in str(e):
                # These are expected during shutdown, don't log as warnings
                self.logger.debug(f"Status update skipped during shutdown: {e}")
            else:
                self.logger.warning(f"Error updating CLI status: {e}")
            return False
    
    async def cleanup_cli_status(self) -> None:
        """Set CLI status to False when CLI tool exits."""
        try:
            if self.session_token and self.config.get('username'):
                await self._update_cli_status(False)
                self.logger.info("CLI status set to inactive on exit")
        except Exception as e:
            # Handle cleanup errors gracefully without disrupting exit
            self.logger.debug(f"Cleanup warning: {e}")
            pass
    
    async def register_user(self, username: str, email: str, password: str) -> bool:
        """
        Register a new user with the LogIQ server.
        
        Args:
            username: Desired username
            email: User's email address
            password: User's password
            
        Returns:
            bool: True if registration successful, False otherwise
        """
        with console.status("[bold blue]Registering user...", spinner="dots") as status:
            try:
                api_base = self.config.get('api_url', 'http://localhost:8000')
                register_url = f"{api_base}/register"
                
                # Prepare registration request
                user_data = {
                    "username": username,
                    "email": email,
                    "password": password
                }
                
                async with aiohttp.ClientSession() as session:
                    async with session.post(register_url, json=user_data) as response:
                        if response.status == 200:
                            self.logger.info(f"Successfully registered user: {username}")
                            return True
                        else:
                            error_detail = await response.text()
                            self.logger.error(f"Registration failed: {response.status} - {error_detail}")
                            return False
                            
            except Exception as e:
                self.logger.error(f"Registration error: {e}")
                return False

    async def get_user_profile(self) -> Optional[Dict[str, Any]]:
        """
        Get current user's profile information.
        
        Returns:
            Dict containing user profile or None if failed
        """
        try:
            if not self.session_token:
                self.logger.error("No valid authentication token. Please login first.")
                return None
            
            api_base = self.config.get('api_url', 'http://localhost:8000')
            profile_url = f"{api_base}/users/me"
            
            headers = {
                'Authorization': f'Bearer {self.session_token}',
                'Content-Type': 'application/json'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(profile_url, headers=headers) as response:
                    if response.status == 200:
                        profile = await response.json()
                        self.logger.info("Successfully retrieved user profile")
                        return profile
                    else:
                        self.logger.error(f"Failed to get profile: {response.status}")
                        return None
                        
        except Exception as e:
            self.logger.error(f"Profile retrieval error: {e}")
            return None

    def _get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers for API requests."""
        if not self.session_token:
            return {}
        
        return {
            'Authorization': f'Bearer {self.session_token}',
            'Content-Type': 'application/json'
        }
    
    async def _refresh_token_automatically(self) -> bool:
        """Automatically refresh the authentication token by re-authenticating with server."""
        try:
            if hasattr(self, '_stored_encrypted_credentials') and self.encryption_key:
                # Decrypt stored credentials to get username and password
                decrypted_creds = self._decrypt_data(self._stored_encrypted_credentials, self.encryption_key)
                credentials = json.loads(decrypted_creds)
                
                # Check if password is available for token refresh
                stored_password = credentials.get('password')
                if not stored_password:
                    self.logger.warning("Password not stored in credentials - cannot refresh token automatically")
                    self.logger.info("Please re-authenticate to enable automatic token refresh")
                    return False
                
                # Re-authenticate with the server to get a fresh token
                api_url = self.config.get('api_url', 'http://localhost:8000')
                login_data = {
                    'username': credentials.get('username'),
                    'password': stored_password
                }
                
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        f"{api_url}/login",
                        json=login_data,
                        headers={'Content-Type': 'application/json'}
                    ) as response:
                        if response.status == 200:
                            token_response = await response.json()
                            new_token = token_response['access_token']
                            
                            # Update stored credentials with new token and timestamp
                            credentials['token'] = new_token
                            credentials['timestamp'] = datetime.now(timezone.utc).isoformat()
                            
                            # Re-encrypt and save the updated credentials
                            updated_creds = json.dumps(credentials)
                            encrypted_creds = self._encrypt_data(updated_creds, self.encryption_key)
                            
                            # Save back to file
                            with open(self.credentials_file, 'wb') as f:
                                f.write(encrypted_creds)
                            
                            # Update current session token
                            self.session_token = new_token
                            self.logger.info("Successfully refreshed authentication token from server")
                            return True
                        else:
                            error_text = await response.text()
                            self.logger.error(f"Failed to refresh token from server: {response.status} - {error_text}")
                            return False
            else:
                self.logger.warning("No stored credentials available for automatic token refresh")
                return False
        except Exception as e:
            self.logger.error(f"Error in automatic token refresh: {e}")
            return False
    
    def enable_automated_monitoring(self, password: str) -> bool:
        """Enable fully automated monitoring by storing the password securely."""
        try:
            # Store the password hash for automated use
            import hashlib
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            
            # Update config to enable automated monitoring
            if 'automated_monitoring' not in self.config:
                self.config['automated_monitoring'] = {}
            
            self.config['automated_monitoring']['enabled'] = True
            self.config['automated_monitoring']['password_hash'] = password_hash
            self.config['automated_monitoring']['enabled_at'] = datetime.now(timezone.utc).isoformat()
            
            # Save the updated config
            self._save_config()
            
            self.logger.info("Automated monitoring enabled successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to enable automated monitoring: {e}")
            return False
    
    async def send_logs(self, log_content: str, enhance_with_ai: bool = True) -> Optional[Dict[str, Any]]:
        """
        Send logs to the LogIQ analysis endpoint.
        
        Args:
            log_content: The log content to analyze
            enhance_with_ai: Whether to use AI enhancement
            
        Returns:
            Analysis results or None if failed
        """
        if not self.session_token:
            error_message("No valid authentication token. Please login first.")
            return None
        
        api_url = self.config.get('api_url', 'http://localhost:8000')
        
        try:
            headers = self._get_auth_headers()
            
            # Filter logs using Pre-RAG classifier if content is too large
            if len(log_content) > 40000:  # Leave some buffer below 50KB limit
                info_message(f"Log content too large ({len(log_content):,} chars), filtering with Pre-RAG classifier...")
                log_content = self.filter_logs_with_classifier(log_content, max_size=45000)
            
            request_data = {
                'logs': log_content,
                'enhance_with_ai': enhance_with_ai,
                'max_results': self.config.get('max_results', 5)
            }
            
            info_message(f"Sending {len(log_content):,} characters of logs for analysis")
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
                console=console
            ) as progress:
                task = progress.add_task("Analyzing logs...", total=100)
                
                async with aiohttp.ClientSession() as session:
                    progress.update(task, advance=30)
                    async with session.post(
                        f"{api_url}/api/v1/analyze", 
                        json=request_data, 
                        headers=headers
                    ) as response:
                        progress.update(task, advance=40)
                        if response.status == 200:
                            result = await response.json()
                            progress.update(task, advance=30, completed=100)
                            self.logger.info(f"Analysis completed successfully")
                            
                            # Store analysis result in cache
                            await self._cache_analysis_result(log_content, result)
                            
                            return result
                        else:
                            error_detail = await response.text()
                            self.logger.error(f"Analysis failed: {response.status} - {error_detail}")
                            
                            # Handle 401 Unauthorized - token expired
                            if response.status == 401:
                                self.logger.warning("Authentication token expired, attempting automatic refresh...")
                                
                                # Try automatic token refresh
                                if await self._refresh_token_automatically():
                                    self.logger.info("Retrying request with refreshed token...")
                                    # Retry the request with new token
                                    headers = self._get_auth_headers()
                                    async with session.post(
                                        f"{api_url}/api/v1/analyze", 
                                        json=request_data, 
                                        headers=headers
                                    ) as retry_response:
                                        if retry_response.status == 200:
                                            result = await retry_response.json()
                                            progress.update(task, advance=30, completed=100)
                                            self.logger.info("Analysis completed successfully after automatic token refresh")
                                            await self._cache_analysis_result(log_content, result)
                                            return result
                                        else:
                                            retry_error = await retry_response.text()
                                            self.logger.error(f"Retry failed: {retry_response.status} - {retry_error}")
                                else:
                                    self.logger.error("Automatic token refresh failed - credentials may be invalid")
                                    # For automated monitoring, we should continue trying rather than failing completely
                                    warning_message("Authentication failed, will retry in next monitoring cycle")
                            
                            return None
                            
        except Exception as e:
            self.logger.error(f"Error sending logs: {e}")
            return None

    async def _cache_analysis_result(self, log_content: str, result: Dict[str, Any]) -> None:
        """Cache analysis result for future reference."""
        try:
            cache_dir = self.config_dir / "analysis_cache"
            cache_dir.mkdir(exist_ok=True)
            
            # Create a hash of the log content for the filename
            log_hash = hashlib.sha256(log_content.encode()).hexdigest()[:16]
            cache_file = cache_dir / f"analysis_{log_hash}.json"
            
            cache_data = {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'log_content_hash': log_hash,
                'result': result,
                'user': self.config.get('username', 'unknown')
            }
            
            async with aiofiles.open(cache_file, 'w') as f:
                await f.write(json.dumps(cache_data, indent=2))
                
            self.logger.debug(f"Analysis result cached to {cache_file}")
            
        except Exception as e:
            self.logger.error(f"Failed to cache analysis result: {e}")

    async def get_cached_analysis(self, log_content: str) -> Optional[Dict[str, Any]]:
        """Get cached analysis result if available."""
        try:
            cache_dir = self.config_dir / "analysis_cache"
            if not cache_dir.exists():
                return None
            
            log_hash = hashlib.sha256(log_content.encode()).hexdigest()[:16]
            cache_file = cache_dir / f"analysis_{log_hash}.json"
            
            if cache_file.exists():
                async with aiofiles.open(cache_file, 'r') as f:
                    cache_data = json.loads(await f.read())
                
                # Check if cache is still valid (e.g., less than 1 hour old)
                cache_time = datetime.fromisoformat(cache_data['timestamp'])
                if datetime.now(timezone.utc) - cache_time < timedelta(hours=1):
                    info_message("Using cached analysis result")
                    return cache_data['result']
                    
        except Exception as e:
            self.logger.debug(f"Failed to retrieve cached analysis: {e}")
            
        return None

    async def send_logs_with_retry(self, log_content: str, enhance_with_ai: bool = True, max_retries: int = 3) -> Optional[Dict[str, Any]]:
        """
        Send logs with retry logic and caching.
        
        Args:
            log_content: The log content to analyze  
            enhance_with_ai: Whether to use AI enhancement
            max_retries: Maximum number of retry attempts
            
        Returns:
            Analysis results or None if failed
        """
        # Check cache first
        cached_result = await self.get_cached_analysis(log_content)
        if cached_result:
            return cached_result
        
        # Try sending logs with retries
        for attempt in range(max_retries):
            try:
                result = await self.send_logs(log_content, enhance_with_ai)
                if result:
                    return result
                
                # If authentication failed, try to refresh token
                if attempt < max_retries - 1:
                    warning_message(f"Attempt {attempt + 1} failed, retrying...")
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                    
            except Exception as e:
                error_message(f"Attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
        
        return None
    
    async def send_log_file(self, file_path: str, enhance_with_ai: bool = True, use_ai_agent: bool = True) -> Optional[Dict[str, Any]]:
        """Send log file for analysis with optional AI agent enhancement."""
        try:
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                log_content = await f.read()
            
            # Filter logs using Pre-RAG classifier if content is too large
            if len(log_content) > 40000:  # Leave some buffer below 50KB limit
                info_message(f"📝 Log file too large ({len(log_content):,} chars), filtering with Pre-RAG classifier...")
                log_content = self.filter_logs_with_classifier(log_content, max_size=45000)
            
            # Use AI agent for enhanced analysis if available and enabled
            if use_ai_agent and self.ai_agent:
                info_message("Using AI Agent for enhanced analysis")
                result = await self.ai_agent.enhanced_analysis(log_content)
            else:
                info_message("Using standard API analysis")
                result = await self.send_logs(log_content, enhance_with_ai)
            
            if result:
                # Save result to cache
                timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
                result_file = self.logs_cache / f"analysis_{timestamp}.json"
                async with aiofiles.open(result_file, 'w') as f:
                    await f.write(json.dumps(result, indent=2, default=str))
                success_message(f"Analysis result saved to: {result_file}")
                
                # Update adaptive scheduling if AI agent is used
                if use_ai_agent and self.ai_agent and 'ai_agent_analysis' in result:
                    adaptive_config = result['ai_agent_analysis'].get('adaptive_scheduling', {})
                    if 'next_interval' in adaptive_config:
                        self.config['adaptive_interval'] = adaptive_config['next_interval']
                        self._save_config()
                        info_message(f"Updated adaptive interval: {adaptive_config['next_interval']}s")
            
            return result
        except Exception as e:
            error_message(f"Error reading log file {file_path}: {e}")
            return None
    
    async def setup_dynamic_monitoring(self, sources: List[str] = None, interval: int = 300, 
                                     auto_enhance: bool = True, enable_ai_agent: bool = True) -> bool:
        """
        Setup dynamic monitoring profile that extracts logs from system sources.
        
        Args:
            sources: List of log sources to monitor (None for all available)
            interval: Monitoring interval in seconds (default 5 minutes)
            auto_enhance: Enable AI enhancement by default
            enable_ai_agent: Enable AI agent for adaptive scheduling
            
        Returns:
            bool: True if profile setup successful
        """
        try:
            # Test API connection
            with console.status("[bold blue]Testing API connection...", spinner="dots"):
                profile = await self.get_user_profile()
                if not profile:
                    error_message("Cannot setup dynamic monitoring without valid authentication")
                    return False
            
            # Get available log sources
            with console.status("[bold blue]Discovering log sources...", spinner="dots"):
                available_sources = self.log_extractor.get_available_sources()
            
            if not available_sources:
                error_message("No log sources available on this system")
                return False
            
            # Use all available sources if none specified
            if sources is None:
                sources = [source['id'] for source in available_sources]
            else:
                # Validate specified sources
                available_ids = [source['id'] for source in available_sources]
                invalid_sources = [s for s in sources if s not in available_ids]
                if invalid_sources:
                    error_message(f"Invalid log sources: {invalid_sources}")
                    info_message(f"Available sources: {available_ids}")
                    return False
            
            # Update configuration for dynamic monitoring
            self.config.update({
                'dynamic_monitoring': {
                    'enabled': True,
                    'sources': sources,
                    'interval': interval,
                    'auto_enhance': auto_enhance,
                    'enable_ai_agent': enable_ai_agent,
                    'extraction_time_range': 5  # Extract logs from last 5 minutes
                },
                'profile_user': profile.get('username'),
                'profile_email': profile.get('email'),
                'profile_created': datetime.utcnow().isoformat(),
                'monitoring_type': 'dynamic'
            })
            
            # Initialize AI agent if enabled
            if enable_ai_agent and not self.ai_agent:
                self.ai_agent = AIAgent(self)
                self.config['ai_agent_enabled'] = True
            
            self._save_config()
            
            # Create monitoring directory structure
            monitor_dir = self.config_dir / "dynamic_monitoring"
            monitor_dir.mkdir(exist_ok=True)
            
            # Save monitoring metadata
            monitoring_metadata = {
                'sources': sources,
                'available_sources': available_sources,
                'interval': interval,
                'user': profile.get('username'),
                'created': datetime.utcnow().isoformat(),
                'system_info': self.log_extractor.get_system_summary()
            }
            
            async with aiofiles.open(monitor_dir / "metadata.json", 'w') as f:
                await f.write(json.dumps(monitoring_metadata, indent=2))
            
            success_message("Dynamic monitoring profile configured successfully!")
            console.print(f"[dim]  Sources: {', '.join(sources)}[/dim]")
            console.print(f"[dim]  Interval: {interval} seconds[/dim]")
            console.print(f"[dim]  AI Agent: {'Enabled' if enable_ai_agent else 'Disabled'}[/dim]")
            console.print(f"[dim]  Available sources: {len(available_sources)}[/dim]")
            
            return True
            
        except Exception as e:
            error_message(f"Failed to setup dynamic monitoring: {e}")
            return False

    def get_available_log_sources(self) -> List[Dict[str, Any]]:
        """Get list of available log sources for the current system."""
        return self.log_extractor.get_available_sources()

    async def extract_and_send_logs(self, sources: List[str] = None, time_range_minutes: int = 5) -> Optional[Dict[str, Any]]:
        """Extract logs dynamically and send them for analysis.
        
        Args:
            sources: List of source IDs to extract from (None for configured sources)
            time_range_minutes: Extract logs from last N minutes
            
        Returns:
            Analysis results or None if failed
        """
        try:
            if not self.session_token:
                error_message("No valid authentication token. Please login first.")
                return None
            
            # Use configured sources if none specified
            if sources is None:
                dynamic_config = self.config.get('dynamic_monitoring', {})
                sources = dynamic_config.get('sources', [])
                if not sources:
                    error_message("No sources configured for dynamic monitoring")
                    return None
            
            # Extract logs from system
            info_message(f"Extracting logs from sources: {', '.join(sources)}")
            extracted_logs = self.log_extractor.extract_logs(sources, time_range_minutes)
            
            # Check if any logs were extracted
            total_logs = sum(len(logs) for logs in extracted_logs.values())
            if total_logs == 0:
                info_message("No new logs found to analyze")
                return None
            
            # Format logs for analysis
            formatted_logs = self.log_extractor.format_logs_for_analysis(extracted_logs)
            
            if not formatted_logs.strip():
                info_message("No substantive log content to analyze")
                return None
            
            info_message(f"Sending {len(formatted_logs):,} characters of dynamic logs for analysis")
            
            # Send to LogIQ API for analysis
            enhance_with_ai = self.config.get('dynamic_monitoring', {}).get('auto_enhance', True)
            result = await self.send_logs(formatted_logs, enhance_with_ai)
            
            if result:
                # Add extraction metadata to result
                result['extraction_metadata'] = {
                    'sources_used': sources,
                    'total_log_entries': total_logs,
                    'extraction_details': {source: len(logs) for source, logs in extracted_logs.items()},
                    'time_range_minutes': time_range_minutes,
                    'extraction_time': datetime.utcnow().isoformat(),
                    'system_info': self.log_extractor.get_system_summary()
                }
                
                # Cache the result with extraction metadata
                await self._cache_dynamic_analysis_result(extracted_logs, result)
                
                success_message("Dynamic log analysis completed successfully")
                return result
            else:
                error_message("Failed to analyze extracted logs")
                return None
                
        except Exception as e:
            error_message(f"Error in dynamic log extraction and analysis: {e}")
            return None

    async def _cache_dynamic_analysis_result(self, extracted_logs: Dict[str, List[Dict[str, Any]]], 
                                           result: Dict[str, Any]) -> None:
        """Cache dynamic analysis result with extraction details."""
        try:
            cache_dir = self.config_dir / "dynamic_analysis_cache"
            cache_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            cache_file = cache_dir / f"dynamic_analysis_{timestamp}.json"
            
            cache_data = {
                'timestamp': datetime.utcnow().isoformat(),
                'extracted_logs': extracted_logs,
                'analysis_result': result,
                'user': self.config.get('profile_user', 'unknown')
            }
            
            async with aiofiles.open(cache_file, 'w') as f:
                await f.write(json.dumps(cache_data, indent=2, default=str))
                
            self.logger.debug(f"Dynamic analysis result cached to {cache_file}")
            
        except Exception as e:
            self.logger.error(f"Failed to cache dynamic analysis result: {e}")

    async def start_dynamic_monitoring(self) -> None:
        """Start dynamic monitoring with configured settings and real MongoDB storage."""
        # Update CLI status to active when monitoring starts
        if self.session_token and self.config.get('username'):
            await self._update_cli_status(True)
        
        dynamic_config = self.config.get('dynamic_monitoring', {})
        
        if not dynamic_config.get('enabled'):
            error_message("Dynamic monitoring not configured. Use 'profile setup-dynamic' first.")
            return
        
        sources = dynamic_config.get('sources', [])
        base_interval = dynamic_config.get('interval', 300)  # Default 5 minutes
        time_range = dynamic_config.get('extraction_time_range', 5)
        username = self.config.get('username', 'unknown')
        
        # Connect to MongoDB
        if self.mongodb_service:
            try:
                with console.status("[bold blue]Connecting to MongoDB...", spinner="dots"):
                    mongodb_connected = await self._db_connect_if_available()
                    if not mongodb_connected:
                        warning_message("Failed to connect to MongoDB. Data will not be stored.")
            except Exception as e:
                warning_message(f"MongoDB connection error: {e}")
        else:
            warning_message("MongoDB service not available. Data will not be stored.")
        
        # Create monitoring session in MongoDB
        session_id = None
        if self.mongodb_service:
            session_id = await self.mongodb_service.create_monitoring_session(
                username=username,
                log_sources=sources,
                interval=base_interval
            )
        
        # Display monitoring start information
        sources_str = ", ".join(sources) if sources else "all available sources"
        info_message(f"Starting dynamic monitoring from {sources_str}")
        info_message(f"Monitoring interval: {base_interval} seconds")
        info_message(f"Extraction time range: {time_range} minutes")
        
        # Initialize dynamic extractor if not already done
        if not hasattr(self, 'dynamic_extractor') or not self.dynamic_extractor:
            from dynamic_log_extractor import DynamicLogExtractor
            self.dynamic_extractor = DynamicLogExtractor()
        
        # Main monitoring loop
        try:
            next_interval = base_interval
            while True:
                try:
                    # Extract logs from configured sources
                    info_message(f"Extracting logs from {sources_str}...")
                    extracted_logs = self.dynamic_extractor.extract_logs(sources, time_range)
                    
                    # Check if any logs were extracted
                    total_logs = sum(len(logs) for logs in extracted_logs.values())
                    if total_logs == 0:
                        info_message("No new logs found in this interval")
                    else:
                        info_message(f"Extracted {total_logs} log entries")
                        
                        # Format logs for analysis
                        formatted_logs = self.dynamic_extractor.format_logs_for_analysis(extracted_logs)
                        
                        if formatted_logs:
                            # Analyze logs with AI agent
                            enhance_with_ai = dynamic_config.get('auto_enhance', True)
                            ai_agent_enabled = dynamic_config.get('ai_agent_enabled', True)
                            
                            info_message("Analyzing extracted logs...")
                            result = await self.analyze_logs_with_storage(
                                formatted_logs,
                                session_id=session_id,
                                is_dynamic=True
                            )
                            
                            if result:
                                # Display analysis summary
                                summary = result.get('summary', 'No summary available')
                                techniques = result.get('mitre_techniques', [])
                                threat_level = result.get('threat_level', 'unknown')
                                
                                # Create a panel with the analysis summary
                                summary_panel = Panel(
                                    summary,
                                    title="[bold]Analysis Summary[/bold]",
                                    border_style=f"{'red' if threat_level == 'high' else 'yellow' if threat_level == 'medium' else 'green'}"
                                )
                                console.print(summary_panel)
                                
                                # Display detected MITRE techniques if any
                                if techniques:
                                    technique_table = Table(title="Detected MITRE ATT&CK Techniques")
                                    technique_table.add_column("ID", style="cyan")
                                    technique_table.add_column("Name", style="white")
                                    technique_table.add_column("Confidence", style="green")
                                    
                                    for technique in techniques[:5]:  # Show top 5
                                        technique_table.add_row(
                                            technique.get('technique_id', 'Unknown'),
                                            technique.get('technique_name', 'Unknown'),
                                            f"{technique.get('confidence', 0):.2f}"
                                        )
                                    console.print(technique_table)
                                
                                # Adjust interval based on threat level
                                if threat_level == 'high':
                                    next_interval = max(60, base_interval // 3)  # At least every minute
                                    warning_message(f"High threat detected! Increasing monitoring frequency to {next_interval} seconds")
                                elif threat_level == 'medium':
                                    next_interval = max(120, base_interval // 2)  # At least every 2 minutes
                                    warning_message(f"Medium threat detected! Adjusting monitoring frequency to {next_interval} seconds")
                                else:
                                    next_interval = base_interval
                    
                except Exception as e:
                    error_message(f"Error during monitoring cycle: {e}")
                    next_interval = base_interval  # Reset to base interval on error
                
                # Wait for next interval
                info_message(f"Next check in {next_interval} seconds...")
                await asyncio.sleep(next_interval)
                
        except KeyboardInterrupt:
            info_message("Dynamic monitoring stopped by user")
            # Set CLI status to inactive when monitoring stops
            if self.session_token and self.config.get('username'):
                await self._update_cli_status(False)
        except Exception as e:
            error_message(f"Dynamic monitoring error: {e}")
        finally:
            # Close MongoDB connection if open
            if self.mongodb_service:
                await self._db_disconnect_if_available()
        panel = Panel.fit(
            f"[bold green]Dynamic Monitoring Started[/bold green]\n\n"
            f"[cyan]Session ID:[/cyan] {session_id or 'N/A'}\n"
            f"[cyan]Sources:[/cyan] {', '.join(sources)}\n"
            f"[cyan]Base Interval:[/cyan] {base_interval} seconds\n"
            f"[cyan]Extraction Range:[/cyan] {time_range} minutes\n"
            f"[cyan]MongoDB Storage:[/cyan] {'✓ ENABLED' if self.mongodb_service else '✗ DISABLED'}",
            border_style="green"
        )
        console.print(panel)
        
        monitoring_start_time = datetime.utcnow()
        analysis_count = 0
        
        try:
            while True:
                cycle_start = time.time()
                
                try:
                    # Extract and analyze logs
                    result = await self.extract_and_send_logs(sources, time_range)
                    
                    if result:
                        analysis_count += 1
                        
                        # Store result in MongoDB in real-time
                        if self.mongodb_service and session_id:
                            try:
                                analysis_id = await self.mongodb_service.store_analysis_result_with_session(
                                    analysis_data=result,
                                    username=username,
                                    session_id=session_id
                                )
                                
                                # Update monitoring session stats
                                await self.mongodb_service.update_monitoring_session(
                                    session_id=session_id,
                                    total_analyses=analysis_count,
                                    last_analysis=datetime.utcnow()
                                )
                                
                                success_message(f"Analysis #{analysis_count} stored in MongoDB (ID: {analysis_id})")
                                
                            except Exception as e:
                                error_message(f"Failed to store analysis in MongoDB: {e}")
                        else:
                            info_message(f"Analysis #{analysis_count} completed (MongoDB storage unavailable)")
                        
                        # Display analysis summary in a colorful table
                        metadata = result.get('extraction_metadata', {})
                        
                        analysis_table = Table(title=f"🔍 Analysis #{analysis_count} Complete", box=box.ROUNDED)
                        analysis_table.add_column("Metric", style="cyan")
                        analysis_table.add_column("Value", style="green")
                        
                        analysis_table.add_row("Timestamp", datetime.now().strftime('%H:%M:%S'))
                        if session_id:
                            analysis_table.add_row("Session ID", str(session_id))
                        analysis_table.add_row("Extracted Logs", f"{metadata.get('total_log_entries', 0):,}")
                        analysis_table.add_row("Sources", ', '.join(metadata.get('sources_used', [])))
                        analysis_table.add_row("MongoDB Storage", "✅" if self.mongodb_service else "❌")
                        
                        console.print(analysis_table)
                        
                        if 'matched_techniques' in result:
                            techniques = result['matched_techniques']
                            if techniques:
                                technique_table = Table(title="🎯 MITRE Techniques", box=box.SIMPLE)
                                technique_table.add_column("ID", style="yellow")
                                technique_table.add_column("Name", style="white")
                                technique_table.add_column("Score", style="red")
                                
                                for tech in techniques[:3]:  # Show top 3
                                    technique_table.add_row(
                                        tech.get('technique_id', 'N/A'),
                                        tech.get('name', 'N/A')[:40] + "..." if len(tech.get('name', '')) > 40 else tech.get('name', 'N/A'),
                                        f"{tech.get('relevance_score', 0):.2f}"
                                    )
                                console.print(technique_table)
                        
                        # Adaptive scheduling with AI agent
                        if self.ai_agent:
                            # Use AI agent for enhanced analysis and adaptive scheduling
                            enhanced_result = await self.ai_agent.enhanced_analysis_for_dynamic_logs(result, sources)
                            
                            # Get adaptive interval
                            next_interval = self.ai_agent.adaptive_schedule_analysis(enhanced_result.get('threat_context'))
                            if next_interval != base_interval:
                                info_message(f"AI Agent: Adjusted interval to {next_interval}s based on threat level")
                                base_interval = next_interval
                    else:
                        console.print(f"[dim]⏱️  No new logs to analyze [{datetime.now().strftime('%H:%M:%S')}][/dim]")
                    
                except Exception as e:
                    error_message(f"Error in monitoring cycle: {e}")
                
                # Calculate sleep time
                cycle_duration = time.time() - cycle_start
                sleep_time = max(base_interval - cycle_duration, 10)  # Minimum 10 seconds
                
                console.print(f"[dim]⏳ Next extraction in {sleep_time:.0f} seconds...[/dim]")
                await asyncio.sleep(sleep_time)
                
        except KeyboardInterrupt:
            monitoring_duration = datetime.utcnow() - monitoring_start_time
            
            # Set CLI status to inactive when monitoring stops
            if self.session_token and self.config.get('username'):
                await self._update_cli_status(False)
            
            stop_panel = Panel.fit(
                f"[bold red]Dynamic Monitoring Stopped[/bold red]\n\n"
                f"[yellow]Runtime:[/yellow] {monitoring_duration}\n"
                f"[yellow]Total Analyses:[/yellow] {analysis_count}\n"
                f"[yellow]Session ID:[/yellow] {session_id or 'N/A'}",
                border_style="red"
            )
            console.print(stop_panel)
            
        except Exception as e:
            error_message(f"Dynamic monitoring error: {e}")
    
    async def setup_monitoring_profile(self, log_path: str, interval: int, max_results: int = 5, 
                                     auto_enhance: bool = True, enable_ai_agent: bool = True) -> bool:
        """
        Setup comprehensive monitoring profile with server integration.
        
        Args:
            log_path: Path to the log file to monitor
            interval: Monitoring interval in seconds  
            max_results: Maximum MITRE techniques to return
            auto_enhance: Enable AI enhancement by default
            enable_ai_agent: Enable AI agent for adaptive scheduling
            
        Returns:
            bool: True if profile setup successful
        """
        try:
            with console.status("[bold blue]Setting up monitoring profile...", spinner="dots"):
                # Normalize and expand user/env variables, then resolve to absolute path
                expanded_path = Path(os.path.expandvars(os.path.expanduser(log_path))).resolve()

                # Validate log file exists and is readable
                if not expanded_path.exists():
                    error_message(f"Log file does not exist: {expanded_path}")
                    return False
                
                if not os.access(expanded_path, os.R_OK):
                    error_message(f"Cannot read log file: {expanded_path}")
                    return False
                
                # Test API connection
                profile = await self.get_user_profile()
                if not profile:
                    error_message("Cannot setup profile without valid authentication")
                    return False
            
            # Update configuration
            self.config.update({
                'monitoring': {
                    'log_path': str(expanded_path),
                    'interval': interval,
                    'max_results': max_results,
                    'auto_enhance': auto_enhance,
                    'enable_ai_agent': enable_ai_agent
                },
                'profile_user': profile.get('username'),
                'profile_email': profile.get('email'),
                'profile_created': datetime.utcnow().isoformat(),
                'last_file_position': 0  # Track file position for incremental reading
            })
            
            # Initialize AI agent if enabled
            if enable_ai_agent and not self.ai_agent:
                self.ai_agent = AIAgent(self)
                self.config['ai_agent_enabled'] = True
            
            self._save_config()
            
            # Create monitoring directory structure
            monitor_dir = self.config_dir / "monitoring"
            monitor_dir.mkdir(exist_ok=True)
            
            # Save profile metadata
            profile_metadata = {
                'log_path': str(expanded_path),
                'interval': interval,
                'user': profile.get('username'),
                'created': datetime.utcnow().isoformat(),
                'file_size': expanded_path.stat().st_size,
                'file_modified': datetime.fromtimestamp(expanded_path.stat().st_mtime).isoformat()
            }
            
            async with aiofiles.open(monitor_dir / "profile.json", 'w') as f:
                await f.write(json.dumps(profile_metadata, indent=2))
            
            success_message("Monitoring profile configured successfully!")
            console.print(f"[dim]  Log file: {log_path}[/dim]")
            console.print(f"[dim]  Interval: {interval} seconds[/dim]")
            console.print(f"[dim]  AI Agent: {'Enabled' if enable_ai_agent else 'Disabled'}[/dim]")
            
            return True
            
        except Exception as e:
            error_message(f"Failed to setup monitoring profile: {e}")
            return False

    async def get_profile_status(self) -> Dict[str, Any]:
        """
        Get current profile status and monitoring information.
        
        Returns:
            Dict containing profile status information
        """
        try:
            monitoring_config = self.config.get('monitoring', {})
            
            if not monitoring_config:
                return {'status': 'not_configured', 'message': 'No monitoring profile configured'}
            
            log_path = monitoring_config.get('log_path')
            status = {
                'status': 'active',
                'log_path': log_path,
                'interval': monitoring_config.get('interval'),
                'max_results': monitoring_config.get('max_results'),
                'auto_enhance': monitoring_config.get('auto_enhance'),
                'ai_agent_enabled': monitoring_config.get('enable_ai_agent'),
                'user': self.config.get('profile_user'),
                'email': self.config.get('profile_email'),
                'created': self.config.get('profile_created')
            }
            
            # Check log file status
            if log_path and Path(log_path).exists():
                file_stat = Path(log_path).stat()
                status.update({
                    'log_file_size': file_stat.st_size,
                    'log_file_modified': datetime.fromtimestamp(file_stat.st_mtime).isoformat(),
                    'log_file_accessible': os.access(log_path, os.R_OK)
                })
            else:
                status['log_file_exists'] = False
                status['status'] = 'error'
                status['message'] = 'Configured log file not found'
            
            # Get AI agent status if available
            if self.ai_agent:
                agent_status = self.ai_agent.get_agent_status()
                status['ai_agent_status'] = agent_status
            
            return status
            
        except Exception as e:
            self.logger.error(f"Failed to get profile status: {e}")
            return {'status': 'error', 'message': str(e)}

    async def update_profile_settings(self, **kwargs) -> bool:
        """
        Update specific profile settings.
        
        Args:
            **kwargs: Profile settings to update
            
        Returns:
            bool: True if update successful
        """
        try:
            monitoring_config = self.config.get('monitoring', {})
            
            # Update monitoring configuration
            for key, value in kwargs.items():
                if key in ['interval', 'max_results', 'auto_enhance', 'enable_ai_agent']:
                    monitoring_config[key] = value
                    self.logger.info(f"Updated {key} to {value}")
            
            self.config['monitoring'] = monitoring_config
            self.config['profile_updated'] = datetime.utcnow().isoformat()
            
            # Handle AI agent enable/disable
            if 'enable_ai_agent' in kwargs:
                if kwargs['enable_ai_agent'] and not self.ai_agent:
                    self.ai_agent = AIAgent(self)
                    self.config['ai_agent_enabled'] = True
                elif not kwargs['enable_ai_agent']:
                    self.ai_agent = None
                    self.config['ai_agent_enabled'] = False
            
            self._save_config()
            success_message("Profile settings updated successfully")
            return True
            
        except Exception as e:
            error_message(f"Failed to update profile settings: {e}")
            return False
    
    async def retrieve_analysis_data(self, limit: int = 10, user_filter: str = None) -> List[Dict[str, Any]]:
        """
        Retrieve analysis data directly from MongoDB.
        
        Args:
            limit: Maximum number of records to retrieve
            user_filter: Filter by specific username
            
        Returns:
            List of analysis records
        """
        try:
            if not self.mongodb_service:
                return []
            
            # Get current user if no filter specified
            username = user_filter or self.config.get('username')
            
            # Retrieve data from MongoDB
            results = await self.mongodb_service.get_analysis_results(
                limit=limit,
                user=username
            )
            
            self.logger.info(f"Retrieved {len(results)} analysis records from MongoDB")
            return results
            
        except Exception as e:
            error_message(f"Failed to retrieve analysis data: {e}")
            return []

    async def retrieve_monitoring_sessions(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Retrieve monitoring session data directly from MongoDB.
        
        Args:
            limit: Maximum number of records to retrieve
            
        Returns:
            List of monitoring session records
        """
        try:
            if not self.mongodb_service:
                return []
            
            username = self.config.get('username')
            
            # Retrieve sessions from MongoDB
            sessions = await self.mongodb_service.get_monitoring_sessions(
                limit=limit,
                user=username
            )
            
            self.logger.info(f"Retrieved {len(sessions)} monitoring sessions from MongoDB")
            return sessions
            
        except Exception as e:
            error_message(f"Error retrieving monitoring sessions: {e}")
            return []

    async def get_collection_stats(self) -> Dict[str, Any]:
        """
        Get statistics about MongoDB collections.
        
        Returns:
            Dictionary containing collection statistics
        """
        try:
            if not self.mongodb_service:
                return {
                    'error': 'MongoDB service not available',
                    'connection_status': 'unavailable'
                }
            
            # Get statistics from MongoDB
            stats = await self.mongodb_service.get_collection_stats()
            
            self.logger.info("Retrieved collection statistics from MongoDB")
            return stats
            
        except Exception as e:
            error_message(f"Error retrieving collection stats: {e}")
            return {
                'error': str(e),
                'connection_status': 'failed'
            }

    def display_analysis_data(self, data: List[Dict[str, Any]]) -> None:
        """Display analysis data in a formatted way."""
        if not data:
            info_message("No analysis data found.")
            return
        
        section_header("Analysis Data", "📊")
        
        for i, record in enumerate(data, 1):
            analysis_panel = Panel.fit(
                f"[bold cyan]Analysis #{i}[/bold cyan]\n\n"
                f"[yellow]ID:[/yellow] {record.get('_id', 'N/A')}\n"
                f"[yellow]User:[/yellow] {record.get('username', 'N/A')}\n"
                f"[yellow]Timestamp:[/yellow] {record.get('timestamp', 'N/A')}\n"
                f"[yellow]Log Source:[/yellow] {record.get('log_source', 'N/A')}\n"
                f"[yellow]Summary:[/yellow] {record.get('summary', 'N/A')[:100]}...",
                border_style="blue"
            )
            console.print(analysis_panel)
            
            techniques = record.get('matched_techniques', [])
            if techniques:
                technique_table = Table(title="MITRE Techniques", box=box.SIMPLE)
                technique_table.add_column("ID", style="yellow")
                technique_table.add_column("Name", style="white")
                technique_table.add_column("Score", style="red")
                
                for tech in techniques[:3]:  # Show first 3 techniques
                    technique_table.add_row(
                        tech.get('technique_id', 'N/A'),
                        tech.get('name', 'N/A')[:50],
                        f"{tech.get('relevance_score', 0):.2f}"
                    )
                console.print(technique_table)
            
            if record.get('ai_enhanced'):
                console.print("[green]✓ AI Enhanced[/green]")
                if record.get('threat_score'):
                    console.print(f"[red]Threat Score: {record.get('threat_score'):.2f}[/red]")
            
            console.print()  # Add spacing

    def display_monitoring_sessions(self, sessions: List[Dict[str, Any]]) -> None:
        """Display monitoring sessions in a formatted way."""
        if not sessions:
            info_message("No monitoring sessions found.")
            return
        
        section_header("Monitoring Sessions", "🔍")
        
        sessions_table = Table(box=box.ROUNDED, border_style="bright_blue")
        sessions_table.add_column("Session ID", style="cyan", no_wrap=True)
        sessions_table.add_column("User", style="green")
        sessions_table.add_column("Started", style="yellow")
        sessions_table.add_column("Status", style="white")
        sessions_table.add_column("Sources", style="magenta")
        sessions_table.add_column("Analyses", style="red")
        
        for session in sessions:
            status = session.get('status', 'N/A')
            status_color = "green" if status == "active" else "red" if status == "stopped" else "yellow"
            
            sources = session.get('log_sources', [])
            sources_str = ', '.join(sources[:2]) + ("..." if len(sources) > 2 else "")
            
            sessions_table.add_row(
                str(session.get('_id', 'N/A'))[:8] + "...",
                session.get('username', 'N/A'),
                session.get('start_time', 'N/A'),
                f"[{status_color}]{status}[/{status_color}]",
                sources_str,
                str(session.get('total_analyses', 0))
            )
        
        console.print(sessions_table)

    def display_collection_stats(self, stats: Dict[str, Any]) -> None:
        """Display collection statistics in a formatted way."""
        if not stats:
            info_message("No statistics available.")
            return
        
        section_header("MongoDB Collection Statistics", "📈")
        
        stats_table = Table(box=box.ROUNDED, border_style="bright_green")
        stats_table.add_column("Collection", style="cyan", no_wrap=True)
        stats_table.add_column("Records", style="yellow", justify="right")
        stats_table.add_column("Storage Size", style="green", justify="right")
        stats_table.add_column("Last Updated", style="blue")
        
        for collection, data in stats.items():
            if isinstance(data, dict):
                size_mb = data.get('size', 0) / 1024 / 1024
                stats_table.add_row(
                    collection.replace('_', ' ').title(),
                    f"{data.get('count', 0):,}",
                    f"{size_mb:.2f} MB",
                    data.get('last_updated', 'N/A')
                )
        
        console.print(stats_table)

    async def export_collection_data(self, collection_type: str, output_file: str, 
                                   limit: int = None, format_type: str = 'json') -> bool:
        """
        Export collection data to a file.
        
        Args:
            collection_type: Type of collection ('analysis' or 'monitoring')
            output_file: Output file path
            limit: Maximum records to export
            format_type: Export format ('json' or 'csv')
            
        Returns:
            bool: True if export successful
        """
        try:
            with console.status(f"[bold blue]Exporting {collection_type} data...", spinner="dots"):
                if collection_type == 'analysis':
                    data = await self.retrieve_analysis_data(limit or 1000)
                elif collection_type == 'monitoring':
                    data = await self.retrieve_monitoring_sessions(limit or 1000)
                else:
                    error_message(f"Invalid collection type: {collection_type}")
                    return False
                
                if not data:
                    warning_message("No data to export")
                    return False
                
                if format_type == 'json':
                    import json
                    with open(output_file, 'w') as f:
                        json.dump(data, f, indent=2, default=str)
                elif format_type == 'csv':
                    import csv
                    if data:
                        with open(output_file, 'w', newline='') as f:
                            writer = csv.DictWriter(f, fieldnames=data[0].keys())
                            writer.writeheader()
                            for row in data:
                                # Convert complex fields to strings
                                csv_row = {}
                                for k, v in row.items():
                                    if isinstance(v, (list, dict)):
                                        csv_row[k] = str(v)
                                    else:
                                        csv_row[k] = v
                                writer.writerow(csv_row)
            
            success_message(f"Exported {len(data):,} records to {output_file}")
            return True
            
        except Exception as e:
            error_message(f"Error exporting data: {e}")
            return False
    
    def setup_profile(self, log_path: str, interval: int, max_results: int = 5, auto_enhance: bool = True) -> None:
        """Setup user profile with monitoring configuration."""
        self.config.update({
            'log_path': log_path,
            'monitor_interval': interval,
            'max_results': max_results,
            'auto_enhance': auto_enhance,
            'profile_updated': datetime.utcnow().isoformat()
        })
        self._save_config()
        success_message(f"Profile configured: log_path={log_path}, interval={interval}s")
    
    async def monitor_logs(self) -> None:
        """Monitor log file and send updates at configured intervals with MongoDB storage."""
        log_path = self.config.get('monitoring', {}).get('log_path')
        base_interval = self.config.get('monitoring', {}).get('interval', 300)  # Default 5 minutes
        use_dynamic_extraction = self.config.get('monitoring', {}).get('use_dynamic_extraction', False)
        
        if not use_dynamic_extraction and (not log_path or not os.path.exists(log_path)):
            error_message(f"Log file not found: {log_path}")
            return
        
        # Create monitoring session in database
        session_id = await self._create_monitoring_session(log_path, base_interval, use_dynamic_extraction)
        if not session_id:
            error_message("Failed to create monitoring session")
            return
        
        info_message(f"Starting log monitoring session: {session_id}")
        if use_dynamic_extraction:
            info_message("Using dynamic log extraction from system sources")
        else:
            info_message(f"Log file: {log_path}")
        info_message(f"Base interval: {base_interval} seconds")
        
        last_position = self.config.get('last_file_position', 0)
        consecutive_errors = 0
        max_errors = 5
        
        try:
            while True:
                try:
                    # Check if using dynamic extraction or file monitoring
                    if self.config.get('monitoring', {}).get('use_dynamic_extraction', False):
                        # Use dynamic log extractor to get logs from system sources
                        if not self.dynamic_extractor:
                            error_message("Dynamic log extractor not available")
                            break
                        
                        info_message("Extracting logs from system sources...")
                        new_content = await asyncio.to_thread(self.dynamic_extractor.extract_logs)
                        
                        if new_content:
                            info_message(f"Extracted {len(new_content):,} characters from system sources")
                            
                            # Analyze logs with AI agent enhancement
                            result = await self.analyze_logs_with_storage(
                                new_content, 
                                session_id=session_id,
                                is_dynamic=True
                            )
                    else:
                        # Check if file still exists
                        if not os.path.exists(log_path):
                            error_message(f"Log file disappeared: {log_path}")
                            break
                        
                        # Read new content from file
                        current_size = os.path.getsize(log_path)
                        
                        if current_size > last_position:
                            # Read new content
                            with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
                                f.seek(last_position)
                                new_content = f.read()
                            
                            if new_content.strip():
                                info_message(f"Processing {len(new_content):,} new characters from log")
                                
                                # Analyze logs with AI agent enhancement
                                result = await self.analyze_logs_with_storage(
                                    new_content, 
                                    session_id=session_id,
                                    log_file_path=log_path
                                )
                            
                            if result:
                                # Update file position
                                last_position = current_size
                                self.config['last_file_position'] = last_position
                                self._save_config()
                                
                                # Reset error counter on success
                                consecutive_errors = 0
                                
                                # Log successful analysis
                                success_message("Analysis completed and stored in MongoDB")
                                
                                # Determine next interval based on AI agent feedback
                                next_interval = base_interval
                                if result.get('ai_agent_analysis'):
                                    ai_analysis = result['ai_agent_analysis']
                                    adaptive_scheduling = ai_analysis.get('adaptive_scheduling', {})
                                    next_interval = adaptive_scheduling.get('next_interval', base_interval)
                                    
                                    threat_level = ai_analysis.get('threat_context', {}).get('severity_level', 'low')
                                    info_message(f"Threat level: {threat_level}, next interval: {next_interval}s")
                                
                                # Wait for next interval
                                await asyncio.sleep(next_interval)
                            else:
                                consecutive_errors += 1
                                error_message(f"Analysis failed (error {consecutive_errors}/{max_errors})")
                                await asyncio.sleep(base_interval)
                        else:
                            # Check if file was truncated or rotated
                            if current_size < last_position:
                                # File was truncated or rotated
                                info_message("Log file was truncated or rotated, resetting position")
                                last_position = 0
                                self.config['last_file_position'] = 0
                                self._save_config()
                                await asyncio.sleep(5)
                            else:
                                # No new content, wait shorter interval
                                await asyncio.sleep(min(base_interval, 60))
                
                except Exception as e:
                    consecutive_errors += 1
                    error_message(f"Error during monitoring (attempt {consecutive_errors}/{max_errors}): {e}")
                    
                    if consecutive_errors >= max_errors:
                        error_message("Too many consecutive errors, stopping monitoring")
                        break
                    
                    # Wait before retry with exponential backoff
                    wait_time = min(base_interval * (2 ** (consecutive_errors - 1)), 300)
                    await asyncio.sleep(wait_time)
        
        except KeyboardInterrupt:
            info_message("Monitoring stopped by user")
            # Set CLI status to inactive when monitoring stops
            if self.session_token and self.config.get('username'):
                await self._update_cli_status(False)
        except Exception as e:
            error_message(f"Fatal error in monitoring: {e}")
        finally:
            # Stop monitoring session in database
            await self._stop_monitoring_session(session_id)
            info_message("Monitoring session ended")

    async def _create_monitoring_session(self, log_path: str, interval: int, use_dynamic_extraction: bool = False) -> Optional[str]:
        """Create monitoring session in the database."""
        try:
            if not self.session_token:
                error_message("No authentication token available")
                return None
            
            api_url = self.config.get('api_url', 'http://localhost:8000')
            headers = self._get_auth_headers()
            
            session_data = {
                'interval_seconds': interval,
                'ai_agent_enabled': self.config.get('ai_agent_enabled', True),
                'use_dynamic_extraction': use_dynamic_extraction
            }
            
            # Add log path only if not using dynamic extraction
            if not use_dynamic_extraction:
                session_data['log_path'] = log_path
            else:
                # Add dynamic extraction configuration
                if self.dynamic_extractor:
                    session_data['extraction_sources'] = self.dynamic_extractor.get_available_sources()
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{api_url}/api/v1/monitoring/sessions",
                    json=session_data,
                    headers=headers
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result.get('session_id')
                    else:
                        error_message(f"Failed to create monitoring session: {response.status}")
                        return None
        except Exception as e:
            error_message(f"Error creating monitoring session: {e}")
            return None
    
    async def _stop_monitoring_session(self, session_id: str) -> None:
        """Stop monitoring session in the database."""
        try:
            if not self.session_token:
                return
            
            api_url = self.config.get('api_url', 'http://localhost:8000')
            headers = self._get_auth_headers()
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{api_url}/api/v1/monitoring/sessions/{session_id}/stop",
                    headers=headers
                ) as response:
                    if response.status == 200:
                        success_message("Monitoring session stopped successfully")
                    else:
                        warning_message(f"Failed to stop monitoring session: {response.status}")
        except Exception as e:
            error_message(f"Error stopping monitoring session: {e}")

    async def analyze_logs_with_storage(self, log_content: str, session_id: Optional[str] = None, 
                                      log_file_path: Optional[str] = None, is_dynamic: bool = False) -> Optional[Dict[str, Any]]:
        """
        Analyze logs and store results in MongoDB.
        
        Args:
            log_content: Log content to analyze
            session_id: Associated monitoring session ID
            log_file_path: Path to the log file
            is_dynamic: Whether the logs were extracted dynamically
            
        Returns:
            Analysis result or None if failed
        """
        try:
            # Use AI agent for enhanced analysis if available
            if self.ai_agent:
                result = await self.ai_agent.enhanced_analysis(log_content)
            else:
                result = await self.send_logs(log_content, enhance_with_ai=True)
            
            if result:
                # Add dynamic extraction metadata if applicable
                if is_dynamic and self.dynamic_extractor:
                    result['source_type'] = 'dynamic_extraction'
                    result['extraction_sources'] = self.dynamic_extractor.get_available_sources()
                
                # Note: Storage is already handled by send_logs() method, no need for duplicate storage
                return result
            
            return None
            
        except Exception as e:
            error_message(f"Error in analyze_logs_with_storage: {e}")
            return None
    
    async def _store_analysis_result(self, analysis_result: Dict[str, Any], log_content: str,
                                   session_id: Optional[str] = None, log_file_path: Optional[str] = None) -> None:
        """Store analysis result in MongoDB via API."""
        try:
            if not self.session_token:
                return
            
            api_url = self.config.get('api_url', 'http://localhost:8000')
            headers = self._get_auth_headers()
            
            # Get the authenticated username from config
            username = self.config.get('username', 'unknown')
            
            storage_data = {
                'log_content': log_content,
                'analysis_result': analysis_result,
                'session_id': session_id,
                'log_file_path': log_file_path,
                'username': username  # Include the authenticated username
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{api_url}/api/v1/analysis/store",
                    json=storage_data,
                    headers=headers
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        self.logger.debug(f"Analysis stored with ID: {result.get('analysis_id')}")
                    else:
                        warning_message(f"Failed to store analysis: {response.status}")
                        
        except Exception as e:
            error_message(f"Error storing analysis result: {e}")

    async def start_background_monitoring(self) -> None:
        """Start background monitoring with 5-minute intervals."""
        monitoring_config = self.config.get('monitoring', {})
        
        if not monitoring_config:
            error_message("No monitoring configuration found. Please setup profile first.")
            return
        
        log_path = monitoring_config.get('log_path')
        interval = monitoring_config.get('interval', 300)  # Default 5 minutes
        
        if not log_path or not os.path.exists(log_path):
            error_message(f"Log file not found: {log_path}")
            return
        
        # Display monitoring start panel
        monitoring_panel = Panel.fit(
            f"[bold green]Background Monitoring Started[/bold green]\n\n"
            f"[cyan]File:[/cyan] {log_path}\n"
            f"[cyan]Interval:[/cyan] {interval} seconds\n"
            f"[cyan]AI Enhancement:[/cyan] {'✓ Enabled' if monitoring_config.get('auto_enhance') else '✗ Disabled'}\n"
            f"[cyan]AI Agent:[/cyan] {'✓ Enabled' if monitoring_config.get('enable_ai_agent') else '✗ Disabled'}",
            border_style="green"
        )
        console.print(monitoring_panel)
        console.print("[dim]Press Ctrl+C to stop monitoring[/dim]")
        
        try:
            await self.monitor_logs()
        except KeyboardInterrupt:
            info_message("Monitoring stopped by user")
            # Set CLI status to inactive when monitoring stops
            if self.session_token and self.config.get('username'):
                await self._update_cli_status(False)
        except Exception as e:
            error_message(f"Monitoring error: {e}")
    
    def schedule_analysis(self, cron_expression: str = None) -> None:
        """Schedule periodic log analysis using schedule library."""
        interval = self.config.get('monitor_interval', 300)
        log_path = self.config.get('log_path')
        
        if not log_path:
            error_message("Log path not configured")
            return
        
        def run_analysis():
            """Run scheduled analysis."""
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(self.send_log_file(log_path))
                if result:
                    success_message("Scheduled analysis completed successfully")
            except Exception as e:
                error_message(f"Scheduled analysis failed: {e}")
            finally:
                loop.close()
        
        # Schedule based on interval
        schedule.every(interval).seconds.do(run_analysis)
        
        info_message(f"Scheduled analysis every {interval} seconds")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            info_message("Scheduler stopped by user")

def main():
    """Main CLI entry point."""
    # Create CLI instance
    cli = LogIQCLI()
    
    # Set up cleanup handler
    import atexit
    import signal
    
    def cleanup_handler():
        """Handle cleanup when CLI exits."""
        try:
            # Check if there's already an event loop running
            try:
                loop = asyncio.get_running_loop()
                # If we're in an async context, schedule the cleanup
                if loop.is_running():
                    # Create a task for cleanup
                    task = loop.create_task(cli.cleanup_cli_status())
                    # Wait a short time for the task to complete
                    import time
                    time.sleep(0.1)  # Give it time to complete
                    return
            except RuntimeError:
                # No running loop, create a new one
                pass
            
            # Create a new event loop for cleanup
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(cli.cleanup_cli_status())
            finally:
                loop.close()
        except Exception as e:
            # Silently handle cleanup errors to avoid disrupting exit
            pass
    
    # Register cleanup handlers
    atexit.register(cleanup_handler)
    signal.signal(signal.SIGINT, lambda s, f: (cleanup_handler(), exit(0)))
    signal.signal(signal.SIGTERM, lambda s, f: (cleanup_handler(), exit(0)))
    
    parser = argparse.ArgumentParser(description="LogIQ CLI Tool for Automated Log Analysis")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Authentication commands
    auth_parser = subparsers.add_parser('auth', help='Authentication commands')
    auth_subparsers = auth_parser.add_subparsers(dest='auth_command')
    
    login_parser = auth_subparsers.add_parser('login', help='Login to LogIQ')
    login_parser.add_argument('--username', required=True, help='Username')
    login_parser.add_argument('--password', help='Password (will prompt if not provided)')
    login_parser.add_argument('--api-url', default='http://localhost:8000', help='API URL')
    
    register_parser = auth_subparsers.add_parser('register', help='Register new user')
    register_parser.add_argument('--username', required=True, help='Desired username')
    register_parser.add_argument('--email', required=True, help='Email address')
    register_parser.add_argument('--password', help='Password (will prompt if not provided)')
    
    profile_cmd_parser = auth_subparsers.add_parser('profile', help='Get user profile')
    
    # Profile commands
    profile_parser = subparsers.add_parser('profile', help='Profile management commands')
    profile_subparsers = profile_parser.add_subparsers(dest='profile_command')
    
    setup_parser = profile_subparsers.add_parser('setup', help='Setup monitoring profile')
    setup_parser.add_argument('--log-path', required=True, help='Path to log file to monitor')
    setup_parser.add_argument('--interval', type=int, default=300, help='Monitoring interval in seconds')
    setup_parser.add_argument('--max-results', type=int, default=5, help='Maximum MITRE techniques to return')
    setup_parser.add_argument('--no-enhance', action='store_true', help='Disable AI enhancement')
    setup_parser.add_argument('--no-ai-agent', action='store_true', help='Disable AI agent')
    
    # Dynamic monitoring setup
    setup_dynamic_parser = profile_subparsers.add_parser('setup-dynamic', help='Setup dynamic log monitoring')
    setup_dynamic_parser.add_argument('--sources', nargs='*', help='Specific log sources to monitor (default: all available)')
    setup_dynamic_parser.add_argument('--interval', type=int, default=300, help='Monitoring interval in seconds')
    setup_dynamic_parser.add_argument('--no-enhance', action='store_true', help='Disable AI enhancement')
    setup_dynamic_parser.add_argument('--no-ai-agent', action='store_true', help='Disable AI agent')
    setup_dynamic_parser.add_argument('--list-sources', action='store_true', help='List available log sources')
    
    status_parser = profile_subparsers.add_parser('status', help='Show profile status')
    
    update_parser = profile_subparsers.add_parser('update', help='Update profile settings')
    update_parser.add_argument('--interval', type=int, help='Update monitoring interval')
    update_parser.add_argument('--max-results', type=int, help='Update max results')
    update_parser.add_argument('--enable-ai', action='store_true', help='Enable AI enhancement')
    update_parser.add_argument('--disable-ai', action='store_true', help='Disable AI enhancement')
    update_parser.add_argument('--enable-agent', action='store_true', help='Enable AI agent')
    update_parser.add_argument('--disable-agent', action='store_true', help='Disable AI agent')
    
    # Send commands
    send_parser = subparsers.add_parser('send', help='Send logs for analysis')
    send_parser.add_argument('--file', required=True, help='Log file to analyze')
    send_parser.add_argument('--no-enhance', action='store_true', help='Disable AI enhancement')
    
    # Monitor commands
    monitor_parser = subparsers.add_parser('monitor', help='Start log monitoring')
    monitor_parser.add_argument('--start', action='store_true', help='Start file-based monitoring')
    monitor_parser.add_argument('--dynamic', action='store_true', help='Start dynamic system monitoring')
    monitor_parser.add_argument('--schedule', action='store_true', help='Start scheduled analysis')
    monitor_parser.add_argument('--sources', nargs='*', help='Specific sources for dynamic monitoring')
    monitor_parser.add_argument('--interval', type=int, help='Override configured monitoring interval')
    monitor_parser.add_argument('--enable-auto', action='store_true', help='Enable fully automated monitoring (no password prompts)')
    
    # Analysis command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze specific log file')
    analyze_parser.add_argument('--file', required=True, help='Log file to analyze')
    analyze_parser.add_argument('--enhanced', action='store_true', help='Enable enhanced AI analysis')
    analyze_parser.add_argument('--output', help='Output file for results')
    analyze_parser.add_argument('--ai-agent', action='store_true', default=True, help='Use AI agent for analysis')
    
    # Pre-RAG Classifier commands
    classifier_parser = subparsers.add_parser('classifier', help='Pre-RAG classifier commands')
    classifier_subparsers = classifier_parser.add_subparsers(dest='classifier_command')
    
    test_parser = classifier_subparsers.add_parser('test', help='Test classifier on log file')
    test_parser.add_argument('--file', required=True, help='Log file to test')
    test_parser.add_argument('--output', help='Output file for filtered logs')
    test_parser.add_argument('--stats', action='store_true', help='Show detailed statistics')
    
    # AI Agent commands
    agent_parser = subparsers.add_parser('agent', help='AI Agent management commands')
    agent_subparsers = agent_parser.add_subparsers(dest='agent_command')
    
    status_parser = agent_subparsers.add_parser('status', help='Show AI agent status')
    
    config_parser = agent_subparsers.add_parser('configure', help='Configure AI agent settings')
    config_parser.add_argument('--learning-threshold', type=int, help='Pattern learning threshold')
    config_parser.add_argument('--high-threat-interval', type=int, help='High threat monitoring interval')
    config_parser.add_argument('--enable', action='store_true', help='Enable AI agent')
    config_parser.add_argument('--disable', action='store_true', help='Disable AI agent')
    
    reset_parser = agent_subparsers.add_parser('reset', help='Reset AI agent learning data')
    reset_parser.add_argument('--confirm', action='store_true', help='Confirm reset operation')
    
    # Data retrieval commands
    data_parser = subparsers.add_parser('data', help='MongoDB data retrieval commands')
    data_subparsers = data_parser.add_subparsers(dest='data_command')
    
    # Analysis data retrieval
    analysis_data_parser = data_subparsers.add_parser('analysis', help='Retrieve analysis data')
    analysis_data_parser.add_argument('--limit', type=int, default=10, help='Maximum records to retrieve')
    analysis_data_parser.add_argument('--user', help='Filter by username')
    analysis_data_parser.add_argument('--export', help='Export to file (specify filename)')
    analysis_data_parser.add_argument('--format', choices=['json', 'csv'], default='json', help='Export format')
    
    # Monitoring sessions retrieval
    sessions_data_parser = data_subparsers.add_parser('sessions', help='Retrieve monitoring sessions')
    sessions_data_parser.add_argument('--limit', type=int, default=10, help='Maximum records to retrieve')
    sessions_data_parser.add_argument('--export', help='Export to file (specify filename)')
    sessions_data_parser.add_argument('--format', choices=['json', 'csv'], default='json', help='Export format')
    
    # Collection statistics
    stats_parser = data_subparsers.add_parser('stats', help='Show collection statistics')
    
    # List all collections
    list_parser = data_subparsers.add_parser('list', help='List all available collections')
    
    args = parser.parse_args()
    
    if not args.command:
        print_banner()
        parser.print_help()
        return
    
    # Print banner for all commands
    print_banner()
    
    # Attempt auto-login if not a login command
    if not (args.command == 'auth' and args.auth_command == 'login'):
        if hasattr(cli, '_stored_encrypted_credentials'):
            # Only try auto-login for commands that need authentication
            needs_auth_commands = ['monitor', 'analyze', 'profile', 'agent', 'data']
            if args.command in needs_auth_commands:
                password = getpass.getpass(f"🔑 Password to decrypt stored credentials for {cli._stored_username}: ")
                cli.encryption_key = cli._generate_encryption_key(password)
                if cli._load_stored_token():
                    success_message(f"Automatically logged in as {cli._stored_username}")
    
    # Handle commands
    if args.command == 'auth':
        if args.auth_command == 'login':
            password = args.password or getpass.getpass("🔑 Password: ")
            success = asyncio.run(cli.authenticate(args.username, password, args.api_url))
            if success:
                success_message("Authentication successful!")
            else:
                error_message("Authentication failed!")
                sys.exit(1)
        
        elif args.auth_command == 'register':
            password = args.password or getpass.getpass("🔑 Password: ")
            confirm_password = getpass.getpass("🔑 Confirm password: ")
            
            if password != confirm_password:
                error_message("Passwords do not match!")
                sys.exit(1)
            
            success = asyncio.run(cli.register_user(args.username, args.email, password))
            if success:
                success_message("Registration successful!")
                info_message("You can now login with your credentials.")
            else:
                error_message("Registration failed!")
                sys.exit(1)
        
        elif args.auth_command == 'profile':
            profile = asyncio.run(cli.get_user_profile())
            if profile:
                profile_table = create_status_table({
                    'username': profile.get('username'),
                    'email': profile.get('email')
                }, "👤 User Profile")
                console.print(profile_table)
                success_message("Profile retrieved successfully!")
            else:
                error_message("Failed to retrieve profile. Please check authentication.")
                sys.exit(1)
    
    elif args.command == 'profile':
        if args.profile_command == 'setup':
            success = asyncio.run(cli.setup_monitoring_profile(
                args.log_path, 
                args.interval, 
                args.max_results,
                not args.no_enhance,
                not args.no_ai_agent
            ))
            if success:
                profile_data = {
                    'log_file': args.log_path,
                    'interval': f"{args.interval} seconds",
                    'ai_enhancement': not args.no_enhance,
                    'ai_agent': not args.no_ai_agent
                }
                profile_table = create_status_table(profile_data, "📋 Monitoring Profile")
                console.print(profile_table)
            else:
                error_message("Failed to setup monitoring profile!")
                sys.exit(1)
        
        elif args.profile_command == 'setup-dynamic':
            if args.list_sources:
                sources = cli.get_available_log_sources()
                
                sources_table = Table(title="📋 Available Log Sources", box=box.ROUNDED)
                sources_table.add_column("ID", style="cyan")
                sources_table.add_column("Description", style="white")
                sources_table.add_column("Type", style="green")
                
                for source in sources:
                    sources_table.add_row(
                        source['id'],
                        source['description'],
                        source['type']
                    )
                console.print(sources_table)
                return
            
            success = asyncio.run(cli.setup_dynamic_monitoring(
                args.sources,
                args.interval,
                not args.no_enhance,
                not args.no_ai_agent
            ))
            if success:
                dynamic_data = {
                    'sources': ', '.join(args.sources) if args.sources else 'All available',
                    'interval': f"{args.interval} seconds",
                    'ai_enhancement': not args.no_enhance,
                    'ai_agent': not args.no_ai_agent
                }
                dynamic_table = create_status_table(dynamic_data, "🔄 Dynamic Monitoring Profile")
                console.print(dynamic_table)
            else:
                error_message("Failed to setup dynamic monitoring profile!")
                sys.exit(1)
        
        elif args.profile_command == 'status':
            status = asyncio.run(cli.get_profile_status())
            
            if status.get('status') == 'active':
                status_data = {
                    'status': status.get('status'),
                    'user': f"{status.get('user')} ({status.get('email')})",
                    'log_path': status.get('log_path'),
                    'interval': f"{status.get('interval')} seconds",
                    'max_results': status.get('max_results'),
                    'ai_enhancement': status.get('auto_enhance'),
                    'ai_agent_enabled': status.get('ai_agent_enabled')
                }
                
                if status.get('log_file_size'):
                    status_data['log_file_size'] = f"{status.get('log_file_size'):,} bytes"
                    status_data['last_modified'] = status.get('log_file_modified')
                
                status_table = create_status_table(status_data, "📊 Profile Status")
                console.print(status_table)
                
                if status.get('ai_agent_status'):
                    agent_status = status['ai_agent_status']
                    agent_table = create_status_table({
                        'learned_patterns': agent_status.get('learned_patterns'),
                        'total_analyses': agent_status.get('total_analyses'),
                        'recent_analyses_24h': agent_status.get('recent_analyses_24h'),
                        'threat_history': agent_status.get('threat_history_count')
                    }, "🤖 AI Agent Status")
                    console.print(agent_table)
            else:
                error_message(f"Profile status: {status.get('status')}")
                if status.get('message'):
                    console.print(f"[dim]{status.get('message')}[/dim]")
        
        elif args.profile_command == 'update':
            updates = {}
            if args.interval:
                updates['interval'] = args.interval
            if args.max_results:
                updates['max_results'] = args.max_results
            if args.enable_ai:
                updates['auto_enhance'] = True
            elif args.disable_ai:
                updates['auto_enhance'] = False
            if args.enable_agent:
                updates['enable_ai_agent'] = True
            elif args.disable_agent:
                updates['enable_ai_agent'] = False
            
            if updates:
                success = asyncio.run(cli.update_profile_settings(**updates))
                if success:
                    update_table = create_status_table(updates, "🔧 Profile Updates")
                    console.print(update_table)
                else:
                    error_message("Failed to update profile settings!")
                    sys.exit(1)
            else:
                info_message("No settings to update. Use --help for available options.")
    
    elif args.command == 'send':
        # Check authentication
        if not cli.session_token:
            password = getpass.getpass("🔑 Password to decrypt stored credentials: ")
            credentials = cli._load_credentials(password)
            if not credentials:
                error_message("No valid credentials found. Please login first.")
                sys.exit(1)
        
        result = asyncio.run(cli.send_log_file(args.file, not args.no_enhance))
        if result:
            success_message("Log analysis completed!")
            
            analysis_summary = {
                'summary': result.get('summary', 'N/A')[:100] + '...',
                'techniques_found': len(result.get('matched_techniques', [])),
                'ai_enhanced': result.get('ai_enhanced', False)
            }
            summary_table = create_status_table(analysis_summary, "📊 Analysis Summary")
            console.print(summary_table)
        else:
            error_message("Analysis failed!")
    
    elif args.command == 'monitor':
        if args.dynamic:
            # Handle automated monitoring setup
            if args.enable_auto:
                if not cli.session_token:
                    password = getpass.getpass("🔑 Enter password to enable automated monitoring: ")
                    credentials = cli._load_credentials(password)
                    if not credentials:
                        error_message("No valid credentials found. Please login first.")
                        sys.exit(1)
                
                if cli.enable_automated_monitoring(password):
                    success_message("Automated monitoring enabled! Future monitoring will run without password prompts.")
                    console.print("[dim]Note: Set LOGIQ_AUTO_PASSWORD environment variable for full automation[/dim]")
                else:
                    error_message("Failed to enable automated monitoring")
                    sys.exit(1)
                return
            
            # Check authentication - try automatic loading first
            if not cli.session_token:
                # Check if automated monitoring is enabled
                automated_enabled = cli.config.get('automated_monitoring', {}).get('enabled', False)
                
                if automated_enabled:
                    # Try to load credentials automatically from environment or config
                    import os
                    auto_password = os.getenv('LOGIQ_AUTO_PASSWORD')
                    if auto_password:
                        cli.encryption_key = cli._generate_encryption_key(auto_password)
                        if cli._load_stored_token():
                            success_message("Automatically loaded credentials for monitoring")
                        else:
                            error_message("Failed to load stored credentials automatically")
                            sys.exit(1)
                    else:
                        error_message("Automated monitoring enabled but LOGIQ_AUTO_PASSWORD not set")
                        console.print("[dim]Set environment variable: export LOGIQ_AUTO_PASSWORD='your_password'[/dim]")
                        sys.exit(1)
                else:
                    # Fall back to manual password prompt
                    password = getpass.getpass("🔑 Password to decrypt stored credentials: ")
                    credentials = cli._load_credentials(password)
                    if not credentials:
                        error_message("No valid credentials found. Please login first.")
                        sys.exit(1)
            
            section_header("Dynamic System Log Monitoring", "🚀")
            console.print("[dim]📊 Logs will be extracted from system sources every 5 minutes[/dim]")
            console.print("[dim]🔄 Data will be automatically sent to LogIQ and stored in MongoDB[/dim]")
            console.print("[dim]🤖 AI Agent will provide enhanced analysis and adaptive scheduling[/dim]")
            console.print("[dim]Press Ctrl+C to stop monitoring[/dim]\n")
            
            # If interval is specified, update config temporarily
            if args.interval:
                original_interval = cli.config.get('dynamic_monitoring', {}).get('interval', 300)
                if 'dynamic_monitoring' not in cli.config:
                    cli.config['dynamic_monitoring'] = {}
                cli.config['dynamic_monitoring']['interval'] = args.interval
                info_message(f"Using custom interval: {args.interval} seconds")
            
            try:
                asyncio.run(cli.start_dynamic_monitoring())
            except KeyboardInterrupt:
                console.print("\n[bold red]🛑 Monitoring stopped by user[/bold red]")
                # Set CLI status to inactive when monitoring stops
                if cli.session_token and cli.config.get('username'):
                    asyncio.run(cli._update_cli_status(False))
            finally:
                # Restore original interval if it was changed
                if args.interval and 'original_interval' in locals():
                    cli.config['dynamic_monitoring']['interval'] = original_interval
        
        elif args.start:
            # Check authentication
            if not cli.session_token:
                password = getpass.getpass("🔑 Password to decrypt stored credentials: ")
                credentials = cli._load_credentials(password)
                if not credentials:
                    error_message("No valid credentials found. Please login first.")
                    sys.exit(1)
            
            section_header("File-Based Log Monitoring", "🚀")
            console.print("[dim]📊 Logs will be automatically sent to LogIQ and stored in MongoDB[/dim]")
            console.print("[dim]🤖 AI Agent will provide enhanced analysis and adaptive scheduling[/dim]")
            console.print("[dim]Press Ctrl+C to stop monitoring[/dim]\n")
            
            asyncio.run(cli.start_background_monitoring())
            
        elif args.schedule:
            if not cli.session_token:
                password = getpass.getpass("🔑 Password to decrypt stored credentials: ")
                credentials = cli._load_credentials(password)
                if not credentials:
                    error_message("No valid credentials found. Please login first.")
                    sys.exit(1)
            
            section_header("Scheduled Analysis", "⏰")
            console.print("[dim]Press Ctrl+C to stop[/dim]")
            cli.schedule_analysis()
    
    elif args.command == 'analyze':
        # Check authentication
        if not cli.session_token:
            password = getpass.getpass("🔑 Password to decrypt stored credentials: ")
            credentials = cli._load_credentials(password)
            if not credentials:
                error_message("No valid credentials found. Please login first.")
                sys.exit(1)
        
        result = asyncio.run(cli.send_log_file(args.file, args.enhanced, args.ai_agent))
        if result:
            success_message("Analysis completed!")
            
            # Enhanced output with AI agent insights
            if args.ai_agent and 'ai_agent_analysis' in result:
                ai_analysis = result['ai_agent_analysis']
                threat_context = ai_analysis.get('threat_context', {})
                
                ai_panel = Panel.fit(
                    f"[bold cyan]AI Agent Enhanced Analysis[/bold cyan]\n\n"
                    f"[yellow]Threat Level:[/yellow] {threat_context.get('severity_level', 'Unknown')}\n"
                    f"[yellow]Confidence:[/yellow] {threat_context.get('confidence_score', 0):.2f}\n"
                    f"[yellow]Patterns:[/yellow] {len(ai_analysis.get('detected_patterns', []))}\n"
                    f"[yellow]Recommendations:[/yellow] {len(ai_analysis.get('recommendations', []))}",
                    border_style="cyan"
                )
                console.print(ai_panel)
                
                # Show recommendations
                recommendations = ai_analysis.get('recommendations', [])
                if recommendations:
                    rec_table = Table(title="🎯 Top Recommendations", box=box.ROUNDED)
                    rec_table.add_column("#", style="cyan", width=3)
                    rec_table.add_column("Action", style="yellow")
                    rec_table.add_column("Priority", style="red")
                    rec_table.add_column("Description", style="white")
                    
                    for i, rec in enumerate(recommendations[:5], 1):
                        rec_table.add_row(
                            str(i),
                            rec.get('action', 'N/A'),
                            rec.get('priority', 'N/A'),
                            rec.get('description', 'N/A')[:50] + "..." if len(rec.get('description', '')) > 50 else rec.get('description', 'N/A')
                        )
                    console.print(rec_table)
            
            if args.output:
                with open(args.output, 'w') as f:
                    json.dump(result, f, indent=2, default=str)
                success_message(f"Results saved to: {args.output}")
            else:
                # Display formatted JSON
                syntax = Syntax(json.dumps(result, indent=2, default=str), "json", theme="monokai", line_numbers=True)
                console.print(syntax)
        else:
            error_message("Analysis failed!")
    
    elif args.command == 'classifier':
        if args.classifier_command == 'test':
            # Test the Pre-RAG classifier on a log file
            if not os.path.exists(args.file):
                error_message(f"Log file not found: {args.file}")
                sys.exit(1)
            
            try:
                with open(args.file, 'r', encoding='utf-8') as f:
                    log_content = f.read()
                
                info_message(f"🧪 Testing Pre-RAG classifier on {args.file}")
                info_message(f"📊 Original file size: {len(log_content):,} characters")
                
                # Test the classifier
                filtered_content = cli.filter_logs_with_classifier(log_content, max_size=45000)
                
                # Show results
                filtered_lines = filtered_content.split('\n')
                original_lines = log_content.split('\n')
                
                console.print(f"\n[bold green]✅ Classification Results:[/bold green]")
                console.print(f"   Original logs: {len(original_lines):,} lines")
                console.print(f"   Threat logs: {len(filtered_lines):,} lines")
                console.print(f"   Filtered out: {len(original_lines) - len(filtered_lines):,} lines")
                console.print(f"   Size reduction: {(1 - len(filtered_content)/len(log_content))*100:.1f}%")
                
                # Show classifier statistics if requested
                if args.stats and cli.prerag_classifier:
                    stats = cli.prerag_classifier.get_stats()
                    console.print(f"\n[bold blue]📈 Classifier Statistics:[/bold blue]")
                    console.print(f"   Total processed: {stats['total_processed']:,}")
                    console.print(f"   Cache hits: {stats['cache_hits']:,} ({stats['cache_hit_rate']:.1%})")
                    console.print(f"   Threats detected: {stats['threats_detected']:,} ({stats['threat_rate']:.1%})")
                    console.print(f"   Logs filtered: {stats['logs_filtered']:,} ({stats['filter_rate']:.1%})")
                
                # Save filtered logs if output file specified
                if args.output:
                    with open(args.output, 'w', encoding='utf-8') as f:
                        f.write(filtered_content)
                    success_message(f"Filtered logs saved to: {args.output}")
                
            except Exception as e:
                error_message(f"Error testing classifier: {e}")
    
    elif args.command == 'agent':
        if args.agent_command == 'status':
            if cli.ai_agent:
                status = cli.ai_agent.get_agent_status()
                
                agent_table = create_status_table({
                    'status': status['status'],
                    'learned_patterns': status['learned_patterns'],
                    'total_analyses': status['total_analyses'],
                    'recent_analyses_24h': status['recent_analyses_24h'],
                    'threat_history': status['threat_history_count'],
                    'last_analysis': status['last_analysis'] or 'Never'
                }, "🤖 AI Agent Status")
                console.print(agent_table)
            else:
                warning_message("AI Agent is not initialized")
        
        elif args.agent_command == 'configure':
            if args.enable:
                cli.config['ai_agent_enabled'] = True
                cli.ai_agent = AIAgent(cli)
                success_message("AI Agent enabled")
            elif args.disable:
                cli.config['ai_agent_enabled'] = False
                cli.ai_agent = None
                success_message("AI Agent disabled")
            
            if cli.ai_agent:
                updates = {}
                if args.learning_threshold:
                    cli.ai_agent.config['learning_threshold'] = args.learning_threshold
                    updates['learning_threshold'] = args.learning_threshold
                if args.high_threat_interval:
                    cli.ai_agent.config['high_threat_interval'] = args.high_threat_interval
                    updates['high_threat_interval'] = args.high_threat_interval
                
                if updates:
                    cli.ai_agent._save_agent_state()
                    config_table = create_status_table(updates, "🔧 AI Agent Configuration")
                    console.print(config_table)
                    success_message("AI Agent configuration updated")
            
            cli._save_config()
        
        elif args.agent_command == 'reset':
            if args.confirm and cli.ai_agent:
                # Reset AI agent learning data
                cli.ai_agent.learned_patterns.clear()
                cli.ai_agent.analysis_history.clear()
                cli.ai_agent.threat_history.clear()
                cli.ai_agent._save_agent_state()
                success_message("AI Agent learning data reset")
            else:
                warning_message("Use --confirm flag to reset AI agent data")
    
    elif args.command == 'data':
        if not args.data_command:
            error_message("Please specify a data command. Use 'python cli_tool.py data --help' for options.")
            return
        
        if args.data_command == 'analysis':
            analysis_data = asyncio.run(cli.retrieve_analysis_data(args.limit, args.user))
            
            if args.export:
                success = asyncio.run(cli.export_collection_data('analysis', args.export, args.limit, args.format))
                if success:
                    success_message(f"Analysis data exported to {args.export}")
                else:
                    error_message("Failed to export analysis data")
            else:
                cli.display_analysis_data(analysis_data)
        
        elif args.data_command == 'sessions':
            sessions_data = asyncio.run(cli.retrieve_monitoring_sessions(args.limit))
            
            if args.export:
                success = asyncio.run(cli.export_collection_data('monitoring', args.export, args.limit, args.format))
                if success:
                    success_message(f"Monitoring sessions exported to {args.export}")
                else:
                    error_message("Failed to export monitoring sessions")
            else:
                cli.display_monitoring_sessions(sessions_data)
        
        elif args.data_command == 'stats':
            stats = asyncio.run(cli.get_collection_stats())
            cli.display_collection_stats(stats)
        
        elif args.data_command == 'list':
            section_header("Available MongoDB Collections", "📋")
            
            collections_table = Table(box=box.ROUNDED, border_style="bright_green")
            collections_table.add_column("Collection", style="cyan", no_wrap=True)
            collections_table.add_column("Description", style="white")
            collections_table.add_column("Data Type", style="yellow")
            
            collections_table.add_row(
                "🔍 analysis",
                "Log analysis results with MITRE ATT&CK techniques",
                "Analysis Data"
            )
            collections_table.add_row(
                "📊 sessions", 
                "Active monitoring configurations and statistics",
                "Session Data"
            )
            collections_table.add_row(
                "👥 users",
                "User authentication and profile information", 
                "User Data"
            )
            
            console.print(collections_table)
            console.print("\n[dim]Use 'python cli_tool.py data <collection> --help' for retrieval options.[/dim]")

if __name__ == "__main__":
    main()
 