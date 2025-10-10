# edubaseid/utils.py
"""
Utility functions for the SDK.
"""

import secrets
from datetime import datetime
from typing import Dict, Tuple
from urllib.parse import urlparse

import requests
from requests.exceptions import RequestException

from .exceptions import NetworkError

def generate_state_token() -> str:
    """Generate secure state token."""
    return secrets.token_urlsafe(16)

def generate_pkce_pair() -> Tuple[str, str]:
    """Generate PKCE code verifier and challenge."""
    verifier = secrets.token_urlsafe(32)
    challenge = verifier  # Simplify, use base64 in production
    return verifier, challenge

def parse_jwt(token: str) -> Dict:
    """Parse JWT (stub)."""
    raise NotImplementedError

def now_utc() -> datetime:
    """Get current UTC time."""
    return datetime.utcnow()

def validate_redirect_uri(uri: str) -> bool:
    """Validate redirect URI."""
    parsed = urlparse(uri)
    return parsed.scheme in ('http', 'https') and bool(parsed.netloc)

def build_auth_header(token: str) -> Dict:
    """Build Authorization header."""
    return {'Authorization': f'Bearer {token}'}

def get_oauth_headers(token: str) -> Dict:
    """Get OAuth headers."""
    return build_auth_header(token)

def safe_request(method: str, url: str, **kwargs) -> requests.Response:
    """Safe HTTP request with error handling."""
    try:
        response = requests.request(method, url, **kwargs)
        response.raise_for_status()
        return response
    except RequestException as e:
        raise NetworkError(f"Request failed: {str(e)}")