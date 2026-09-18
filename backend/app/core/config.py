from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./campusgpt.db"
    JWT_SECRET_KEY: str = "development-only-change-me"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    LLM_API_KEY: str = ""
    LLM_MODEL: str = "claude-sonnet-5"
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    CORS_ORIGINS: str = "http://localhost:5173"
    ENV: str = "development"

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()