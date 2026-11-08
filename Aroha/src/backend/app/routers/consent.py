from datetime import datetime, timezone
from typing import Dict

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_user
from ..models import ConsentRecord, User
from ..schemas import ConsentIn, ConsentRecordOut

router = APIRouter(prefix="/users/consent", tags=["Consent"])


def has_consent(db: Session, user_id: int, consent_type: str) -> bool:
    """Latest record wins. No record means no consent."""
    row = db.scalar(
        select(ConsentRecord)
        .where(ConsentRecord.user_id == user_id, ConsentRecord.consent_type == consent_type)
        .order_by(ConsentRecord.id.desc())
    )
    return bool(row and row.consent_status == "granted")


@router.get("", response_model=Dict[str, ConsentRecordOut])
def get_consents(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    result: Dict[str, ConsentRecordOut] = {}
    for ctype in ("media_retention", "model_training"):
        latest = db.scalar(
            select(ConsentRecord)
            .where(ConsentRecord.user_id == user.id, ConsentRecord.consent_type == ctype)
            .order_by(ConsentRecord.id.desc())
        )
        if latest:
            result[ctype] = ConsentRecordOut(
                id=latest.id,
                consent_type=latest.consent_type,
                consent_status=latest.consent_status,
                recorded_at=latest.recorded_at,
                withdrawn_at=latest.withdrawn_at,
                granted=(latest.consent_status == "granted"),
            )
        else:
            result[ctype] = ConsentRecordOut(
                id=None,
                consent_type=ctype,
                consent_status="withdrawn",
                recorded_at=datetime.now(timezone.utc),
                withdrawn_at=None,
                granted=False,
            )
    return result


@router.put("", response_model=ConsentRecordOut)
def set_consent(data: ConsentIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    now = datetime.now(timezone.utc)
    if not data.granted:
        for r in db.scalars(
            select(ConsentRecord).where(
                ConsentRecord.user_id == user.id,
                ConsentRecord.consent_type == data.consent_type,
                ConsentRecord.consent_status == "granted",
            )
        ):
            r.withdrawn_at = now
            r.consent_status = "withdrawn"

    record = ConsentRecord(
        user_id=user.id,
        consent_type=data.consent_type,
        consent_status="granted" if data.granted else "withdrawn",
        recorded_at=now,
        withdrawn_at=None if data.granted else now,
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return ConsentRecordOut(
        id=record.id,
        consent_type=record.consent_type,
        consent_status=record.consent_status,
        recorded_at=record.recorded_at,
        withdrawn_at=record.withdrawn_at,
        granted=data.granted,
    )
