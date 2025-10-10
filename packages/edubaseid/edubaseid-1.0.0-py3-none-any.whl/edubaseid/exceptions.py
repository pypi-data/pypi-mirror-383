# edubaseid/exceptions.py
"""
Custom exceptions for EduBaseID SDK.
"""

class EduBaseIDError(Exception):
    """Base exception for EduBaseID errors."""

class InvalidClientError(EduBaseIDError):
    """Invalid client configuration."""

class TokenExpiredError(EduBaseIDError):
    """Token has expired."""

class UnauthorizedError(EduBaseIDError):
    """Unauthorized access."""

class NetworkError(EduBaseIDError):
    """Network-related error."""

class InvalidRedirectURI(EduBaseIDError):
    """Invalid redirect URI."""

class PermissionDeniedError(EduBaseIDError):
    """Permission denied."""

class InvalidStateError(EduBaseIDError):
    """Invalid state parameter."""