"""Centralized Dashboard Notifications and Feature-Wise Video Catalog Router (Phase 3).
Provides multi-category issue monitoring, aggregated KPI summaries, feature catalogs,
and media-linked diagnostic reports with joined media metadata (thumbnails, permalinks, viseme metrics).
"""
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from ..audit_service import trigger_profile_scan
from ..database import get_db
from ..deps import get_current_user
from ..models import IssueNotification, User, utcnow
from ..schemas import IssueNotificationOut, NotificationSummaryOut

router = APIRouter(prefix="/notifications", tags=["Notifications & Catalog"])


@router.get("", response_model=List[IssueNotificationOut])
def get_notifications(
    category: Optional[str] = Query(None, description="broken_link | audio_loss | lipsync_mismatch"),
    status: Optional[str] = Query("all", description="all | unread | resolved | unresolved"),
    media_id: Optional[int] = Query(None, description="Filter by exact MediaItem ID"),
    limit: int = Query(100, ge=1, le=200),
    skip: int = Query(0, ge=0),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieve creator notifications with joined media metadata (thumbnails, captions, permalinks)."""
    # Normalize if invoked directly in test suites without FastAPI DI resolution
    if hasattr(category, "default"):
        category = category.default
    if hasattr(status, "default"):
        status = status.default
    if hasattr(media_id, "default"):
        media_id = media_id.default
    if hasattr(limit, "default"):
        limit = limit.default
    if hasattr(skip, "default"):
        skip = skip.default

    stmt = (
        select(IssueNotification)
        .options(joinedload(IssueNotification.media))
        .where(
            IssueNotification.user_id == user.id,
            IssueNotification.is_dismissed == False,  # noqa: E712
        )
    )

    if category:
        if category not in ("broken_link", "audio_loss", "lipsync_mismatch"):
            raise HTTPException(400, f"Invalid category: {category}. Choose from broken_link, audio_loss, lipsync_mismatch")
        stmt = stmt.where(IssueNotification.issue_category == category)

    if media_id is not None:
        stmt = stmt.where(IssueNotification.media_id == media_id)

    if status == "unread":
        stmt = stmt.where(IssueNotification.is_read == False)  # noqa: E712
    elif status == "resolved":
        stmt = stmt.where(IssueNotification.is_resolved == True)  # noqa: E712
    elif status == "unresolved":
        stmt = stmt.where(IssueNotification.is_resolved == False)  # noqa: E712

    stmt = stmt.order_by(IssueNotification.analysis_timestamp.desc()).offset(skip).limit(limit)
    return db.scalars(stmt).unique().all()


@router.get("/summary", response_model=NotificationSummaryOut)
def get_notification_summary(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return 7 aggregated KPI metrics for main dashboard monitoring cards."""
    base_where = [
        IssueNotification.user_id == user.id,
        IssueNotification.is_dismissed == False,  # noqa: E712
    ]

    total = db.scalar(select(func.count(IssueNotification.id)).where(*base_where)) or 0
    broken = db.scalar(
        select(func.count(IssueNotification.id)).where(
            *base_where, IssueNotification.issue_category == "broken_link"
        )
    ) or 0
    audio_iss = db.scalar(
        select(func.count(IssueNotification.id)).where(
            *base_where, IssueNotification.issue_category == "audio_loss"
        )
    ) or 0
    lipsync = db.scalar(
        select(func.count(IssueNotification.id)).where(
            *base_where, IssueNotification.issue_category == "lipsync_mismatch"
        )
    ) or 0
    unresolved = db.scalar(
        select(func.count(IssueNotification.id)).where(
            *base_where, IssueNotification.is_resolved == False  # noqa: E712
        )
    ) or 0
    resolved = db.scalar(
        select(func.count(IssueNotification.id)).where(
            *base_where, IssueNotification.is_resolved == True  # noqa: E712
        )
    ) or 0
    unread = db.scalar(
        select(func.count(IssueNotification.id)).where(
            *base_where, IssueNotification.is_read == False  # noqa: E712
        )
    ) or 0

    return NotificationSummaryOut(
        total_issues=total,
        broken_link_issues=broken,
        audio_issues=audio_iss,
        lipsync_issues=lipsync,
        unresolved_issues=unresolved,
        resolved_issues=resolved,
        unread_count=unread,
    )


@router.get("/catalog/{category}", response_model=List[IssueNotificationOut])
def get_feature_catalog(
    category: str,
    status: Optional[str] = Query("all", description="all | resolved | unresolved"),
    limit: int = Query(100, ge=1, le=200),
    skip: int = Query(0, ge=0),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return read-only feature catalog entries for a specific integrity category with joined media metadata."""
    if hasattr(status, "default"):
        status = status.default
    if hasattr(limit, "default"):
        limit = limit.default
    if hasattr(skip, "default"):
        skip = skip.default

    if category not in ("broken_link", "audio_loss", "lipsync_mismatch"):
        raise HTTPException(
            status_code=400,
            detail="Invalid catalog category. Choose from: broken_link, audio_loss, lipsync_mismatch",
        )

    stmt = (
        select(IssueNotification)
        .options(joinedload(IssueNotification.media))
        .where(
            IssueNotification.user_id == user.id,
            IssueNotification.issue_category == category,
            IssueNotification.is_dismissed == False,  # noqa: E712
        )
    )

    if status == "resolved":
        stmt = stmt.where(IssueNotification.is_resolved == True)  # noqa: E712
    elif status == "unresolved":
        stmt = stmt.where(IssueNotification.is_resolved == False)  # noqa: E712

    stmt = stmt.order_by(IssueNotification.analysis_timestamp.desc()).offset(skip).limit(limit)
    return db.scalars(stmt).unique().all()


@router.get("/{issue_id}", response_model=IssueNotificationOut)
def get_notification_detail(
    issue_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieve full issue diagnostic report with joined media and automatically mark as read."""
    issue = db.scalar(
        select(IssueNotification)
        .options(joinedload(IssueNotification.media))
        .where(
            IssueNotification.id == issue_id,
            IssueNotification.user_id == user.id,
        )
    )
    if not issue:
        raise HTTPException(status_code=404, detail="Issue notification not found")

    if not issue.is_read:
        issue.is_read = True
        db.commit()

    return issue


@router.put("/{issue_id}/read", response_model=IssueNotificationOut)
def mark_notification_read(
    issue_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Explicitly mark a notification as read."""
    issue = db.scalar(
        select(IssueNotification)
        .options(joinedload(IssueNotification.media))
        .where(
            IssueNotification.id == issue_id,
            IssueNotification.user_id == user.id,
        )
    )
    if not issue:
        raise HTTPException(status_code=404, detail="Issue notification not found")

    issue.is_read = True
    db.commit()
    return issue


@router.put("/{issue_id}/resolve", response_model=IssueNotificationOut)
def mark_issue_resolved(
    issue_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Mark an issue notification as resolved by the creator."""
    issue = db.scalar(
        select(IssueNotification)
        .options(joinedload(IssueNotification.media))
        .where(
            IssueNotification.id == issue_id,
            IssueNotification.user_id == user.id,
        )
    )
    if not issue:
        raise HTTPException(status_code=404, detail="Issue notification not found")

    issue.is_resolved = True
    issue.resolved_at = utcnow()
    db.commit()
    return issue


@router.put("/{issue_id}/unresolve", response_model=IssueNotificationOut)
def mark_issue_unresolved(
    issue_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Reopen a previously resolved issue notification."""
    issue = db.scalar(
        select(IssueNotification)
        .options(joinedload(IssueNotification.media))
        .where(
            IssueNotification.id == issue_id,
            IssueNotification.user_id == user.id,
        )
    )
    if not issue:
        raise HTTPException(status_code=404, detail="Issue notification not found")

    issue.is_resolved = False
    issue.resolved_at = None
    db.commit()
    return issue


@router.delete("/{issue_id}")
def dismiss_notification(
    issue_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Dismiss a notification from creator dashboard."""
    issue = db.scalar(
        select(IssueNotification).where(
            IssueNotification.id == issue_id,
            IssueNotification.user_id == user.id,
        )
    )
    if not issue:
        raise HTTPException(status_code=404, detail="Issue notification not found")

    issue.is_dismissed = True
    db.commit()
    return {"dismissed": True, "issue_id": issue_id}


@router.post("/scan")
def trigger_media_integrity_audit(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Iterate through all MediaItem records (Reels, Posts, Bio) of the connected Instagram profile.
    Automatically evaluates:
      - Promotional links (broken_link)
      - Muted or copyright-stripped audio tracks (audio_loss)
      - Audio-visual speech-to-lip desynchronization (lipsync_mismatch)
    Creates or updates IssueNotification records linked via media_id with deduplication.
    """
    return trigger_profile_scan(db=db, user=user)
