# app/routes/__init__.py

from .services import bp as services_bp
from .auth import bp as auth_bp
from .user import bp as user_bp
from .playlist import bp as playlist_bp

__all__ = ['services_bp', 'auth_bp', 'user_bp', 'playlist_bp']
