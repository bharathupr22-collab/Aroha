from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..config import settings
from ..database import get_db
from ..deps import current_user, get_current_user
from ..models import User
from ..schemas import ForgotPasswordIn, LoginIn, RegisterIn, UserOut
from ..security import create_access_token, hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["Authentication"])

_DUMMY_HASH = hash_password("dummy-password-1")


def _set_cookie(response: Response, user_id: int) -> str:
    token = create_access_token(user_id)
    response.set_cookie(
        settings.cookie_name, token, httponly=True, secure=settings.cookie_secure,
        samesite="lax", max_age=settings.access_token_minutes * 60,
    )
    return token


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(data: RegisterIn, response: Response, db: Session = Depends(get_db)):
    email = data.email.lower()
    if db.scalar(select(User).where(User.email == email)):
        raise HTTPException(status.HTTP_409_CONFLICT, "Email already registered")
    user = User(name=data.name.strip(), email=email, password_hash=hash_password(data.password))
    db.add(user)
    db.commit()
    _set_cookie(response, user.id)
    return user


@router.post("/login")
def login(data: LoginIn, response: Response, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == data.email.lower()))
    ok = verify_password(data.password, user.password_hash if user else _DUMMY_HASH)
    if not user or not ok:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid email or password")
    token = _set_cookie(response, user.id)
    return {"user": UserOut.model_validate(user), "access_token": token, "token_type": "bearer"}


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(response: Response):
    response.delete_cookie(settings.cookie_name)


@router.post("/forgot-password")
def forgot_password(data: ForgotPasswordIn):
    # Always the same reply so account existence is never revealed. E-mail delivery is added later.
    return {"detail": "If that e-mail is registered, a reset link has been sent."}


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return user
