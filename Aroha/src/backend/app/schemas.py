import re
from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


# ==========================================
# AUTHENTICATION & USER SCHEMAS
# ==========================================
class RegisterIn(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

    @field_validator("password")
    @classmethod
    def strong_password(cls, v: str) -> str:
        if not (re.search(r"[A-Za-z]", v) and re.search(r"\d", v)):
            raise ValueError("Password must contain letters and digits")
        return v


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class ForgotPasswordIn(BaseModel):
    email: EmailStr


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    email: EmailStr
    created_at: datetime


class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserOut


class ProfileUpdate(BaseModel):
    name: str = Field(min_length=1, max_length=120)


# ==========================================
# USER CONSENT SCHEMAS
# ==========================================
ConsentType = Literal["media_retention", "model_training"]


class ConsentIn(BaseModel):
    consent_type: ConsentType
    granted: bool


class ConsentRecordOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: Optional[int] = None
    consent_type: str
    consent_status: str
    recorded_at: datetime
    withdrawn_at: Optional[datetime] = None
    granted: bool = False


# ==========================================
# LINK ANALYZER SCHEMAS
# ==========================================
class LinkAnalyzeRequest(BaseModel):
    text: Optional[str] = Field(default=None, max_length=20000, description="Bio or caption text to extract links from")
    urls: Optional[List[str]] = Field(default=None, description="Direct list of URLs to analyze")


# Backward compatibility alias
LinkAnalyzeIn = LinkAnalyzeRequest


class ScanMediaLinksRequest(BaseModel):
    media_id: int
    platform_media_id: Optional[str] = None
    media_type: str = "VIDEO"
    caption: Optional[str] = None
    video_path: Optional[str] = None


class LinkReportOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    detected_url: str
    final_url: Optional[str] = None
    source_type: str = "caption"
    is_promotional: bool = True
    response_status: Optional[int] = None
    validation_result: str
    error_category: Optional[str] = None
    issue_description: Optional[str] = None
    checked_at: datetime
    redirect_count: Optional[int] = 0
    redirect_chain: Optional[Any] = None
    response_time_ms: Optional[float] = None
    analysis_report: Optional[Dict[str, Any]] = None


# Backward compatibility alias
LinkResultOut = LinkReportOut


# ==========================================
# NEWS SCHEMAS
# ==========================================
class NewsOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    description: Optional[str] = None
    source: str
    article_url: str
    category: str
    published_at: Optional[datetime] = None


# ==========================================
# MEDIA ITEM SCHEMAS
# ==========================================
class MediaItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    platform_media_id: Optional[str] = None
    media_type: str
    media_reference: Optional[str] = None
    permalink: Optional[str] = None
    thumbnail_url: Optional[str] = None
    caption: Optional[str] = None
    created_at: datetime


# ==========================================
# NOTIFICATION & CATALOG SCHEMAS
# ==========================================
class IssueNotificationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    media_id: Optional[int] = None
    issue_category: str
    issue_type: str
    severity: str
    title: str
    description: str
    recommendation: Optional[str] = None
    detected_url: Optional[str] = None
    final_url: Optional[str] = None
    source_type: Optional[str] = None
    http_status: Optional[int] = None
    audio_status: Optional[str] = None
    previous_audio_ref: Optional[str] = None
    current_audio_status: Optional[str] = None
    similarity_score: Optional[float] = None
    sync_offset_ms: Optional[float] = None
    confidence_score: Optional[float] = None
    problem_timestamps: Optional[str] = None
    analysis_report: Optional[Dict[str, Any]] = None
    is_read: bool
    is_resolved: bool
    is_dismissed: bool
    analysis_timestamp: datetime
    last_checked_at: datetime
    resolved_at: Optional[datetime] = None
    media: Optional[MediaItemOut] = None


class NotificationSummaryOut(BaseModel):
    total_issues: int
    broken_link_issues: int
    audio_issues: int
    lipsync_issues: int
    unresolved_issues: int
    resolved_issues: int
    unread_count: int


# ==========================================
# AUDIO DETECTOR SCHEMAS
# ==========================================
class AudioReferenceOut(BaseModel):
    reference_id: int


class AudioAnalysisOut(BaseModel):
    report_id: int
    status: str
    similarity: float
    details: Optional[Dict[str, Any]] = None


# ==========================================
# LIP-SYNC DETECTOR SCHEMAS
# ==========================================
class LipSyncReportOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    video_reference: str
    synchronization_status: str
    estimated_offset_ms: Optional[float] = None
    confidence_score: Optional[float] = None
    analysis_report: Optional[Dict[str, Any]] = None
    created_at: datetime


class JobStatusOut(BaseModel):
    job_id: int
    status: str
    progress: int


# ==========================================
# INSTAGRAM SCHEMAS (PHASE 2)
# ==========================================
class InstagramConnectOut(BaseModel):
    authorize_url: str
    url: str


class InstagramAccountOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    platform: str = "instagram"
    platform_user_id: str
    username: str
    status: str
    connection_status: str
    token_expiry: Optional[datetime] = None
    biography: Optional[str] = None
    external_url: Optional[str] = None
    profile_picture_url: Optional[str] = None
    connected_at: Optional[datetime] = None


class GrowthPointOut(BaseModel):
    date: str
    followers: float


class InstagramGrowthOut(BaseModel):
    series: List[Dict[str, Any]]
    data: List[GrowthPointOut]
    net_follower_change: Optional[float] = None
    note: Optional[str] = None


class InstagramMediaOut(BaseModel):
    data: List[MediaItemOut]
    total: int

