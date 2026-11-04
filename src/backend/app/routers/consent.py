from datetime import datetime, timezone
from typing import Literal

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import current_user
from ..models import ConsentRecord, User

router = APIRouter(prefix="/users/consent", tags=["Consent"])
ConsentType = Literal["media_retention", "model_training"]


class ConsentIn(BaseModel):
    consent_type: ConsentType
    granted: bool


def has_consent(db: Session, user_id: int, consent_type: str) -> bool:
    """Latest record wins. No record means no consent."""
    row = db.scalar(select(ConsentRecord).where(
        ConsentRecord.user_id == user_id, ConsentRecord.consent_type == consent_type
    ).order_by(ConsentRecord.id.desc()))
    return bool(row and row.consent_status == "granted")


@router.get("")
def get_consents(user: User = Depends(current_user), db: Session = Depends(get_db)):
    return {t: has_consent(db, user.id, t) for t in ("media_retention", "model_training")}


@router.put("")
def set_consent(data: ConsentIn, user: User = Depends(current_user), db: Session = Depends(get_db)):
    now = datetime.now(timezone.utc)
    if not data.granted:
        for r in db.scalars(select(ConsentRecord).where(
                ConsentRecord.user_id == user.id, ConsentRecord.consent_type == data.consent_type,
                ConsentRecord.consent_status == "granted")):
            r.withdrawn_at = now
    db.add(ConsentRecord(user_id=user.id, consent_type=data.consent_type,
                         consent_status="granted" if data.granted else "withdrawn", recorded_at=now,
                         withdrawn_at=None if data.granted else now))
    db.commit()
    return {data.consent_type: data.granted}
