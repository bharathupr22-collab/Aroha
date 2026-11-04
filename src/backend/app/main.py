from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .database import Base, engine
from .routers import audio, auth, consent, instagram, links, news, notifications, users

@asynccontextmanager
async def lifespan(_: FastAPI):
    # Dev convenience only. Production schema is managed by Alembic migrations.
    from . import models  # noqa: F401
    Base.metadata.create_all(engine)
    yield


app = FastAPI(title="AROHA API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware, allow_origins=settings.cors_origins, allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)


@app.middleware("http")
async def security_headers(request, call_next):
    response = await call_next(request)
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
    return response



@app.get("/health", tags=["System"])
def health():
    return {"status": "ok"}


for r in (auth.router, consent.router, users.router, links.router, audio.router, instagram.router, news.router, notifications.router):
    app.include_router(r)
