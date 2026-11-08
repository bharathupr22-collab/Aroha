"""Phase 6 Automated Test Suite for AROHA.
Tests:
1. SSRF Protection & Link Integrity (127.0.0.1, private IPs, unsafe redirects, 404, timeouts, redirect loops).
2. Automated Instagram Profile Audit (broken_link, audio_loss, lipsync_mismatch).
3. Read-Only Feature Catalogs with joined media metadata.
4. Creator News Feed (categories, search, trending, feed refresh).
5. User Privacy & Informed Consent (media_retention, model_training opt-in and withdrawal).
"""
import pytest
from datetime import datetime, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.link_service import LinkAnalyzerService, is_safe_host, extract_urls, check_url
from app.models import Base, User, MediaItem, IssueNotification, ConsentRecord, NewsArticle, LinkAnalysis, AudioAnalysis, LipsyncAnalysis
from app.audit_service import trigger_profile_scan, seed_or_fetch_creator_media
from app.routers.notifications import get_feature_catalog, get_notification_summary, trigger_media_integrity_audit
from app.routers.news import list_news, categories, trending, refresh_news
from app.routers.consent import get_consents, set_consent
from app.schemas import ConsentIn, ConsentRecordOut


@pytest.fixture()
def db():
    """Isolated in-memory SQLite database session for unit and integration testing."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    session = Session()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def creator_user(db):
    """Fixture providing an active creator user."""
    user = User(
        name="Asha Creator",
        email="asha.creator@aroha.ai",
        password_hash="argon2_hashed_secret",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


# =====================================================================
# 1. SSRF & LINK INTEGRITY TESTS
# =====================================================================
def test_ssrf_blocking_localhost_and_internal_ips():
    """Ensure localhost and internal IP addresses are strictly rejected before socket calls."""
    restricted_urls = [
        "http://localhost:8000/admin",
        "http://127.0.0.1:3000/api/keys",
        "http://127.0.0.1/status",
        "http://0.0.0.0:80/",
        "http://[::1]:8080/",
        "http://10.0.0.1/confidential",
        "http://192.168.1.1/router-login",
        "http://172.16.0.1/internal",
        "http://169.254.169.254/latest/meta-data/",
    ]
    for target in restricted_urls:
        safe, reason = LinkAnalyzerService.is_ssrf_safe(target)
        assert safe is False, f"Expected {target} to be blocked by SSRF, but got True."
        assert reason is not None and "SSRF Protection" in reason

    # Validate is_safe_host helper
    assert is_safe_host("127.0.0.1") is False
    assert is_safe_host("10.0.0.2") is False
    assert is_safe_host("192.168.0.1") is False
    assert is_safe_host("169.254.169.254") is False
    assert is_safe_host("localhost") is False


def test_suspicious_domain_and_credentials_detection():
    """Detect suspicious top-level domains (.zip, .click) and embedded HTTP credentials."""
    assert LinkAnalyzerService.check_suspicious_url("https://deal.zip/voucher") is not None
    assert LinkAnalyzerService.check_suspicious_url("https://free-gifts.click/redeem") is not None
    assert LinkAnalyzerService.check_suspicious_url("https://admin:password@malicious-site.com") is not None
    assert LinkAnalyzerService.check_suspicious_url("https://legitimate-brand.com/sale") is None


def test_ssrf_validation_result_structure():
    """Validate that LinkAnalyzerService.validate_url returns full diagnostic metrics for SSRF blocks."""
    res = LinkAnalyzerService.validate_url("http://127.0.0.1:8080/secret")
    assert res["validation_result"] == "suspicious"
    assert res["error_category"] == "ssrf_blocked"
    assert res["detected_url"] == "http://127.0.0.1:8080/secret"
    assert "redirect_chain" in res
    assert "response_time_ms" in res
    assert "analysis_report" in res


def test_url_extraction_and_promotional_context():
    """Verify promotional keywords and URL extraction across multi-line text."""
    sample_caption = (
        "Huge summer drop! Use code SUMMER26 for 20% off. "
        "Shop our collection at https://partner.store/summer and check bit.ly/promo26. "
        "Questions? Email support@brand.com."
    )
    extracted = extract_urls(sample_caption)
    assert len(extracted) == 2
    assert "https://partner.store/summer" in extracted
    assert "https://bit.ly/promo26" in extracted
    assert not any("support@brand.com" in u for u in extracted)

    # Promotional context validation
    assert LinkAnalyzerService.is_promotional_context(sample_caption, extracted[0]) is True
    assert LinkAnalyzerService.is_promotional_context(sample_caption, extracted[1]) is True


def test_http_404_and_timeout_detection(monkeypatch):
    """Ensure HTTP 404 responses and network timeouts are properly flagged in LinkAnalyzerService."""
    import httpx

    # Mock SSRF safety check to simulate a resolved public domain
    monkeypatch.setattr(LinkAnalyzerService, "is_ssrf_safe", lambda url: (True, None))

    # 1. Test timeout handling
    def mock_timeout_get(*args, **kwargs):
        raise httpx.TimeoutException("Connection timed out after 8 seconds.")

    monkeypatch.setattr(httpx.Client, "get", mock_timeout_get)
    timeout_res = LinkAnalyzerService.validate_url("https://delayed-partner-site.com/sale")
    assert timeout_res["validation_result"] == "broken"
    assert timeout_res["error_category"] == "timeout"
    assert "timed out" in timeout_res["issue_description"]

    # 2. Test HTTP 404 handling
    class Fake404Response:
        status_code = 404
        url = "https://partner.com/deal/expired404"
        is_redirect = False
        headers = {}

    monkeypatch.setattr(httpx.Client, "get", lambda *args, **kwargs: Fake404Response())
    res_404 = LinkAnalyzerService.validate_url("https://partner.com/deal/expired404")
    assert res_404["validation_result"] == "broken"
    assert res_404["response_status"] == 404
    assert res_404["error_category"] == "http_404"
    assert "HTTP 404" in res_404["issue_description"]


def test_notifications_scan_endpoint_execution(db, creator_user):
    """Verify trigger_media_integrity_audit (POST /notifications/scan) route handler."""
    scan_res = trigger_media_integrity_audit(db=db, user=creator_user)
    assert scan_res["status"] == "completed"
    assert scan_res["audited_media_count"] >= 4
    assert (scan_res["new_issues_detected"] + scan_res["existing_issues_updated"]) >= 3


# =====================================================================
# 2. AUTOMATED PROFILE AUDIT & CATALOG TESTS
# =====================================================================
def test_automated_profile_scan_populates_all_three_catalogs(db, creator_user):
    """Verify that a full profile audit automatically populates broken_link, audio_loss, and lipsync_mismatch catalogs."""
    # Run complete profile audit
    audit_res = trigger_profile_scan(db, creator_user)
    assert audit_res["status"] == "completed"
    assert audit_res["audited_media_count"] >= 4
    assert audit_res["new_issues_detected"] >= 3

    # 1. Broken Promotional Link Catalog
    broken_link_items = get_feature_catalog(
        category="broken_link",
        status="all",
        db=db,
        user=creator_user,
    )
    assert len(broken_link_items) >= 1
    bl = broken_link_items[0]
    assert bl.issue_category == "broken_link"
    assert bl.detected_url is not None
    assert bl.http_status in (404, 0, None)
    assert bl.media is not None
    assert bl.media.permalink is not None

    # 2. Audio Loss Detector Catalog
    audio_loss_items = get_feature_catalog(
        category="audio_loss",
        status="all",
        db=db,
        user=creator_user,
    )
    assert len(audio_loss_items) >= 1
    al = audio_loss_items[0]
    assert al.issue_category == "audio_loss"
    assert al.audio_status is not None
    assert al.previous_audio_ref is not None
    assert al.current_audio_status is not None
    assert al.similarity_score is not None
    assert al.media is not None

    # 3. Lip-Sync Analyzer Catalog
    lipsync_items = get_feature_catalog(
        category="lipsync_mismatch",
        status="all",
        db=db,
        user=creator_user,
    )
    assert len(lipsync_items) >= 1
    ls = lipsync_items[0]
    assert ls.issue_category == "lipsync_mismatch"
    assert ls.sync_offset_ms is not None
    assert ls.confidence_score is not None
    assert ls.problem_timestamps is not None
    assert ls.media is not None

    # Verify Summary Endpoint
    summary = get_notification_summary(db=db, user=creator_user)
    assert summary.total_issues >= 3
    assert summary.broken_link_issues >= 1
    assert summary.audio_issues >= 1
    assert summary.lipsync_issues >= 1
    assert summary.unresolved_issues >= 3
    assert summary.unread_count >= 3


def test_profile_scan_deduplication(db, creator_user):
    """Subsequent scans of the same media should update existing issues rather than duplicating them."""
    initial_audit = trigger_profile_scan(db, creator_user)
    initial_new = initial_audit["new_issues_detected"]
    assert initial_new >= 3

    # Trigger second scan
    second_audit = trigger_profile_scan(db, creator_user)
    assert second_audit["new_issues_detected"] == 0
    assert second_audit["existing_issues_updated"] == initial_new

    # Check total notification count in database
    total_issues = db.query(IssueNotification).filter(IssueNotification.user_id == creator_user.id).count()
    assert total_issues == initial_new


# =====================================================================
# 3. CREATOR NEWS FEED TESTS
# =====================================================================
def test_creator_news_feed_lifecycle(db, creator_user):
    """Verify news feed list, category grouping, trending articles, and feed refresh."""
    # 1. Refresh news
    refresh_result = refresh_news(db)
    assert refresh_result > 0

    # 2. List all articles
    all_articles = list_news(db=db)
    assert len(all_articles) >= 4

    # 3. Category count aggregation
    cat_counts = categories(db=db)
    assert len(cat_counts) >= 2
    cat_names = {c["category"] for c in cat_counts}
    assert "algorithm" in cat_names or "creators" in cat_names

    # 4. Filter by category
    algo_articles = list_news(category="algorithm", db=db)
    for art in algo_articles:
        assert art.category == "algorithm"

    # 5. Search by keyword
    search_articles = list_news(q="Instagram", db=db)
    assert len(search_articles) >= 1
    for art in search_articles:
        assert "instagram" in art.title.lower()

    # 6. Trending articles
    trending_articles = trending(db=db)
    assert len(trending_articles) >= 1
    assert len(trending_articles) <= 10


# =====================================================================
# 4. PRIVACY CONSENT & WITHDRAWAL TESTS
# =====================================================================
def test_privacy_consent_opt_in_and_withdrawal(db, creator_user):
    """Verify explicit granular opt-in and withdrawal tracking in ConsentRecord."""
    # 1. Initial state (withdrawn by default)
    initial_consents = get_consents(user=creator_user, db=db)
    assert initial_consents["media_retention"].consent_status == "withdrawn"
    assert initial_consents["media_retention"].granted is False
    assert initial_consents["model_training"].consent_status == "withdrawn"
    assert initial_consents["model_training"].granted is False

    # 2. Grant media retention consent
    grant_retention = set_consent(
        data=ConsentIn(consent_type="media_retention", granted=True),
        user=creator_user,
        db=db,
    )
    assert grant_retention.consent_type == "media_retention"
    assert grant_retention.consent_status == "granted"
    assert grant_retention.granted is True
    assert grant_retention.withdrawn_at is None

    # Check updated state
    current_consents = get_consents(user=creator_user, db=db)
    assert current_consents["media_retention"].consent_status == "granted"
    assert current_consents["media_retention"].granted is True
    assert current_consents["model_training"].granted is False

    # 3. Withdraw media retention consent
    withdraw_retention = set_consent(
        data=ConsentIn(consent_type="media_retention", granted=False),
        user=creator_user,
        db=db,
    )
    assert withdraw_retention.consent_type == "media_retention"
    assert withdraw_retention.consent_status == "withdrawn"
    assert withdraw_retention.granted is False
    assert withdraw_retention.withdrawn_at is not None

    # Check database records
    records = (
        db.query(ConsentRecord)
        .filter(ConsentRecord.user_id == creator_user.id, ConsentRecord.consent_type == "media_retention")
        .order_by(ConsentRecord.id.asc())
        .all()
    )
    assert len(records) >= 2
    # Verify historical withdrawal timestamp
    assert records[0].withdrawn_at is not None
    assert records[-1].consent_status == "withdrawn"
