"""ORM models following SRS section 7 (database design)."""
from datetime import datetime, timezone

from sqlalchemy import (
    JSON, CheckConstraint, DateTime, Float, ForeignKey, Index, Integer, String, Text, UniqueConstraint, Boolean
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(254), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)


class ConnectedAccount(Base):
    __tablename__ = "connected_accounts"
    __table_args__ = (UniqueConstraint("platform", "platform_user_id"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    platform: Mapped[str] = mapped_column(String(30), default="instagram")
    platform_user_id: Mapped[str] = mapped_column(String(64))
    username: Mapped[str] = mapped_column(String(120))
    encrypted_access_token: Mapped[str] = mapped_column(Text)
    token_expiry: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    connection_status: Mapped[str] = mapped_column(String(20), default="connected")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class AnalyticsHistory(Base):
    __tablename__ = "analytics_history"
    __table_args__ = (Index("ix_analytics_acct_metric_time", "connected_account_id", "metric_name", "captured_at"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    connected_account_id: Mapped[int] = mapped_column(ForeignKey("connected_accounts.id", ondelete="CASCADE"))
    metric_name: Mapped[str] = mapped_column(String(60))
    metric_value: Mapped[float] = mapped_column(Float)
    reporting_period: Mapped[str] = mapped_column(String(30), default="day")
    captured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    source: Mapped[str] = mapped_column(String(40), default="instagram_api")
    calculation_method: Mapped[str | None] = mapped_column(String(120), nullable=True)


class MediaItem(Base):
    __tablename__ = "media_items"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    platform_media_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    media_type: Mapped[str] = mapped_column(String(20))  # REEL, VIDEO, IMAGE
    media_reference: Mapped[str | None] = mapped_column(String(500), nullable=True)
    permalink: Mapped[str | None] = mapped_column(String(500), nullable=True)
    thumbnail_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    caption: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class IssueNotification(Base):
    __tablename__ = "issue_notifications"
    __table_args__ = (
        Index("ix_issue_user_resolved", "user_id", "is_resolved"),
        Index("ix_issue_user_category", "user_id", "issue_category"),
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    media_id: Mapped[int | None] = mapped_column(ForeignKey("media_items.id", ondelete="CASCADE"), nullable=True)

    issue_category: Mapped[str] = mapped_column(String(40))  # broken_link | audio_loss | lipsync_mismatch
    issue_type: Mapped[str] = mapped_column(String(60))
    severity: Mapped[str] = mapped_column(String(20), default="warning")  # critical | warning | info

    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text)
    recommendation: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Diagnostic metadata
    detected_url: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    http_status: Mapped[int | None] = mapped_column(Integer, nullable=True)
    audio_status: Mapped[str | None] = mapped_column(String(40), nullable=True)
    previous_audio_ref: Mapped[str | None] = mapped_column(String(100), nullable=True)
    current_audio_status: Mapped[str | None] = mapped_column(String(100), nullable=True)
    similarity_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    sync_offset_ms: Mapped[float | None] = mapped_column(Float, nullable=True)
    confidence_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    problem_timestamps: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Status & Workflow
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    is_resolved: Mapped[bool] = mapped_column(Boolean, default=False)
    is_dismissed: Mapped[bool] = mapped_column(Boolean, default=False)

    analysis_timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    last_checked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    media: Mapped[MediaItem | None] = relationship(lazy="joined")


class LinkAnalysis(Base):
    __tablename__ = "link_analysis"
    __table_args__ = (Index("ix_link_analysis_user_time", "user_id", "checked_at"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    media_id: Mapped[int | None] = mapped_column(ForeignKey("media_items.id", ondelete="SET NULL"), nullable=True)
    detected_url: Mapped[str] = mapped_column(String(2000))
    response_status: Mapped[int | None] = mapped_column(Integer, nullable=True)
    validation_result: Mapped[str] = mapped_column(String(30))
    issue_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    checked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class AudioReference(Base):
    __tablename__ = "audio_references"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    media_id: Mapped[int | None] = mapped_column(ForeignKey("media_items.id", ondelete="SET NULL"), nullable=True)
    audio_fingerprint: Mapped[str] = mapped_column(Text)
    reference_file: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class AudioAnalysis(Base):
    __tablename__ = "audio_analysis"
    __table_args__ = (CheckConstraint("similarity_score >= 0 AND similarity_score <= 1"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    media_id: Mapped[int | None] = mapped_column(ForeignKey("media_items.id", ondelete="SET NULL"), nullable=True)
    detected_status: Mapped[str] = mapped_column(String(30))
    similarity_score: Mapped[float] = mapped_column(Float)
    analysis_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class LipsyncAnalysis(Base):
    __tablename__ = "lipsync_analysis"
    __table_args__ = (CheckConstraint("confidence_score >= 0 AND confidence_score <= 1"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    video_reference: Mapped[str] = mapped_column(String(500))
    synchronization_status: Mapped[str] = mapped_column(String(30))
    estimated_offset_ms: Mapped[float | None] = mapped_column(Float, nullable=True)
    confidence_score: Mapped[float] = mapped_column(Float, default=0.0)
    analysis_report: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class NewsArticle(Base):
    __tablename__ = "news_articles"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(500))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    source: Mapped[str] = mapped_column(String(200))
    article_url: Mapped[str] = mapped_column(String(1000), unique=True)
    category: Mapped[str] = mapped_column(String(60), default="general")
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class BackgroundJob(Base):
    __tablename__ = "background_jobs"
    __table_args__ = (Index("ix_jobs_user_time", "user_id", "created_at"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    job_type: Mapped[str] = mapped_column(String(40))
    job_status: Mapped[str] = mapped_column(String(20), default="queued")  # queued|running|completed|failed
    progress: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class ConsentRecord(Base):
    __tablename__ = "consent_records"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    consent_type: Mapped[str] = mapped_column(String(40))  # media_retention|model_training
    consent_status: Mapped[str] = mapped_column(String(20))  # granted|withdrawn
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    withdrawn_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
