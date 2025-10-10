# edubaseid/config.py
"""
Configuration module.
Loads config from Django settings or environment.
"""

import os
from typing import Dict

try:
    from django.conf import settings as django_settings
    HAS_DJANGO = True
except ImportError:
    HAS_DJANGO = False

def get_config() -> Dict:
    """
    Get EduBaseID configuration.

    :return: Config dict
    """
    if HAS_DJANGO:
        return getattr(django_settings, 'EDUBASEID_CONFIG', {})
    else:
        return {
            'SERVER_URL': os.getenv('EDUBASEID_SERVER_URL', 'https://id.edubase.uz'),
            'CLIENT_ID': os.getenv('EDUBASEID_CLIENT_ID'),
            'CLIENT_SECRET': os.getenv('EDUBASEID_CLIENT_SECRET'),
            'REDIRECT_URI': os.getenv('EDUBASEID_REDIRECT_URI'),
            'SCOPES': os.getenv('EDUBASEID_SCOPES', 'openid profile email').split(),
            'AUTO_SYNC_USER': bool(os.getenv('EDUBASEID_AUTO_SYNC_USER', True)),
            'AUTO_REFRESH_TOKEN': bool(os.getenv('EDUBASEID_AUTO_REFRESH_TOKEN', True)),
            'TIMEOUT': int(os.getenv('EDUBASEID_TIMEOUT', 10)),
        }