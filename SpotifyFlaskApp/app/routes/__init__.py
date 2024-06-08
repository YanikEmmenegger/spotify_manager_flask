# app/routes/__init__.py

from .api import bp as api_bp
from .auth import bp as auth_bp

__all__ = ['api_bp', 'auth_bp']
