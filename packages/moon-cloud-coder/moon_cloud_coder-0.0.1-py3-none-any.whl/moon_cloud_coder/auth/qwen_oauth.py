"""Qwen OAuth Authentication Module for Moon-Cloud-Coder.

This module implements Qwen OAuth authentication flow, including:
- Device authorization flow
- PKCE (Proof Key for Code Exchange)
- Token management and caching
- Cross-process token synchronization
"""

import os
import json
import time
import secrets
import base64
import hashlib
import threading
import requests
import webbrowser
import uuid
from typing import Optional, Dict, Any
from pathlib import Path
import urllib.parse
from datetime import datetime, timedelta
from rich.console import Console
from moon_cloud_coder.utils.logger import get_logger, LoggerConfig

# OAuth Endpoints
QWEN_OAUTH_BASE_URL = 'https://chat.qwen.ai'
QWEN_OAUTH_DEVICE_CODE_ENDPOINT = f'{QWEN_OAUTH_BASE_URL}/api/v1/oauth2/device/code'
QWEN_OAUTH_TOKEN_ENDPOINT = f'{QWEN_OAUTH_BASE_URL}/api/v1/oauth2/token'
QWEN_OAUTH_AUTHORIZATION_ENDPOINT = f'{QWEN_OAUTH_BASE_URL}/authorize'

# OAuth Client Configuration
QWEN_OAUTH_CLIENT_ID = os.getenv('QWEN_OAUTH_CLIENT_ID', 'f0304373b74a44d2b584a3fb70ca9e56')
QWEN_OAUTH_SCOPE = 'openid profile email model.completion'

# File System Configuration
QWEN_DIR = Path.home() / '.moon-cloud-coder'
QWEN_CREDENTIAL_FILENAME = 'oauth_creds.json'
QWEN_LOCK_FILENAME = 'oauth_creds.lock'

# Token and Cache Configuration
TOKEN_REFRESH_BUFFER_SECONDS = 30  # 30 seconds before expiry
LOCK_TIMEOUT_SECONDS = 10  # 10 seconds lock timeout

console = Console()

LoggerConfig()
logger = get_logger(__name__)

class QwenCredentials:
    """Qwen OAuth2 credentials class"""
    
    def __init__(self, 
                 access_token: Optional[str] = None,
                 refresh_token: Optional[str] = None,
                 id_token: Optional[str] = None,
                 expiry_date: Optional[float] = None,
                 token_type: Optional[str] = 'Bearer',
                 resource_url: Optional[str] = None):
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.id_token = id_token
        self.expiry_date = expiry_date
        self.token_type = token_type
        self.resource_url = resource_url
    
    def is_valid(self) -> bool:
        """Check if the credentials are still valid"""
        if not self.access_token:
            return False
        if not self.expiry_date:
            return False
        # Check if token expires within the refresh buffer
        return time.time() < self.expiry_date - TOKEN_REFRESH_BUFFER_SECONDS
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert credentials to dictionary"""
        return {
            'access_token': self.access_token,
            'refresh_token': self.refresh_token,
            'id_token': self.id_token,
            'expiry_date': self.expiry_date,
            'token_type': self.token_type,
            'resource_url': self.resource_url
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'QwenCredentials':
        """Create credentials from dictionary"""
        return cls(
            access_token=data.get('access_token'),
            refresh_token=data.get('refresh_token'),
            id_token=data.get('id_token'),
            expiry_date=data.get('expiry_date'),
            token_type=data.get('token_type'),
            resource_url=data.get('resource_url')
        )

def generate_code_verifier() -> str:
    """Generate a random code verifier for PKCE"""
    return base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8').rstrip('=')

def generate_code_challenge(code_verifier: str) -> str:
    """Generate a code challenge from a code verifier using SHA-256"""
    hashed = hashlib.sha256(code_verifier.encode('utf-8')).digest()
    return base64.urlsafe_b64encode(hashed).decode('utf-8').rstrip('=')

def generate_pkce_pair() -> Dict[str, str]:
    """Generate PKCE code verifier and challenge pair"""
    code_verifier = generate_code_verifier()
    code_challenge = generate_code_challenge(code_verifier)
    return {'code_verifier': code_verifier, 'code_challenge': code_challenge}

class QwenOAuth2Client:
    """Qwen OAuth2 client implementation"""
    
    def __init__(self):
        self.credentials: Optional[QwenCredentials] = None
        self.lock = threading.Lock()
        self.token_manager = SharedTokenManager()
    
    def request_device_authorization(self, scope: str, code_challenge: str, code_challenge_method: str = 'S256'):
        """Request device authorization from Qwen OAuth server"""
        body_data = {
            'client_id': QWEN_OAUTH_CLIENT_ID,
            'scope': scope,
            'code_challenge': code_challenge,
            'code_challenge_method': code_challenge_method,
        }
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json',
            'x-request-id': str(uuid.uuid4()),
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        }
        
        response = requests.post(QWEN_OAUTH_DEVICE_CODE_ENDPOINT, data=body_data, headers=headers)
        
        # Check if the response is successful
        if not response.ok:
            # Try to get error details from response
            try:
                error_data = response.json()
                error_msg = f"Device authorization failed: {response.status_code} {response.reason}. Response: {error_data}"
            except Exception:
                # If JSON parsing fails, use text response
                error_text = response.text
                error_msg = f"Device authorization failed: {response.status_code} {response.reason}. Response: {error_text}"
            
            raise Exception(error_msg)
        
        # Check response content type
        content_type = response.headers.get('Content-Type', '')
        if 'application/json' not in content_type:
            # If response is not JSON, it might be an error page
            error_text = response.text[:500]  # Limit to first 500 chars
            raise Exception(f"Device authorization failed: Expected JSON response but got {content_type}. Response preview: {error_text}")
        
        result = response.json()
        console.print(f"[bold yellow] request_device_authorization: {result} [/bold yellow]")
        
        # Validate response
        if 'device_code' not in result or 'user_code' not in result:
            raise Exception(f"Invalid device authorization response: {result}")
        
        # Add the authorization URL for the user to visit
        # Based on the example: https://chat.qwen.ai/authorize?user_code=xxx&client=qwen-code
        # TODO-LYY
        result['verification_uri_complete'] = f"{QWEN_OAUTH_AUTHORIZATION_ENDPOINT}?user_code={result['user_code']}&client=qwen-code"
        
        return result
    
    def poll_device_token(self, device_code: str, code_verifier: str):
        """Poll for device token from Qwen OAuth server"""
        body_data = {
            'grant_type': 'urn:ietf:params:oauth:grant-type:device_code',
            'client_id': QWEN_OAUTH_CLIENT_ID,
            'device_code': device_code,
            'code_verifier': code_verifier,
        }
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json',
            'x-request-id': str(uuid.uuid4()),
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        }
        
        response = requests.post(QWEN_OAUTH_TOKEN_ENDPOINT, data=body_data, headers=headers)
        
        if response.status_code == 400:
            error_data = response.json()
            if error_data.get('error') == 'authorization_pending':
                return {'status': 'pending'}
            elif error_data.get('error') == 'slow_down':
                return {'status': 'pending', 'slow_down': True}
            else:
                raise Exception(f"Token polling failed: {error_data}")
        elif not response.ok:
            raise Exception(f"Token polling failed: {response.status_code} {response.text}")
        
        return response.json()
    
    def refresh_access_token(self) -> Dict[str, Any]:
        """Refresh access token using refresh token"""
        logger.debug(f"refresh_access_token credentials: {self.credentials}")
        if not self.credentials or not self.credentials.refresh_token:
            raise Exception("No refresh token available")
        logger.debug(f"refresh_access_token credentials: {self.credentials.to_dict()}")
        body_data = {
            'grant_type': 'refresh_token',
            'refresh_token': self.credentials.refresh_token,
            'client_id': QWEN_OAUTH_CLIENT_ID,
        }
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json',
            'x-request-id': str(uuid.uuid4()),
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        }
        
        response = requests.post(QWEN_OAUTH_TOKEN_ENDPOINT, data=body_data, headers=headers)
        console.print(f"[bold yellow] refresh_access_token response: {response} [/bold yellow]")
        
        if not response.ok:
            # Handle 400 errors which might indicate refresh token expiry
            if response.status_code == 400:
                self.clear_credentials()
                raise Exception("Refresh token expired or invalid. Please re-authenticate.")
            raise Exception(f"Token refresh failed: {response.status_code} {response.text}")
        
        response_data = response.json()
        logger.debug(f"refresh_access_token response: {response_data}")
        
        if 'error' in response_data:
            raise Exception(f"Token refresh failed: {response_data}")
        
        # Update credentials with new tokens
        self.credentials.access_token = response_data.get('access_token')
        self.credentials.token_type = response_data.get('token_type')
        self.credentials.refresh_token = response_data.get('refresh_token', self.credentials.refresh_token)
        self.credentials.resource_url = response_data.get('resource_url')
        self.credentials.expiry_date = time.time() + response_data.get('expires_in', 3600)
        
        # Save credentials to file
        self.save_credentials(self.credentials)
        
        return response_data
    
    def get_access_token(self) -> Optional[str]:
        """Get valid access token, refreshing if necessary"""
        # Try to get valid credentials from token manager first
        try:
            credentials = self.token_manager.get_valid_credentials(self)
            return credentials.access_token if credentials else None
        except Exception as e:
            print(f"Failed to get access token from shared manager: {e}")
            return None
    
    def save_credentials(self, credentials: QwenCredentials) -> None:
        """Save credentials to file"""
        QWEN_DIR.mkdir(exist_ok=True)
        cred_file_path = QWEN_DIR / QWEN_CREDENTIAL_FILENAME
        
        with open(cred_file_path, 'w', encoding='utf-8') as f:
            json.dump(credentials.to_dict(), f, indent=2, ensure_ascii=False)
        
        # Set restrictive file permissions (read/write for owner only)
        os.chmod(cred_file_path, 0o600)
    
    def load_credentials(self) -> Optional[QwenCredentials]:
        """Load credentials from file"""
        cred_file_path = QWEN_DIR / QWEN_CREDENTIAL_FILENAME
        
        if not cred_file_path.exists():
            return None
        
        try:
            with open(cred_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                credentials = QwenCredentials.from_dict(data)
                
                # Check if token is expired but refresh token exists
                if not credentials.is_valid() and credentials.refresh_token:
                    # Try to refresh the token
                    try:
                        # Create a temporary client to refresh the token
                        temp_client = QwenOAuth2Client()
                        temp_client.credentials = credentials
                        refreshed_data = temp_client.refresh_access_token()
                        
                        # Update with refreshed credentials
                        refreshed_credentials = QwenCredentials.from_dict(refreshed_data)
                        self.save_credentials(refreshed_credentials)
                        print("Token was refreshed automatically.")
                        return refreshed_credentials
                    except Exception as e:
                        print(f"Failed to refresh token: {e}")
                        # Clear credentials if refresh fails
                        self.clear_credentials()
                        return None
                
                # Only return if token is still valid
                if credentials.is_valid():
                    return credentials
                else:
                    return None
        except Exception as e:
            print(f"Failed to load credentials: {e}")
            return None
    
    def clear_credentials(self) -> None:
        """Clear cached credentials from disk"""
        cred_file_path = QWEN_DIR / QWEN_CREDENTIAL_FILENAME
        try:
            cred_file_path.unlink()
            print("Cached Qwen credentials cleared successfully.")
        except FileNotFoundError:
            # File doesn't exist, already cleared
            pass
        except Exception as e:
            print(f"Warning: Failed to clear cached Qwen credentials: {e}")

class SharedTokenManager:
    """Manages OAuth tokens across multiple processes using file-based caching and locking"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.memory_cache: Optional[QwenCredentials] = None
        self.file_mod_time: float = 0
        self.last_check: float = 0
        self.refresh_lock = threading.Lock()
        self.check_lock = threading.Lock()
        
        # Create directory if it doesn't exist
        QWEN_DIR.mkdir(exist_ok=True)
    
    def get_valid_credentials(self, client: QwenOAuth2Client, force_refresh: bool = False) -> QwenCredentials:
        """Get valid OAuth credentials, refreshing them if necessary"""
        with self.check_lock:
            # Check if credentials file has been updated by other sessions
            self._check_and_reload_if_needed(client)
        
        # Return valid cached credentials if available (unless force refresh is requested)
        if not force_refresh and self.memory_cache and self._is_token_valid(self.memory_cache):
            return self.memory_cache
        
        # Use a refresh lock to prevent race conditions
        with self.refresh_lock:
            # Double-check after acquiring lock
            if not force_refresh and self.memory_cache and self._is_token_valid(self.memory_cache):
                return self.memory_cache
            
            try:
                # Perform the actual token refresh
                credentials = client.refresh_access_token()
                qwen_creds = QwenCredentials.from_dict(credentials)
                self.memory_cache = qwen_creds
                client.credentials = qwen_creds
                client.save_credentials(qwen_creds)
                
                return qwen_creds
            except Exception as e:
                # If refresh fails, try to re-authenticate using device flow
                print(f"Token refresh failed: {e}")
                print("Attempting to re-authenticate using device flow...")
                
                # Clear current credentials to force re-authentication
                client.clear_credentials()
                
                # Attempt to authenticate again
                success = authenticate_with_device_flow(client)
                if success:
                    # Update cache with new credentials
                    self.memory_cache = client.credentials
                    self._check_and_reload_if_needed(client)
                    return client.credentials
                else:
                    raise Exception("Failed to refresh or re-authenticate OAuth credentials")
    
    def _check_and_reload_if_needed(self, client: QwenOAuth2Client) -> None:
        """Check if the credentials file was updated by another process and reload if so"""
        now = time.time()
        
        # Limit check frequency to avoid excessive disk I/O
        if now - self.last_check < 5:  # 5 seconds
            return
        
        try:
            cred_file_path = QWEN_DIR / QWEN_CREDENTIAL_FILENAME
            if cred_file_path.exists():
                stat = cred_file_path.stat()
                file_mod_time = stat.st_mtime
                
                # Reload credentials if file has been modified since last cache
                if file_mod_time > self.file_mod_time:
                    with open(cred_file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        self.memory_cache = QwenCredentials.from_dict(data)
                        self.file_mod_time = file_mod_time
                        self.last_check = now
                        
                        # Sync with client
                        if client:
                            client.credentials = self.memory_cache
            else:
                self.memory_cache = None
                self.file_mod_time = 0
        
        except Exception:
            # If there's an error accessing the file, clear the cache
            self.memory_cache = None
            self.file_mod_time = 0
        
        self.last_check = now
    
    def _is_token_valid(self, credentials: QwenCredentials) -> bool:
        """Check if the token is valid and not expired"""
        return credentials.is_valid()
    
    def get_current_credentials(self) -> Optional[QwenCredentials]:
        """Get the current cached credentials (may be expired)"""
        return self.memory_cache

def authenticate_with_device_flow(client: QwenOAuth2Client) -> bool:
    """Perform the Qwen OAuth device flow authentication"""
    try:
        # Generate PKCE code verifier and challenge
        pkce_pair = generate_pkce_pair()
        code_verifier = pkce_pair['code_verifier']
        code_challenge = pkce_pair['code_challenge']
        
        # Request device authorization
        device_auth = client.request_device_authorization(
            scope=QWEN_OAUTH_SCOPE,
            code_challenge=code_challenge,
            code_challenge_method='S256'
        )
        
        # Display authorization info to user
        print(f"\n=== Qwen OAuth Device Authorization ===")
        print(f"Please visit the following URL in your browser to authorize:")
        print(f"\n{device_auth['verification_uri_complete']}\n")
        print(f"Waiting for authorization to complete...\n")
        
        # Optionally open browser
        auto_open = os.getenv('QWEN_AUTO_OPEN_BROWSER', 'true').lower() == 'true'
        if auto_open:
            try:
                webbrowser.open(device_auth['verification_uri_complete'])
            except Exception as e:
                print(f"Failed to open browser: {e}")
                print(f"Please manually visit: {device_auth['verification_uri_complete']}")
        
        # Poll for the token
        poll_interval = 2  # 2 seconds
        max_attempts = int(device_auth['expires_in'] / poll_interval)
        
        for attempt in range(max_attempts):
            print(f"Polling for token... (attempt {attempt + 1}/{max_attempts})")
            token_response = client.poll_device_token(
                device_code=device_auth['device_code'],
                code_verifier=code_verifier
            )
            
            # Check if the response indicates success
            if 'access_token' in token_response:
                # Convert response to credentials format
                credentials = QwenCredentials(
                    access_token=token_response['access_token'],
                    refresh_token=token_response.get('refresh_token'),
                    token_type=token_response.get('token_type', 'Bearer'),
                    resource_url=token_response.get('resource_url'),
                    expiry_date=time.time() + token_response.get('expires_in', 3600)
                )
                
                # Store credentials
                client.credentials = credentials
                client.save_credentials(credentials)
                
                print("Authentication successful! Access token obtained.")
                return True
            
            # Check if the response is pending
            if 'status' in token_response and token_response['status'] == 'pending':
                # Handle slow_down error by increasing poll interval
                if token_response.get('slow_down'):
                    poll_interval = min(poll_interval * 1.5, 10)  # Increase by 50%, max 10 seconds
                    print(f"Server requested to slow down, increasing poll interval to {poll_interval} seconds")
                else:
                    poll_interval = 2  # Reset to default interval
                
                # Wait before next poll
                time.sleep(poll_interval)
                continue
            
            # Handle error response
            if 'error' in token_response:
                raise Exception(f"Token polling failed: {token_response}")
        
        # If we've exhausted attempts
        raise Exception("Authorization timeout, please restart the process.")
    
    except KeyboardInterrupt:
        print("\nAuthentication cancelled by user.")
        return False
    except Exception as e:
        print(f"Device authorization flow failed: {e}")
        return False

def get_or_init_qwen_oauth_client() -> QwenOAuth2Client:
    """Get or initialize Qwen OAuth client with valid credentials"""
    client = QwenOAuth2Client()
    token_manager = SharedTokenManager()
    
    # Try to get valid credentials from shared cache first
    try:
        credentials = token_manager.get_valid_credentials(client)
        if credentials and credentials.is_valid():
            client.credentials = credentials
            return client
        else:
            print("Cached credentials are not valid, attempting to get fresh credentials.")
    except Exception as e:
        print(f"Shared token manager failed: {e}, attempting device flow.")
        
    # Check if we have cached credentials that can be refreshed
    cached_credentials = client.load_credentials()
    if cached_credentials:
        # We have cached credentials, return the client with those credentials
        # The token will be refreshed as needed during API calls
        client.credentials = cached_credentials
        return client
    
    # No cached credentials, use device authorization flow for authentication
    success = authenticate_with_device_flow(client)
    if success:
        return client
    else:
        raise Exception("Qwen OAuth authentication failed")

# def get_current_access_token() -> Optional[str]:
#     """Get the current access token without initiating authentication flow"""
#     client = QwenOAuth2Client()
#     token_manager = SharedTokenManager()
    
#     # Get current credentials from cache (may be expired)
#     cached_credentials = client.load_credentials()
#     if cached_credentials and cached_credentials.is_valid():
#         return cached_credentials.access_token
    
#     return None