import re
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


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
    email: str
    created_at: datetime


class ProfileUpdate(BaseModel):
    name: str = Field(min_length=1, max_length=120)


class LinkAnalyzeIn(BaseModel):
    text: str | None = Field(default=None, max_length=20000, description="Bio/caption text to extract links from")
    urls: list[str] = Field(default_factory=list, max_length=50)


class LinkResultOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    detected_url: str
    response_status: int | None
    validation_result: str
    issue_description: str | None
    checked_at: datetime


class NewsOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    description: str | None
    source: str
    article_url: str
    category: str
    published_at: datetime | None


class MediaItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    platform_media_id: str | None
    media_type: str
    media_reference: str | None
    permalink: str | None
    thumbnail_url: str | None
    caption: str | None
    created_at: datetime


class IssueNotificationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    media_id: int | None
    issue_category: str
    issue_type: str
    severity: str
    title: str
    description: str
    recommendation: str | None
    detected_url: str | None
    http_status: int | None
    audio_status: str | None
    previous_audio_ref: str | None
    current_audio_status: str | None
    similarity_score: float | None
    sync_offset_ms: float | None
    confidence_score: float | None
    problem_timestamps: str | None
    is_read: bool
    is_resolved: bool
    is_dismissed: bool
    analysis_timestamp: datetime
    last_checked_at: datetime
    resolved_at: datetime | None
    media: MediaItemOut | None = None


class NotificationSummaryOut(BaseModel):
    total_issues: int
    broken_link_issues: int
    audio_issues: int
    lipsync_issues: int
    unresolved_issues: int
    resolved_issues: int
    unread_count: int
