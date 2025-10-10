# edubaseid/session.py
"""
Session and token management module.
"""

from datetime import datetime, timedelta
from typing import Dict, Optional

try:
    from django.utils import timezone
    HAS_DJANGO = True
except ImportError:
    HAS_DJANGO = False
    timezone = datetime  # Fallback

from .client import EduBaseIDClient
from .config import get_config
from .exceptions import TokenExpiredError

class SessionManager:
    """
    Manages sessions and tokens.

    Usage:
    >>> manager = SessionManager()
    >>> manager.save_token(1, {'access_token': 'tok'})
    """

    def __init__(self):
        self.storage: Dict[int, Dict] = {}  # In-memory; use Redis in production
        self.config = get_config()
        self.client = EduBaseIDClient()

    def save_token(self, user_id: int, token_data: Dict, expiry_days: int = 1) -> Dict:
        """
        Save token for user.

        :param user_id: User ID
        :param token_data: Token data
        :param expiry_days: Expiry in days
        :return: Saved token
        """
        token_data['expires_at'] = timezone.now() + timedelta(days=expiry_days) if HAS_DJANGO else datetime.now() + timedelta(days=expiry_days)
        self.storage[user_id] = token_data
        return token_data

    def get_token(self, user_id: int) -> Optional[Dict]:
        """
        Get token for user.

        :param user_id: User ID
        :return: Token data or None
        """
        return self.storage.get(user_id)

    def delete_token(self, user_id: int) -> None:
        """
        Delete token.

        :param user_id: User ID
        """
        self.storage.pop(user_id, None)

    def get_token_by_token(self, token: str) -> Optional[Dict]:
        """
        Get token data by token string.
        """
        for data in self.storage.values():
            if data.get('token') == token:
                return data
        return None

    def delete_token_by_token(self, token: str) -> None:
        """
        Delete by token string.
        """
        for user_id, data in list(self.storage.items()):
            if data.get('token') == token:
                del self.storage[user_id]

    def auto_refresh(self, user_id: int) -> Dict:
        """
        Auto refresh token if expired.

        :param user_id: User ID
        :return: Fresh token
        :raises TokenExpiredError: If cannot refresh
        """
        token_data = self.get_token(user_id)
        if not token_data:
            raise TokenExpiredError("No token found")
        now = timezone.now() if HAS_DJANGO else datetime.now()
        if token_data['expires_at'] < now:
            if self.config.get('AUTO_REFRESH_TOKEN'):
                refreshed = self.client.refresh_access_token(token_data['refresh_token'])
                self.save_token(user_id, refreshed)
                return refreshed
            else:
                raise TokenExpiredError("Token expired")
        return token_data

    def clear_expired(self) -> None:
        """Clear expired tokens."""
        now = timezone.now() if HAS_DJANGO else datetime.now()
        for user_id in list(self.storage.keys()):
            if self.storage[user_id]['expires_at'] < now:
                del self.storage[user_id]