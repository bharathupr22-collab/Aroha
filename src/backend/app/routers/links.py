from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import current_user
from ..link_service import check_url, extract_urls
from ..models import LinkAnalysis, User
from ..schemas import LinkAnalyzeIn, LinkResultOut

router = APIRouter(prefix="/links", tags=["Link Analyzer"])


@router.post("/analyze", response_model=list[LinkResultOut])
def analyze(data: LinkAnalyzeIn, user: User = Depends(current_user), db: Session = Depends(get_db)):
    urls = list(data.urls)
    if data.text:
        urls += extract_urls(data.text)
    urls = list(dict.fromkeys(u.strip() for u in urls if u.strip()))[:50]
    if not urls:
        raise HTTPException(422, "No links found to analyse")
    rows = []
    for url in urls:
        code, result, issue = check_url(url)
        row = LinkAnalysis(user_id=user.id, detected_url=url[:2000], response_status=code,
                           validation_result=result, issue_description=issue)
        db.add(row)
        rows.append(row)
    db.commit()
    return rows


@router.get("/reports", response_model=list[LinkResultOut])
def reports(user: User = Depends(current_user), db: Session = Depends(get_db)):
    stmt = select(LinkAnalysis).where(LinkAnalysis.user_id == user.id).order_by(LinkAnalysis.checked_at.desc()).limit(200)
    return db.scalars(stmt).all()


@router.get("/reports/{report_id}", response_model=LinkResultOut)
def report(report_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    row = db.get(LinkAnalysis, report_id)
    if not row or row.user_id != user.id:
        raise HTTPException(404, "Report not found")
    return row
