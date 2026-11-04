from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from ..config import settings
from ..database import get_db
from ..deps import current_user
from ..models import ConnectedAccount, ConsentRecord, User
from ..schemas import ProfileUpdate, UserOut
from sqlalchemy import select

router = APIRouter(prefix="/users", tags=["User settings"])


@router.get("/profile", response_model=UserOut)
def get_profile(user: User = Depends(current_user)):
    return user


@router.put("/profile", response_model=UserOut)
def update_profile(data: ProfileUpdate, user: User = Depends(current_user), db: Session = Depends(get_db)):
    user.name = data.name.strip()
    db.commit()
    return user


@router.get("/settings")
def get_settings(user: User = Depends(current_user), db: Session = Depends(get_db)):
    accounts = db.scalars(select(ConnectedAccount).where(ConnectedAccount.user_id == user.id)).all()
    consents = db.scalars(select(ConsentRecord).where(ConsentRecord.user_id == user.id)).all()
    return {
        "connected_accounts": [{"platform": a.platform, "username": a.username, "status": a.connection_status}
                               for a in accounts],
        "consents": [{"type": c.consent_type, "status": c.consent_status} for c in consents],
    }


@router.delete("/account", status_code=status.HTTP_204_NO_CONTENT)
def delete_account(response: Response, user: User = Depends(current_user), db: Session = Depends(get_db)):
    db.delete(user)
    db.commit()
    response.delete_cookie(settings.cookie_name)
