from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from .config import settings
from .database import get_db
from .models import User
from .security import decode_access_token


def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    """Standardized authentication dependency across all AROHA protected routes.
    Extracts JWT from the 'aroha_session' HttpOnly cookie or Authorization Bearer header.
    """
    token = request.cookies.get(settings.cookie_name)
    if not token:
        auth = request.headers.get("authorization", "")
        if auth.lower().startswith("bearer "):
            token = auth[7:].strip()
    user_id = decode_access_token(token) if token else None
    user = db.get(User, user_id) if user_id else None
    if user is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Not authenticated")
    return user


# Backwards compatibility alias
current_user = get_current_user
