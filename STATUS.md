# AROHA – Build Status and Handoff

Last updated: 2026-11-02 ~15:51. Backend: `src/backend` (FastAPI). **18 tests pass.**

## Run
```powershell
cd src\backend
.\.venv\Scripts\python -m uvicorn app.main:app --reload     # http://localhost:8000/docs
.\.venv\Scripts\python -m pytest -q
.\.venv\Scripts\python -m alembic upgrade head              # production DB schema
```

## Done
| Area | Files | Notes |
|---|---|---|
| Auth, sessions, settings, delete account | `routers/auth.py`, `users.py`, `security.py` | Argon2id, HTTP-only cookie JWT, no account enumeration |
| Database (all 11 SRS tables) + Alembic | `models.py`, `migrations/versions/0001_initial_schema.py` | SQLite dev, PostgreSQL via `DATABASE_URL` |
| Link analyzer (text/URLs) | `link_service.py`, `routers/links.py` | SSRF-protected, per-user reports |
| News (RSS) | `routers/news.py` | Categories, search, trending, dedupe by URL |
| Audio loss detector (WAV) | `audio_service.py`, `routers/audio.py` | Fingerprint, missing / partially silent / changed / replaced |
| Instagram connect, sync, growth, analytics | `routers/instagram.py` | Tested with mocked Meta responses only |
| Consent (media retention, model training) | `routers/consent.py` | `has_consent()` helper to gate media retention later |

## Remaining
1. **Frontend (Next.js, React, TypeScript, Tailwind, Recharts)** – not started.
   Node.js is not installed. The `winget install OpenJS.NodeJS.LTS` run was interrupted at the admin prompt. Install it and then scaffold `src/frontend`.
   Pages (SRS 4.1): landing, login, register, forgot password, dashboard, analytics, growth, unfollowers, link analyzer, audio detector, lip-sync, trends and news, settings.
2. **Lip-sync analyzer** – not started. Needs FFmpeg, OpenCV, a lip-sync model (e.g. SyncNet-style) and Celery jobs. Endpoints: `/lipsync/upload|analyze|status/{job_id}|report/{report_id}`. Report accuracy must be measured, not assumed (SRS).
3. **Celery + Redis background jobs** – `background_jobs` table exists, with no workers or endpoints yet.
4. **Link extraction from video** (`/links/extract-from-video`): OpenCV frames, OCR (EasyOCR or PaddleOCR), QR codes, Whisper speech.
5. **Audio:** non-WAV formats (install FFmpeg and convert), and `/audio` analysis of Instagram Reels by media id.
6. **Instagram:**
   - Unfollowers view.
   - `/instagram/media` and per-post insights.
   - Scheduled daily snapshots (needs Celery beat).
   - Token refresh before expiry.
   - **Re-verify endpoints, fields and permissions against Meta's current docs.** They were written from memory.
   - Public use needs Meta Advanced Access (App Review and business verification), which is outside our control.
7. **Password-reset e-mail** (SMTP): `/auth/forgot-password` is a stub and sends nothing.
8. **Researcher/admin role** with dataset, annotation and evaluation management. Also wire `has_consent()` into uploads so media is deleted after processing unless the user consented (audio currently never stores the file).
9. **Hardening:** rate limiting on auth, a CSRF strategy for the cookie session when the frontend is on another origin, `COOKIE_SECURE=true` and a real `SECRET_KEY` and `TOKEN_ENCRYPTION_KEY` in production, and the HTTPS deployment setup.
10. **Housekeeping:** the stale root `synopsis.md` template still differs from `docs/AROHA_Synopsis.docx`, and `_extract*.py` in the root are scratch scripts that can be deleted.

## Needs from you
- Node.js LTS and FFmpeg installed (admin rights needed).
- Meta developer app (App ID and secret) for real Instagram testing, put in `src/backend/.env`.
- Decision on which comes next: frontend (visible demo) or lip-sync (hardest part).
