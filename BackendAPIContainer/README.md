# BackendAPIContainer - Notes App

FastAPI backend providing JWT authentication, notes CRUD, summarization integration, and PostgreSQL persistence.

## Features
- JWT auth: /auth/register, /auth/login, /auth/logout, /auth/reset-password
- Notes CRUD: /notes (GET, POST), /notes/{id} (GET, PUT, DELETE)
- Summarization: /notes/{id}/summary (GET), /notes/{id}/summarize (POST)
- Async SQLAlchemy 2.0 with PostgreSQL (asyncpg)
- Alembic migrations ready
- CORS enabled for web and mobile frontends
- Config via environment variables (.env)

## Environment Variables
See .env.example for all variables:
- SECRET_KEY, ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM
- DATABASE_URL (e.g., postgresql+asyncpg://user:pass@host:5432/db)
- CORS_ALLOW_ORIGINS
- SUMMARIZATION_API_URL, SUMMARIZATION_API_TOKEN

## Local Development
1. Create and populate `.env` from `.env.example`.
2. Install dependencies:
   pip install -r requirements.txt
3. Run migrations (optional to start, models can be created by your own migration workflow):
   - Initialize alembic (already configured): alembic revision --autogenerate -m "init"
   - Apply: alembic upgrade head
4. Start server:
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

OpenAPI at: /openapi.json, Swagger UI at: /docs

## Notes
- The logout endpoint returns 204 (stateless JWT).
- The password reset endpoint is a placeholder and should be replaced with a real email flow.
- Summarization client polls an external API and falls back to a trimmed content snippet on failure.

