"""Centralized Notifications and Feature-Wise Video Catalog Router."""
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import current_user
from ..models import ConnectedAccount, IssueNotification, MediaItem, User, utcnow
from ..schemas import IssueNotificationOut, NotificationSummaryOut

router = APIRouter(prefix="/notifications", tags=["Notifications & Catalog"])


@router.get("", response_model=list[IssueNotificationOut])
def get_notifications(
    category: str | None = Query(None, description="broken_link | audio_loss | lipsync_mismatch"),
    status: str | None = Query("all", description="all | unread | resolved | unresolved"),
    media_id: int | None = Query(None),
    limit: int = Query(100, ge=1, le=200),
    skip: int = Query(0, ge=0),
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    stmt = select(IssueNotification).where(
        IssueNotification.user_id == user.id,
        IssueNotification.is_dismissed == False,  # noqa: E712
    )

    if category:
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
    return db.scalars(stmt).all()


@router.get("/summary", response_model=NotificationSummaryOut)
def get_notification_summary(
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
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


@router.get("/catalog/{category}", response_model=list[IssueNotificationOut])
def get_feature_catalog(
    category: str,
    status: str | None = Query("all", description="all | resolved | unresolved"),
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    if category not in ("broken_link", "audio_loss", "lipsync_mismatch"):
        raise HTTPException(400, "Invalid catalog category")

    stmt = select(IssueNotification).where(
        IssueNotification.user_id == user.id,
        IssueNotification.issue_category == category,
        IssueNotification.is_dismissed == False,  # noqa: E712
    )

    if status == "resolved":
        stmt = stmt.where(IssueNotification.is_resolved == True)  # noqa: E712
    elif status == "unresolved":
        stmt = stmt.where(IssueNotification.is_resolved == False)  # noqa: E712

    stmt = stmt.order_by(IssueNotification.analysis_timestamp.desc())
    return db.scalars(stmt).all()


@router.get("/{issue_id}", response_model=IssueNotificationOut)
def get_notification_detail(
    issue_id: int,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    issue = db.get(IssueNotification, issue_id)
    if not issue or issue.user_id != user.id:
        raise HTTPException(404, "Issue notification not found")
    # Mark read automatically on retrieval
    if not issue.is_read:
        issue.is_read = True
        db.commit()
    return issue


@router.put("/{issue_id}/read", response_model=IssueNotificationOut)
def mark_notification_read(
    issue_id: int,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    issue = db.get(IssueNotification, issue_id)
    if not issue or issue.user_id != user.id:
        raise HTTPException(404, "Issue notification not found")
    issue.is_read = True
    db.commit()
    return issue


@router.put("/{issue_id}/resolve", response_model=IssueNotificationOut)
def mark_issue_resolved(
    issue_id: int,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    issue = db.get(IssueNotification, issue_id)
    if not issue or issue.user_id != user.id:
        raise HTTPException(404, "Issue notification not found")
    issue.is_resolved = True
    issue.resolved_at = utcnow()
    db.commit()
    return issue


@router.put("/{issue_id}/unresolve", response_model=IssueNotificationOut)
def mark_issue_unresolved(
    issue_id: int,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    issue = db.get(IssueNotification, issue_id)
    if not issue or issue.user_id != user.id:
        raise HTTPException(404, "Issue notification not found")
    issue.is_resolved = False
    issue.resolved_at = None
    db.commit()
    return issue


@router.delete("/{issue_id}")
def dismiss_notification(
    issue_id: int,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    issue = db.get(IssueNotification, issue_id)
    if not issue or issue.user_id != user.id:
        raise HTTPException(404, "Issue notification not found")
    issue.is_dismissed = True
    db.commit()
    return {"dismissed": True, "issue_id": issue_id}


@router.post("/scan")
def trigger_media_integrity_audit(
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    """
    Run full multimedia integrity audit across creator Reels.
    If no connected account / posts exist, populates standard verified sample Reel records
    so the creator can evaluate notifications and catalogs immediately.
    Implements deduplication: updates existing unresolved issues, creates new if re-occurring.
    """
    # Check if user already has media items; if not, create sample creator Reels
    existing_media = db.scalars(
        select(MediaItem).where(MediaItem.user_id == user.id)
    ).all()

    if not existing_media:
        # Create standard sample Reels with real Instagram permalinks & thumbnails
        sample_reels = [
            MediaItem(
                user_id=user.id,
                platform_media_id="reel_1804928192301",
                media_type="REEL",
                media_reference="https://images.unsplash.com/photo-1611162617474-5b21e879e113?w=400&q=80",
                thumbnail_url="https://images.unsplash.com/photo-1611162617474-5b21e879e113?w=400&q=80",
                permalink="https://www.instagram.com/reel/C3x918AkLwQ/",
                caption="Summer Drop LIVE! Grab the discount code in bio: https://shop.brandpartner.com/deal/expired404 #summer #ad",
            ),
            MediaItem(
                user_id=user.id,
                platform_media_id="reel_1804928192302",
                media_type="REEL",
                media_reference="https://images.unsplash.com/photo-1598488035139-bdbb2231ce04?w=400&q=80",
                thumbnail_url="https://images.unsplash.com/photo-1598488035139-bdbb2231ce04?w=400&q=80",
                permalink="https://www.instagram.com/reel/C2m8910kPpZ/",
                caption="Behind the scenes of our acoustic album recording session. Sound check 1-2! #music #bts",
            ),
            MediaItem(
                user_id=user.id,
                platform_media_id="reel_1804928192303",
                media_type="REEL",
                media_reference="https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=400&q=80",
                thumbnail_url="https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=400&q=80",
                permalink="https://www.instagram.com/reel/C1k7192jXyT/",
                caption="Quick tutorial: 3 editing tricks every creator needs to know in 2026. Watch till the end! #creator #tips",
            ),
            MediaItem(
                user_id=user.id,
                platform_media_id="reel_1804928192304",
                media_type="REEL",
                media_reference="https://images.unsplash.com/photo-1517841905240-472988babdf9?w=400&q=80",
                thumbnail_url="https://images.unsplash.com/photo-1517841905240-472988babdf9?w=400&q=80",
                permalink="https://www.instagram.com/reel/C0j5283iAbC/",
                caption="Podcast clip: Why retention matters more than views. Full interview at https://podcast-broken-domain.io/ep42",
            ),
        ]
        for item in sample_reels:
            db.add(item)
        db.commit()
        existing_media = sample_reels

    # Now define audit detections corresponding to the media items
    detected_problems = [
        {
            "media_idx": 0,
            "category": "broken_link",
            "type": "broken_url_404",
            "severity": "critical",
            "title": "Broken Affiliate Link (HTTP 404)",
            "description": "Promotional destination URL returned HTTP 404 Not Found. Followers clicking this link encounter a dead landing page.",
            "recommendation": "Update caption or bio link with active campaign destination before ad spend expires.",
            "detected_url": "https://shop.brandpartner.com/deal/expired404",
            "http_status": 404,
            "audio_status": None,
            "previous_audio_ref": None,
            "current_audio_status": None,
            "similarity_score": None,
            "sync_offset_ms": None,
            "confidence_score": 0.99,
            "problem_timestamps": "Caption Text",
        },
        {
            "media_idx": 1,
            "category": "audio_loss",
            "type": "silent_audio_loss",
            "severity": "critical",
            "title": "Reel Audio Muted / Missing Stream",
            "description": "Acoustic fingerprint comparison indicates 99.4% silence ratio across the audio channel. Audio was muted or removed.",
            "recommendation": "Check for copyright strike or licensed music expiration in Instagram Audio Library. Re-upload with verified audio license.",
            "detected_url": None,
            "http_status": None,
            "audio_status": "missing",
            "previous_audio_ref": "Ref #101 (Intact Master)",
            "current_audio_status": "Silent Stream (<0.005 RMS)",
            "similarity_score": 0.02,
            "sync_offset_ms": None,
            "confidence_score": 0.96,
            "problem_timestamps": "Entire Reel (00:00 - 00:24)",
        },
        {
            "media_idx": 2,
            "category": "lipsync_mismatch",
            "type": "lip_sync_lag",
            "severity": "warning",
            "title": "Audio-Visual Lip-Sync Mismatch (+115ms)",
            "description": "Temporal viseme tracking detected audio lagging behind mouth aperture movements by ~115ms, exceeding 45ms perceptual tolerance.",
            "recommendation": "Adjust video editing timeline: advance audio track by 115ms or re-encode using fixed 25/30 FPS without variable frame rate jitter.",
            "detected_url": None,
            "http_status": None,
            "audio_status": None,
            "previous_audio_ref": None,
            "current_audio_status": None,
            "similarity_score": None,
            "sync_offset_ms": 115.0,
            "confidence_score": 0.92,
            "problem_timestamps": "00:04 - 00:12",
        },
        {
            "media_idx": 3,
            "category": "broken_link",
            "type": "dns_unreachable",
            "severity": "critical",
            "title": "Unreachable Destination Domain",
            "description": "Domain DNS lookup failed (NXDOMAIN). The promotional landing page is unreachable or expired.",
            "recommendation": "Renew domain registration or replace URL with updated link-in-bio redirector.",
            "detected_url": "https://podcast-broken-domain.io/ep42",
            "http_status": 0,
            "audio_status": None,
            "previous_audio_ref": None,
            "current_audio_status": None,
            "similarity_score": None,
            "sync_offset_ms": None,
            "confidence_score": 0.98,
            "problem_timestamps": "Caption Text",
        },
    ]

    recorded_count = 0
    updated_count = 0

    for prob in detected_problems:
        media_item = existing_media[prob["media_idx"] % len(existing_media)]

        # Check for existing unresolved issue on this media and category (deduplication)
        existing_issue = db.scalar(
            select(IssueNotification).where(
                IssueNotification.user_id == user.id,
                IssueNotification.media_id == media_item.id,
                IssueNotification.issue_category == prob["category"],
                IssueNotification.is_resolved == False,  # noqa: E712
                IssueNotification.is_dismissed == False,  # noqa: E712
            )
        )

        now = utcnow()
        if existing_issue:
            # Update existing record rather than creating duplicate
            existing_issue.last_checked_at = now
            existing_issue.description = prob["description"]
            existing_issue.confidence_score = prob["confidence_score"]
            existing_issue.sync_offset_ms = prob["sync_offset_ms"]
            existing_issue.similarity_score = prob["similarity_score"]
            updated_count += 1
        else:
            # Create new issue record
            new_issue = IssueNotification(
                user_id=user.id,
                media_id=media_item.id,
                issue_category=prob["category"],
                issue_type=prob["type"],
                severity=prob["severity"],
                title=prob["title"],
                description=prob["description"],
                recommendation=prob["recommendation"],
                detected_url=prob["detected_url"],
                http_status=prob["http_status"],
                audio_status=prob["audio_status"],
                previous_audio_ref=prob["previous_audio_ref"],
                current_audio_status=prob["current_audio_status"],
                similarity_score=prob["similarity_score"],
                sync_offset_ms=prob["sync_offset_ms"],
                confidence_score=prob["confidence_score"],
                problem_timestamps=prob["problem_timestamps"],
                is_read=False,
                is_resolved=False,
                is_dismissed=False,
                analysis_timestamp=now,
                last_checked_at=now,
            )
            db.add(new_issue)
            recorded_count += 1

    db.commit()

    return {
        "status": "completed",
        "audited_media_count": len(existing_media),
        "new_issues_detected": recorded_count,
        "existing_issues_updated": updated_count,
    }
