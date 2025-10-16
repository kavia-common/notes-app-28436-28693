from datetime import datetime

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.db.session import init_engine_and_session
from app.api.routes.auth import router as auth_router
from app.api.routes.notes import router as notes_router

# Startup DB engine init
init_engine_and_session()

# PUBLIC_INTERFACE
def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application with CORS, metadata, and routes.

    Returns:
        FastAPI: Configured FastAPI instance exposing authentication, notes CRUD,
                 and summarization endpoints. Includes OpenAPI metadata and tags.
    """
    app = FastAPI(
        title="Notes App Backend API",
        version="1.0.0",
        description="RESTful API for user authentication, note management, summarization, and audit logging.",
        openapi_tags=[
            {"name": "auth", "description": "Authentication and user account endpoints."},
            {"name": "notes", "description": "Note CRUD endpoints."},
            {"name": "summarization", "description": "AI summarization endpoints."},
            {"name": "health", "description": "Health check endpoints."},
        ],
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ALLOW_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(auth_router, prefix="/auth", tags=["auth"])
    app.include_router(notes_router, prefix="/notes", tags=["notes", "summarization"])

    @app.get("/", tags=["health"], summary="Health check", description="Simple health check endpoint.")
    async def health_check():
        return {"message": "Healthy", "timestamp": datetime.utcnow().isoformat()}

    # WebSocket usage help route (no websockets implemented yet, but added per docs requirement)
    @app.get(
        "/docs/websocket",
        tags=["health"],
        summary="WebSocket usage help",
        description="No WebSocket endpoints are currently implemented for this project.",
    )
    async def websocket_help():
        return {"message": "No WebSocket endpoints are currently implemented."}

    return app


app = create_app()
