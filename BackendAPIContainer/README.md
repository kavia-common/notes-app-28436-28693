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
- CORS_ALLOW_ORIGINS (comma-separated list of allowed origins)
- SUMMARIZATION_API_URL, SUMMARIZATION_API_TOKEN
- PREVIEW_NO_AUTH (boolean: enables no-auth preview mode)
- LOG_LEVEL, ENV

Preview-safe defaults are provided in `.env` for local runs:
- ACCESS_TOKEN_EXPIRE_MINUTES=500 (JWT token validity in minutes)
- DATABASE_URL=postgresql+asyncpg://appuser:dbuser123@localhost:5001/myapp
- CORS_ALLOW_ORIGINS=http://localhost:3000 (comma-separated, e.g., "http://localhost:3000,http://localhost:3001")
- SUMMARIZATION_API_URL=http://localhost:3001
- PREVIEW_NO_AUTH=true (allows unauthenticated access to notes routes)
- LOG_LEVEL=info
- ENV=development

### Preview Mode (PREVIEW_NO_AUTH)
When `PREVIEW_NO_AUTH=true`, the backend allows unauthenticated access to all `/notes` endpoints without requiring an Authorization header. This is useful for:
- Quick testing and previewing the app
- Development without setting up authentication
- Demo environments

**Important:** In production, always set `PREVIEW_NO_AUTH=false` to enforce JWT authentication.

When enabled, a stub preview user (ID: 9999) is used for all operations. Authentication endpoints (/auth/login, /auth/register) remain functional and unchanged.

### CORS Configuration
The `CORS_ALLOW_ORIGINS` environment variable accepts a comma-separated list of allowed origins. Examples:
- Single origin: `CORS_ALLOW_ORIGINS=http://localhost:3000`
- Multiple origins: `CORS_ALLOW_ORIGINS=http://localhost:3000,http://localhost:3001,https://app.example.com`
- Allow all (not recommended for production): `CORS_ALLOW_ORIGINS=*`

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

## Authentication Behavior
### Normal Mode (PREVIEW_NO_AUTH=false)
All `/notes` endpoints require a valid JWT token in the Authorization header:
```
Authorization: Bearer <your-jwt-token>
```
Requests without a valid token will receive a 401 Unauthorized response.

### Preview Mode (PREVIEW_NO_AUTH=true)
All `/notes` endpoints work without authentication:
- No Authorization header required
- A stub preview user is automatically used for all operations
- Authentication endpoints (/auth/login, /auth/register, /auth/logout) remain functional

## Notes
- The logout endpoint returns 204 (stateless JWT).
- The password reset endpoint is a placeholder and should be replaced with a real email flow.
- Summarization client polls an external API and falls back to a trimmed content snippet on failure.
- When summarization fails or times out, a truncated version of the note content (first 140 characters) is returned as a fallback.

