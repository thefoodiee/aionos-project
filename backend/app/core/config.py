import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://admin:admin123@db:5432/team_builder"
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000"
    DOCUMENT_STORAGE_PATH: str = "/data/uploads"
    ENVIRONMENT: str = "development"
    APP_VERSION: str = "1.0.0"

    # Gemini LLM configuration (sole LLM provider as requested)
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.5-flash"

    # Embedding configuration (384-dimensional dense vectors)
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    EMBEDDING_DIMENSION: int = 384

    model_config = SettingsConfigDict(
        extra="ignore",
        env_file=str(Path(__file__).parent.parent.parent / ".env"),
        env_file_encoding="utf-8"
    )

settings = Settings()
