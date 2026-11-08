"""Authentication dependency compatibility module."""
from .deps import current_user, get_current_user

__all__ = ["get_current_user", "current_user"]

