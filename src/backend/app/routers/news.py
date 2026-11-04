import re
from datetime import datetime, timezone
from time import mktime
from urllib.parse import urlparse

import feedparser
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..config import settings
from ..database import get_db
from ..deps import current_user
from ..models import NewsArticle, User
from ..schemas import NewsOut

router = APIRouter(prefix="/news", tags=["News"])

CATEGORY_KEYWORDS = {
    "algorithm": ["algorithm", "ranking", "reach"],
    "creators": ["creator", "influencer", "monetiz"],
    "features": ["feature", "launch", "update", "rolls out", "new "],
    "policy": ["policy", "ban", "regulat", "privacy", "law"],
    "ai": [" ai ", "artificial intelligence", "machine learning"],
}


def categorise(text: str) -> str:
    t = f" {text.lower()} "
    for cat, words in CATEGORY_KEYWORDS.items():
        if any(w in t for w in words):
            return cat
    return "general"


def refresh_news(db: Session) -> int:
    """Fetch configured RSS feeds and store new articles. Returns number added."""
    added = 0
    for feed_url in settings.news_feeds:
        parsed = feedparser.parse(feed_url)
        source = parsed.feed.get("title") or urlparse(feed_url).hostname or "unknown"
        for e in parsed.entries:
            url = e.get("link")
            if not url or db.scalar(select(NewsArticle.id).where(NewsArticle.article_url == url)):
                continue
            published = None
            if e.get("published_parsed"):
                published = datetime.fromtimestamp(mktime(e.published_parsed), tz=timezone.utc)
            desc = re.sub(r"<[^>]+>", "", e.get("summary", ""))[:1000] or None
            title = e.get("title", "Untitled")[:500]
            db.add(NewsArticle(title=title, description=desc, source=source[:200], article_url=url[:1000],
                               category=categorise(f"{title} {desc or ''}"), published_at=published))
            added += 1
    db.commit()
    return added


@router.get("", response_model=list[NewsOut])
def list_news(category: str | None = None, q: str | None = None, limit: int = 30, offset: int = 0,
              db: Session = Depends(get_db)):
    stmt = select(NewsArticle).order_by(NewsArticle.published_at.desc().nullslast(), NewsArticle.id.desc())
    if category:
        stmt = stmt.where(NewsArticle.category == category)
    if q:
        stmt = stmt.where(NewsArticle.title.ilike(f"%{q}%"))
    return db.scalars(stmt.limit(min(limit, 100)).offset(max(offset, 0))).all()


@router.get("/categories")
def categories(db: Session = Depends(get_db)):
    rows = db.execute(select(NewsArticle.category, func.count()).group_by(NewsArticle.category)).all()
    return [{"category": c, "count": n} for c, n in rows]


@router.get("/trending", response_model=list[NewsOut])
def trending(db: Session = Depends(get_db)):
    stmt = select(NewsArticle).order_by(NewsArticle.published_at.desc().nullslast()).limit(10)
    return db.scalars(stmt).all()


@router.post("/refresh")
def refresh(db: Session = Depends(get_db), _: User = Depends(current_user)):
    return {"added": refresh_news(db)}


@router.get("/{article_id}", response_model=NewsOut)
def get_article(article_id: int, db: Session = Depends(get_db)):
    art = db.get(NewsArticle, article_id)
    if not art:
        raise HTTPException(404, "Article not found")
    return art
