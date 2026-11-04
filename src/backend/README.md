# AROHA Backend (FastAPI)

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
copy .env.example .env
.\.venv\Scripts\python -m uvicorn app.main:app --reload   # http://localhost:8000/docs
.\.venv\Scripts\python -m pytest -q
```

Uses SQLite by default; set `DATABASE_URL` to PostgreSQL for deployment.

## Status
| Module | State |
|---|---|
| Auth, user settings | Done (cookie session, Argon2id) |
| Link analyzer (manual text/URLs) | Done, SSRF-protected |
| News (RSS) | Done |
| Alembic migrations | Done (`alembic upgrade head`) |
| Audio loss detector (WAV) | Done |
| Instagram connect, sync, growth | Done, mock-tested only; needs Meta credentials |
| Lip-sync analyzer, Celery, frontend | Todo, see `../../STATUS.md` |
