import os
from functools import lru_cache
from typing import List

from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load .env from container root if present
load_dotenv()


class Settings(BaseModel):
    """Application settings loaded from environment variables."""

    # Security
    SECRET_KEY: str = Field(default="CHANGE_ME", description="JWT signing secret")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=60, description="JWT expiry in minutes")
    ALGORITHM: str = Field(default="HS256", description="JWT algorithm")

    # Database
    DATABASE_URL: str = Field(default="postgresql+asyncpg://appuser:dbuser123@localhost:5001/myapp", description="SQLAlchemy async database URL")

    # CORS
    CORS_ALLOW_ORIGINS: List[str] = Field(default_factory=lambda: ["http://localhost:3000"], description="Allowed CORS origins")

    # Summarization service
    SUMMARIZATION_API_URL: str = Field(default="http://localhost:3001", description="External summarization API base URL")
    SUMMARIZATION_API_TOKEN: str = Field(default="dev-ai-token", description="Bearer token for summarization API")

    # Preview mode
    PREVIEW_NO_AUTH: bool = Field(default=True, description="Enable no-auth preview mode for testing (bypasses authentication)")


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings(
        SECRET_KEY=os.getenv("SECRET_KEY", "CHANGE_ME"),
        ACCESS_TOKEN_EXPIRE_MINUTES=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "500")),
        ALGORITHM=os.getenv("ALGORITHM", "HS256"),
        DATABASE_URL=os.getenv("DATABASE_URL", "postgresql+asyncpg://appuser:dbuser123@localhost:5001/myapp"),
        CORS_ALLOW_ORIGINS=[o.strip() for o in os.getenv("CORS_ALLOW_ORIGINS", "http://localhost:3000").split(",")],
        SUMMARIZATION_API_URL=os.getenv("SUMMARIZATION_API_URL", "http://localhost:3001"),
        SUMMARIZATION_API_TOKEN=os.getenv("SUMMARIZATION_API_TOKEN", "dev-ai-token"),
        PREVIEW_NO_AUTH=os.getenv("PREVIEW_NO_AUTH", "true").lower() in ("true", "1", "yes"),
    )


settings = get_settings()
