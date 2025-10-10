# edubaseid/health.py
"""
Health check utilities.
"""

from .client import EduBaseIDClient
from .utils import safe_request

def check_server_status() -> bool:
    """
    Check if server is up.

    :return: Status
    """
    client = EduBaseIDClient()
    try:
        safe_request('GET', f"{client.server_url}/oauth/validate-client/")
        return True
    except Exception:
        return False

def ping() -> str:
    """Ping server."""
    return "Pong" if check_server_status() else "Server down"