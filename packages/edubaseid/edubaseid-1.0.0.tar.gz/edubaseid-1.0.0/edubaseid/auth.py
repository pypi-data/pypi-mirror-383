# edubaseid/auth.py
"""
Module for Django/DRF authentication integration.
Provides authentication backend, views, and decorators.
"""

from functools import wraps
from typing import Any, Callable, Tuple

try:
    from django.conf import settings
    from django.http import HttpRequest, JsonResponse
    from django.shortcuts import redirect
    from django.utils import timezone
    from django.views.decorators.csrf import csrf_exempt
    from rest_framework.authentication import BaseAuthentication
    from rest_framework.exceptions import AuthenticationFailed
    from rest_framework.decorators import api_view, permission_classes
    from rest_framework.permissions import AllowAny, IsAuthenticated
    from rest_framework.response import Response
    HAS_DJANGO = True
except ImportError:
    HAS_DJANGO = False

from .client import EduBaseIDClient
from .config import get_config
from .exceptions import EduBaseIDError, InvalidStateError
from .user import sync_user
from .session import SessionManager
from .utils import generate_state_token

if HAS_DJANGO:
    class EduBaseIDAuthentication(BaseAuthentication):
        """
        DRF authentication backend for EduBaseID.

        Usage in settings:
        REST_FRAMEWORK = {
            'DEFAULT_AUTHENTICATION_CLASSES': ['edubaseid.auth.EduBaseIDAuthentication']
        }
        """

        def authenticate(self, request: HttpRequest) -> Tuple[Any, None]:
            auth_header = request.META.get('HTTP_AUTHORIZATION', '')
            if not auth_header.startswith('Bearer '):
                return None
            token = auth_header[7:]
            session_manager = SessionManager()
            token_data = session_manager.get_token_by_token(token)
            if not token_data or token_data['expires_at'] < timezone.now():
                raise AuthenticationFailed('Invalid or expired token')
            user = token_data['user']
            return (user, None)

    @api_view(['GET'])
    @permission_classes([AllowAny])
    def login_redirect(request: HttpRequest) -> JsonResponse:
        """
        Redirect to EduBaseID login.

        :param request: Django request
        :return: JSON with auth URL
        """
        client = EduBaseIDClient()
        state = generate_state_token()
        request.session['oauth_state'] = state
        auth_url = client.get_authorize_url(state=state)
        return JsonResponse({'success': True, 'auth_url': auth_url})

    @csrf_exempt
    @api_view(['POST'])
    @permission_classes([AllowAny])
    def auth_callback(request: HttpRequest) -> Response:
        """
        Handle OAuth callback.

        :param request: Django request with code and state
        :return: Response with user and token
        """
        code = request.data.get('code')
        state = request.data.get('state')
        saved_state = request.session.get('oauth_state')
        if state and state != saved_state:
            raise InvalidStateError("State mismatch")
        client = EduBaseIDClient()
        token_data = client.exchange_code_for_token(code)
        user_data = client.get_user_info(token_data['access_token'])
        user = sync_user(user_data)
        session_manager = SessionManager()
        local_token = session_manager.save_token(user.id, token_data)
        return Response({
            'success': True,
            'user': user_data,
            'token': local_token['token'],
            'token_expires': local_token['expires_at'].isoformat()
        })

    @api_view(['POST'])
    @permission_classes([IsAuthenticated])
    def logout_view(request: HttpRequest) -> Response:
        """
        Logout user.

        :param request: Django request
        :return: Success response
        """
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if auth_header.startswith('Bearer '):
            token = auth_header[7:]
            session_manager = SessionManager()
            session_manager.delete_token_by_token(token)
        client = EduBaseIDClient()
        client.logout(request.user.access_token)  # Assuming user has access_token
        return Response({'message': 'Logout successful'})

    def edubaseid_required(view_func: Callable) -> Callable:
        """
        Decorator to require EduBaseID authentication.

        :param view_func: View to decorate
        :return: Decorated view
        """
        @wraps(view_func)
        def wrapper(request: HttpRequest, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login_redirect')
            return view_func(request, *args, **kwargs)
        return wrapper

    def get_current_user(request: HttpRequest) -> Any:
        """
        Get current authenticated user.

        :param request: Django request
        :return: User object or None
        """
        if request.user.is_authenticated:
            return request.user
        return None
else:
    # Define stubs to avoid import errors
    class EduBaseIDAuthentication:
        def __init__(self):
            raise NotImplementedError("Django/DRF is required for EduBaseIDAuthentication")

    def login_redirect(*args, **kwargs):
        raise NotImplementedError("Django is required for login_redirect")

    def auth_callback(*args, **kwargs):
        raise NotImplementedError("Django is required for auth_callback")

    def logout_view(*args, **kwargs):
        raise NotImplementedError("Django is required for logout_view")

    def edubaseid_required(*args, **kwargs):
        raise NotImplementedError("Django is required for edubaseid_required")

    def get_current_user(*args, **kwargs):
        raise NotImplementedError("Django is required for get_current_user")

    import warnings
    warnings.warn("Django not found; auth features are disabled. Install 'django' and 'djangorestframework' for full functionality.", ImportWarning)