from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_user
from ..link_service import LinkAnalyzerService, check_url, extract_urls
from ..models import IssueNotification, LinkAnalysisReport, MediaItem, User
from ..schemas import LinkAnalyzeRequest, LinkReportOut, ScanMediaLinksRequest

router = APIRouter(prefix="/links", tags=["Link Analyzer"])


def _save_report_and_notify(
    db: Session,
    user_id: int,
    result: dict,
    media_id: Optional[int] = None,
) -> LinkAnalysisReport:
    report = LinkAnalysisReport(
        user_id=user_id,
        media_id=media_id,
        detected_url=result["detected_url"],
        final_url=result.get("final_url"),
        source_type=result.get("source_type", "caption"),
        is_promotional=result.get("is_promotional", True),
        response_status=result.get("response_status"),
        validation_result=result["validation_result"],
        error_category=result.get("error_category"),
        redirect_count=result.get("redirect_count", 0),
        redirect_chain=result.get("redirect_chain"),
        response_time_ms=result.get("response_time_ms"),
        issue_description=result.get("issue_description"),
        analysis_report=result.get("analysis_report"),
        checked_at=result.get("checked_at", datetime.now(timezone.utc)),
    )
    db.add(report)
    db.flush()

    # Automatically create or update a Broken Link Catalog notification if broken/suspicious
    if result["validation_result"] in ("broken", "suspicious"):
        existing_issue = (
            db.query(IssueNotification)
            .filter(
                IssueNotification.user_id == user_id,
                IssueNotification.issue_category == "broken_link",
                IssueNotification.detected_url == result["detected_url"],
                IssueNotification.is_dismissed == False,  # noqa: E712
            )
            .first()
        )

        status_label = (
            f"HTTP {result['response_status']}"
            if result.get("response_status")
            else "Unreachable / DNS Error"
        )
        title = f"Broken Promotional Link ({status_label})"
        description = (
            f"Detected via {result.get('source_type', 'caption').upper()}: "
            f"{result.get('issue_description') or 'Promotional link failed validation.'}"
        )
        recommendation = (
            "Update the Reel caption or bio link with an active landing page URL, "
            "or remove the expired affiliate redirect."
        )

        analysis_meta = {
            "redirect_chain": result.get("redirect_chain"),
            "redirect_count": result.get("redirect_count", 0),
            "response_time_ms": result.get("response_time_ms"),
            "final_url": result.get("final_url"),
            "source_type": result.get("source_type", "caption"),
        }

        if existing_issue:
            existing_issue.http_status = result.get("response_status")
            existing_issue.final_url = result.get("final_url")
            existing_issue.description = description
            existing_issue.analysis_report = analysis_meta
            existing_issue.last_checked_at = datetime.now(timezone.utc)
            existing_issue.is_resolved = False
        else:
            new_issue = IssueNotification(
                user_id=user_id,
                media_id=media_id,
                issue_category="broken_link",
                issue_type=result.get("error_category") or "broken_url",
                severity="critical" if result["validation_result"] == "broken" else "warning",
                title=title,
                description=description,
                recommendation=recommendation,
                detected_url=result["detected_url"],
                final_url=result.get("final_url"),
                source_type=result.get("source_type", "caption"),
                http_status=result.get("response_status"),
                analysis_report=analysis_meta,
                is_read=False,
                is_resolved=False,
                is_dismissed=False,
                analysis_timestamp=datetime.now(timezone.utc),
                last_checked_at=datetime.now(timezone.utc),
            )
            db.add(new_issue)

    return report


@router.post("/analyze", response_model=List[LinkReportOut])
def analyze_links(
    payload: LinkAnalyzeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    urls_to_check: List[str] = []
    if payload.urls:
        for u in payload.urls:
            norm = LinkAnalyzerService.normalize_url(u)
            if norm not in urls_to_check:
                urls_to_check.append(norm)

    if payload.text:
        extracted = extract_urls(payload.text)
        for u in extracted:
            if u not in urls_to_check:
                urls_to_check.append(u)

    if not urls_to_check:
        raise HTTPException(
            status_code=422,
            detail="No valid URLs found in the provided text or URL list.",
        )

    saved_reports: List[LinkAnalysisReport] = []
    for url in urls_to_check:
        res = LinkAnalyzerService.validate_url(
            url=url,
            source_type="caption",
            context_text=payload.text,
        )
        report = _save_report_and_notify(
            db=db,
            user_id=current_user.id,
            result=res,
            media_id=None,
        )
        saved_reports.append(report)

    db.commit()
    for r in saved_reports:
        db.refresh(r)

    return saved_reports


@router.post("/scan-media", response_model=List[LinkReportOut])
def scan_media_links(
    payload: ScanMediaLinksRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    media = (
        db.query(MediaItem)
        .filter(MediaItem.id == payload.media_id, MediaItem.user_id == current_user.id)
        .first()
    )
    caption_text = payload.caption or (media.caption if media else "")

    discovered: List[tuple[str, str]] = []
    for u in extract_urls(caption_text):
        discovered.append((u, "caption"))

    if payload.video_path:
        mm_urls = LinkAnalyzerService.extract_video_multimodal_urls(payload.video_path)
        for source_key, url_list in mm_urls.items():
            for u in url_list:
                discovered.append((u, source_key))

    saved_reports: List[LinkAnalysisReport] = []
    seen = set()
    for url, source_type in discovered:
        if (url, source_type) in seen:
            continue
        seen.add((url, source_type))
        res = LinkAnalyzerService.validate_url(
            url=url,
            source_type=source_type,
            context_text=caption_text,
        )
        report = _save_report_and_notify(
            db=db,
            user_id=current_user.id,
            result=res,
            media_id=media.id if media else None,
        )
        saved_reports.append(report)

    db.commit()
    for r in saved_reports:
        db.refresh(r)

    return saved_reports


@router.get("/reports", response_model=List[LinkReportOut])
def get_link_reports(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(LinkAnalysisReport)
        .filter(LinkAnalysisReport.user_id == current_user.id)
        .order_by(LinkAnalysisReport.checked_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


@router.get("/reports/{report_id}", response_model=LinkReportOut)
def get_single_link_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    report = (
        db.query(LinkAnalysisReport)
        .filter(
            LinkAnalysisReport.id == report_id,
            LinkAnalysisReport.user_id == current_user.id,
        )
        .first()
    )
    if not report:
        raise HTTPException(status_code=404, detail="Link analysis report not found.")
    return report
