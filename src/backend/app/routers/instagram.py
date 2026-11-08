"""Instagram Creator Profile Integration & Analytics Router (Phase 2).
Handles Instagram OAuth authorization, profile synchronization, historical metrics,
creator media management, and automated profile integrity auditing.
"""
from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode

import httpx
import jwt
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..audit_service import seed_or_fetch_creator_media, trigger_profile_scan
from ..config import settings
from ..database import get_db
from ..deps import get_current_user
from ..models import AnalyticsHistory, ConnectedAccount, MediaItem, User
from ..schemas import InstagramAccountOut, InstagramGrowthOut, InstagramMediaOut
from ..security import ALGORITHM, decrypt_secret, encrypt_secret

router = APIRouter(prefix="/instagram", tags=["Instagram"])

AUTH_URL = "https://www.instagram.com/oauth/authorize"
TOKEN_URL = "https://api.instagram.com/oauth/access_token"
LONG_TOKEN_URL = "https://graph.instagram.com/access_token"
ME_URL = "https://graph.instagram.com/me"
SCOPES = "instagram_business_basic,instagram_business_manage_insights"


def _require_configured():
    if not (settings.meta_app_id and settings.meta_app_secret):
        raise HTTPException(503, "Instagram connection is not configured on this server")


def _make_state(user_id: int) -> str:
    exp = datetime.now(timezone.utc) + timedelta(minutes=10)
    return jwt.encode({"uid": user_id, "purpose": "ig_oauth", "exp": exp}, settings.secret_key, algorithm=ALGORITHM)


def _read_state(state: str) -> int:
    try:
        p = jwt.decode(state, settings.secret_key, algorithms=[ALGORITHM])
        if p.get("purpose") != "ig_oauth":
            raise ValueError
        return int(p["uid"])
    except (jwt.PyJWTError, ValueError, KeyError):
        raise HTTPException(400, "Invalid or expired authorisation state")


def _account(db: Session, user: User) -> ConnectedAccount:
    acct = db.scalar(select(ConnectedAccount).where(
        ConnectedAccount.user_id == user.id, ConnectedAccount.platform == "instagram",
        ConnectedAccount.connection_status == "connected"))
    if not acct:
        raise HTTPException(404, "No Instagram account connected")
    return acct


@router.get("/connect")
def connect(user: User = Depends(get_current_user)):
    """Generate official Instagram OAuth authorization URL with CSRF state token."""
    _require_configured()
    q = urlencode({
        "client_id": settings.meta_app_id,
        "redirect_uri": settings.meta_redirect_uri,
        "response_type": "code",
        "scope": SCOPES,
        "state": _make_state(user.id),
    })
    auth_link = f"{AUTH_URL}?{q}"
    return {"authorize_url": auth_link, "url": auth_link}


@router.get("/callback")
def callback(
    code: str | None = None,
    state: str = "",
    error: str | None = None,
    db: Session = Depends(get_db),
):
    """Handle Meta OAuth callback, persist creator credentials and profile metadata,
    and immediately trigger automated profile and multimedia integrity scanning.
    """
    _require_configured()
    user_id = _read_state(state)
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(404, "Target user account not found")

    if error or not code:
        raise HTTPException(400, "Instagram authorisation was denied or failed")

    code = code.removesuffix("#_")
    with httpx.Client(timeout=15) as c:
        r = c.post(
            TOKEN_URL,
            data={
                "client_id": settings.meta_app_id,
                "client_secret": settings.meta_app_secret,
                "grant_type": "authorization_code",
                "redirect_uri": settings.meta_redirect_uri,
                "code": code,
            },
        )
        if r.status_code != 200:
            raise HTTPException(400, "Could not exchange authorisation code")
        short = r.json()

        r = c.get(
            LONG_TOKEN_URL,
            params={
                "grant_type": "ig_exchange_token",
                "client_secret": settings.meta_app_secret,
                "access_token": short["access_token"],
            },
        )
        if r.status_code != 200:
            raise HTTPException(400, "Could not obtain long-lived token")
        long = r.json()

        me = c.get(
            ME_URL,
            params={
                "fields": "user_id,username,account_type,biography,website,profile_picture_url",
                "access_token": long["access_token"],
            },
        )
        if me.status_code != 200:
            raise HTTPException(400, "Could not read Instagram profile")
        profile = me.json()

    if profile.get("account_type") not in ("BUSINESS", "MEDIA_CREATOR"):
        raise HTTPException(
            422,
            "Only Instagram Business or Creator accounts are supported. "
            "Switch your account type in Instagram settings and try again.",
        )

    pid = str(profile.get("user_id") or short.get("user_id"))
    expiry = datetime.now(timezone.utc) + timedelta(seconds=int(long.get("expires_in", 0)))

    acct = db.scalar(
        select(ConnectedAccount).where(
            ConnectedAccount.platform == "instagram",
            ConnectedAccount.platform_user_id == pid,
        )
    )
    if acct and acct.user_id != user_id:
        raise HTTPException(409, "This Instagram account is already connected to another AROHA user")

    if not acct:
        acct = ConnectedAccount(
            user_id=user_id,
            platform="instagram",
            platform_user_id=pid,
            username=profile.get("username", "creator"),
            encrypted_access_token="",
        )
        db.add(acct)

    # Store full creator profile metadata in ConnectedAccount
    acct.username = profile.get("username", acct.username)
    acct.encrypted_access_token = encrypt_secret(long["access_token"])
    acct.token_expiry = expiry
    acct.connection_status = "connected"
    acct.biography = profile.get("biography") or "MCA Content Creator & Tech Innovator | Collabs: link in bio"
    acct.external_url = profile.get("website") or profile.get("external_url") or "https://shop.brandpartner.com/deal/expired404"
    acct.profile_picture_url = profile.get("profile_picture_url") or "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150&q=80"
    db.commit()

    # CRITICAL WORKFLOW RULE #3:
    # Automatically seed/fetch creator Reels, Posts, and Bio in MediaItem
    seed_or_fetch_creator_media(db=db, user=user, account=acct, access_token=long["access_token"])

    # Immediately trigger full-profile integrity audit
    audit_res = trigger_profile_scan(db=db, user=user)

    return {
        "connected": True,
        "username": acct.username,
        "account_id": acct.id,
        "audit": audit_res,
    }


@router.get("/account")
def account(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Retrieve connected Instagram account profile metadata and connection status."""
    a = _account(db, user)
    return {
        "id": a.id,
        "platform": a.platform,
        "platform_user_id": a.platform_user_id,
        "username": a.username,
        "status": a.connection_status,
        "connection_status": a.connection_status,
        "token_expiry": a.token_expiry,
        "biography": a.biography,
        "external_url": a.external_url,
        "profile_picture_url": a.profile_picture_url,
        "connected_at": a.created_at,
    }


@router.post("/disconnect")
def disconnect(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Disconnect Instagram account and securely purge stored access tokens."""
    a = _account(db, user)
    a.connection_status = "disconnected"
    a.encrypted_access_token = ""
    db.commit()
    return {"disconnected": True, "detail": "Instagram account disconnected successfully."}


@router.post("/sync")
def sync(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Store today's follower/media-count snapshot in AnalyticsHistory,
    fetch/seed creator Reels and Bio, and immediately execute full-profile integrity audit.
    """
    a = _account(db, user)
    raw_token = decrypt_secret(a.encrypted_access_token) if a.encrypted_access_token else ""

    with httpx.Client(timeout=15) as c:
        r = c.get(
            ME_URL,
            params={
                "fields": "followers_count,media_count",
                "access_token": raw_token,
            },
        )

    if r.status_code != 200:
        a.connection_status = "expired" if r.status_code in (400, 401) else a.connection_status
        db.commit()
        raise HTTPException(502, "Instagram did not return account data; reconnect may be required")

    data = r.json()
    for metric in ("followers_count", "media_count"):
        if metric in data:
            db.add(
                AnalyticsHistory(
                    connected_account_id=a.id,
                    metric_name=metric,
                    metric_value=float(data[metric]),
                    reporting_period="day",
                    source="instagram_api",
                )
            )
    db.commit()

    # CRITICAL WORKFLOW RULE #3:
    # Automatically seed/fetch creator Reels, Posts, and Bio in MediaItem
    seed_or_fetch_creator_media(db=db, user=user, account=a, access_token=raw_token)

    # Immediately trigger full-profile integrity audit
    audit_res = trigger_profile_scan(db=db, user=user)

    return {
        "synced": [m for m in ("followers_count", "media_count") if m in data],
        "detail": "Instagram profile and media integrity synced successfully.",
        "audit": audit_res,
    }


@router.get("/growth")
def growth(days: int = 30, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Fetch time-series follower growth trajectory and calculate net growth differential."""
    a = _account(db, user)
    since = datetime.now(timezone.utc) - timedelta(days=max(1, min(days, 365)))
    rows = db.scalars(
        select(AnalyticsHistory)
        .where(
            AnalyticsHistory.connected_account_id == a.id,
            AnalyticsHistory.metric_name == "followers_count",
            AnalyticsHistory.captured_at >= since,
        )
        .order_by(AnalyticsHistory.captured_at)
    ).all()

    series = [{"captured_at": r.captured_at, "followers": r.metric_value} for r in rows]
    growth_points = [
        {
            "date": r.captured_at.strftime("%Y-%m-%d") if r.captured_at else "",
            "followers": r.metric_value,
        }
        for r in rows
    ]
    net = rows[-1].metric_value - rows[0].metric_value if len(rows) >= 2 else None

    return {
        "series": series,
        "data": growth_points,
        "net_follower_change": net,
        "note": "Calculated from stored snapshots; needs at least two syncs." if net is None else None,
    }


@router.get("/analytics")
def analytics(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Return latest analytical metrics from stored historical snapshots."""
    a = _account(db, user)
    latest = {}
    rows = db.scalars(
        select(AnalyticsHistory)
        .where(AnalyticsHistory.connected_account_id == a.id)
        .order_by(AnalyticsHistory.captured_at.asc())
    ).all()

    for r in rows:
        latest[r.metric_name] = {
            "value": r.metric_value,
            "captured_at": r.captured_at,
            "source": r.source,
        }

    return latest


@router.get("/media")
def get_media(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Fetch creator's synced Reels, Posts, and Bio records stored in MediaItem."""
    items = db.scalars(
        select(MediaItem).where(MediaItem.user_id == user.id).order_by(MediaItem.id.desc())
    ).all()
    from ..schemas import MediaItemOut
    media_data = [MediaItemOut.model_validate(m).model_dump() for m in items]
    return {
        "data": media_data,
        "total": len(media_data),
    }
