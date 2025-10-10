# edubaseid/client.py
"""
Module for EduBaseID OAuth2/OpenID Connect client.
Provides EduBaseIDClient class for handling authentication flows.
"""

import secrets
from typing import Dict, List, Optional
from urllib.parse import urlencode

import requests

from .config import get_config
from .exceptions import EduBaseIDError, InvalidClientError, UnauthorizedError
from .utils import generate_state_token, safe_request

class EduBaseIDClient:
    """
    EduBaseID OAuth2 client for authentication and user management.

    Usage example:
    >>> client = EduBaseIDClient()
    >>> auth_url = client.get_authorize_url()
    >>> print(auth_url)  # Redirect user to this URL
    """

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or get_config()
        self.server_url = self.config.get('SERVER_URL', 'https://id.edubase.uz')
        self.client_id = self.config['CLIENT_ID']
        self.client_secret = self.config['CLIENT_SECRET']
        self.redirect_uri = self.config['REDIRECT_URI']
        self.scopes = self.config.get('SCOPES', ['openid', 'profile', 'email'])
        self.timeout = self.config.get('TIMEOUT', 10)

    def get_authorize_url(self, state: Optional[str] = None, scopes: Optional[List[str]] = None) -> str:
        """
        Generate OAuth authorization URL.

        :param state: Optional CSRF state token
        :param scopes: Optional list of scopes
        :return: Authorization URL
        :raises EduBaseIDError: If configuration is invalid
        """
        scopes = scopes or self.scopes
        state = state or generate_state_token()
        params = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'response_type': 'code',
            'scope': ' '.join(scopes),
            'state': state,
        }
        return f"{self.server_url}/oauth/authorize/?{urlencode(params)}"

    def exchange_code_for_token(self, code: str) -> Dict:
        """
        Exchange authorization code for access token.

        :param code: Authorization code from callback
        :return: Token data dictionary
        :raises EduBaseIDError: On exchange failure
        """
        data = {
            'grant_type': 'authorization_code',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': code,
            'redirect_uri': self.redirect_uri,
        }
        response = safe_request('POST', f"{self.server_url}/oauth/token/", data=data, timeout=self.timeout)
        return response.json()

    def get_user_info(self, access_token: str) -> Dict:
        """
        Fetch user information using access token.

        :param access_token: Valid access token
        :return: User data dictionary
        :raises UnauthorizedError: If token is invalid
        """
        headers = {'Authorization': f'Bearer {access_token}'}
        response = safe_request('GET', f"{self.server_url}/oauth/userinfo/", headers=headers, timeout=self.timeout)
        if response.status_code == 401:
            raise UnauthorizedError("Invalid access token")
        return response.json()

    def refresh_access_token(self, refresh_token: str) -> Dict:
        """
        Refresh access token using refresh token.

        :param refresh_token: Valid refresh token
        :return: New token data
        :raises EduBaseIDError: On refresh failure
        """
        data = {
            'grant_type': 'refresh_token',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'refresh_token': refresh_token,
        }
        response = safe_request('POST', f"{self.server_url}/oauth/token/", data=data, timeout=self.timeout)
        return response.json()

    def logout(self, access_token: str) -> bool:
        """
        Perform logout on server.

        :param access_token: Access token to revoke
        :return: Success status
        """
        headers = {'Authorization': f'Bearer {access_token}'}
        response = safe_request('POST', f"{self.server_url}/accounts/logout/", headers=headers, timeout=self.timeout)
        return response.ok

    def validate_client(self) -> Dict:
        """
        Validate client configuration.

        :return: Validation result
        :raises InvalidClientError: If client is invalid
        """
        params = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
        }
        response = safe_request('GET', f"{self.server_url}/oauth/validate-client/?{urlencode(params)}", timeout=self.timeout)
        data = response.json()
        if not data.get('valid'):
            raise InvalidClientError(data.get('error', 'Invalid client'))
        return data

    def register_application(self, name: str, redirect_uri: str, website: Optional[str] = None, access_token: str = '') -> Dict:
        """
        Register new OAuth application (requires admin access).

        :param name: Application name
        :param redirect_uri: Redirect URI
        :param website: Optional website URL
        :param access_token: Admin access token
        :return: Application data
        """
        headers = {'Authorization': f'Bearer {access_token}'} if access_token else {}
        data = {'name': name, 'redirect_uris': redirect_uri, 'website': website}
        response = safe_request('POST', f"{self.server_url}/oauth/applications/create/", json=data, headers=headers, timeout=self.timeout)
        return response.json()

    def list_applications(self, access_token: str) -> List[Dict]:
        """
        List user's applications.

        :param access_token: Access token
        :return: List of applications
        """
        headers = {'Authorization': f'Bearer {access_token}'}
        response = safe_request('GET', f"{self.server_url}/oauth/applications/", headers=headers, timeout=self.timeout)
        return response.json()

    def revoke_application(self, app_id: int, access_token: str) -> Dict:
        """
        Revoke application.

        :param app_id: Application ID
        :param access_token: Access token
        :return: Response message
        """
        headers = {'Authorization': f'Bearer {access_token}'}
        response = safe_request('POST', f"{self.server_url}/oauth/applications/{app_id}/revoke/", headers=headers, timeout=self.timeout)
        return response.json()

    def decode_jwt(self, token: str) -> Dict:
        """
        Decode JWT token (if applicable).

        Note: Current implementation assumes non-JWT tokens; stub for future use.
        """
        # Implement with jwt if tokens are JWT
        raise NotImplementedError("JWT decoding not supported in current token format")

    def verify_token(self, token: str) -> bool:
        """
        Verify token validity.

        :param token: Token to verify
        :return: Validity status
        """
        try:
            self.get_user_info(token)
            return True
        except UnauthorizedError:
            return False