# edubaseid/__init__.py
from .client import EduBaseIDClient
from .user import sync_user, get_local_user, update_local_user, delete_user, get_roles, has_permission
from .utils import generate_state_token, generate_pkce_pair, parse_jwt, now_utc, validate_redirect_uri, build_auth_header, get_oauth_headers, safe_request
from .exceptions import EduBaseIDError, InvalidClientError, TokenExpiredError, UnauthorizedError, NetworkError, InvalidRedirectURI, PermissionDeniedError, InvalidStateError
from .session import SessionManager
from .webhooks import handle_event, register_event_handler, verify_signature
from .logging import enable_debug, log_event, metrics
from .config import get_config
from .cli import cli
from .health import check_server_status, ping
from .admin import get_all_users, revoke_token
from .analytics import get_login_stats, get_active_users

# Lazy import for auth to avoid errors if Django is missing
try:
    from .auth import EduBaseIDAuthentication, login_redirect, auth_callback, logout_view, edubaseid_required, get_current_user
except ImportError:
    pass  # Auth features skipped

__version__ = '1.0.0'