# edubaseid/user.py
"""
Module for user management and synchronization.
Handles local user model and operations, with Django as optional dependency.
"""

from typing import Dict, List, Any, Optional
from datetime import timedelta

try:
    from django.db import models
    from django.utils import timezone
    HAS_DJANGO = True
except ImportError:
    HAS_DJANGO = False

if HAS_DJANGO:
    class EduBaseIDUser(models.Model):
        """
        Local user model synced with EduBaseID.
        """
        ROLE_CHOICES = [
            ('student', 'Student'),
            ('teacher', 'Teacher'),
            ('admin', 'Administrator'),
            ('staff', 'Staff'),
        ]
        
        edubase_id = models.CharField(max_length=255, unique=True, db_index=True)
        email = models.EmailField(db_index=True)
        name = models.CharField(max_length=300)
        login = models.CharField(max_length=150, db_index=True)
        phone = models.CharField(max_length=20, blank=True)
        role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
        
        # OAuth details
        access_token = models.TextField(blank=True)
        refresh_token = models.TextField(blank=True)
        token_expires = models.DateTimeField(null=True, blank=True)
        
        created_at = models.DateTimeField(auto_now_add=True)
        updated_at = models.DateTimeField(auto_now=True)
        last_login = models.DateTimeField(null=True, blank=True)
        
        def is_token_expired(self) -> bool:
            if not self.token_expires:
                return True
            return timezone.now() > self.token_expires
        
        def update_tokens(self, access_token: str, refresh_token: str, expires_in: int = 3600) -> None:
            self.access_token = access_token
            self.refresh_token = refresh_token
            self.token_expires = timezone.now() + timedelta(seconds=expires_in)
            self.save()
        
        def update_last_login(self) -> None:
            self.last_login = timezone.now()
            self.save()
        
        def __str__(self) -> str:
            return f"{self.name} ({self.role})"

def sync_user(user_data: Dict) -> Optional[Any]:
    """
    Sync or create local user from EduBaseID data.

    :param user_data: User info from server
    :return: Local user instance or None if Django not available
    """
    if not HAS_DJANGO:
        raise ImportError("Django required for user sync")
    user, created = EduBaseIDUser.objects.update_or_create(
        edubase_id=user_data['sub'],
        defaults={
            'email': user_data['email'],
            'name': user_data['name'],
            'login': user_data['login'],
            'phone': user_data.get('phone', ''),
            'last_login': timezone.now(),
        }
    )
    return user

def get_local_user(edubase_id: str) -> Optional[Any]:
    """
    Get local user by EduBaseID.

    :param edubase_id: EduBase ID
    :return: User or None
    """
    if not HAS_DJANGO:
        raise ImportError("Django required for user management")
    return EduBaseIDUser.objects.filter(edubase_id=edubase_id).first()

def update_local_user(user_data: Dict) -> Optional[Any]:
    """
    Update local user.

    :param user_data: Updated data
    :return: Updated user or None
    """
    if not HAS_DJANGO:
        raise ImportError("Django required for user management")
    user = get_local_user(user_data['sub'])
    if user:
        for key, value in user_data.items():
            if hasattr(user, key):
                setattr(user, key, value)
        user.save()
    return user

def delete_user(edubase_id: str) -> None:
    """
    Delete local user.

    :param edubase_id: EduBase ID
    """
    if not HAS_DJANGO:
        raise ImportError("Django required for user management")
    user = get_local_user(edubase_id)
    if user:
        user.delete()

def get_roles(user: Any) -> List[str]:
    """
    Get user roles.

    :param user: User instance
    :return: List of roles
    """
    if not HAS_DJANGO:
        raise ImportError("Django required for user management")
    return [user.role] if user else []

def has_permission(user: Any, permission: str) -> bool:
    """
    Check if user has permission.

    :param user: User instance
    :param permission: Permission string
    :return: Bool
    """
    if not HAS_DJANGO:
        raise ImportError("Django required for user management")
    if user.role == 'admin':
        return True
    # Add more permission logic as needed
    return False

if not HAS_DJANGO:
    import warnings
    warnings.warn(
        "Django not found; user management features are disabled. "
        "Install 'django' for full functionality.",
        ImportWarning
    )