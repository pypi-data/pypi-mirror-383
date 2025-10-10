# edubaseid/analytics.py
"""
Analytics utilities.
"""

from typing import Dict

from .client import EduBaseIDClient
from .utils import safe_request

def get_login_stats(access_token: str) -> Dict:
    """
    Get login statistics (stub).

    :param access_token: Token
    :return: Stats
    """
    client = EduBaseIDClient()
    headers = {'Authorization': f'Bearer {access_token}'}
    response = safe_request('GET', f"{client.server_url}/analytics/logins/", headers=headers)
    return response.json()

def get_active_users(access_token: str) -> int:
    """
    Get active users count.

    :param access_token: Token
    :return: Count
    """
    stats = get_login_stats(access_token)
    return stats.get('active_users', 0)