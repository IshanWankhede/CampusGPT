from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    LLM_API_KEY: str = ""
    LLM_MODEL: str = "claude-sonnet-5"
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    CORS_ORIGINS: str = "http://localhost:5173"
    ENV: str = "development"

    class Config:
        env_file = ".env"


settings = Settings()