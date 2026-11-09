from pathlib import Path
from typing import Literal
from urllib.parse import urlparse

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[2]

# Stored as a constant so tests can reference the exact default value.
_JWT_DEV_DEFAULT = "development-only-change-me"

# Database names that must never be used in staging or production.
_RESERVED_NON_DEV_DB_NAMES: frozenset[str] = frozenset(
    {"campusgpt", "campusgpt_dev", "campusgpt_test"}
)

# Hosts that indicate a local/development database connection.
_LOCALHOST_HOSTS: frozenset[str] = frozenset({"localhost", "127.0.0.1", "::1"})


class Settings(BaseSettings):
    # DATABASE_URL has no default — startup fails immediately if unset.
    # SQLite is not supported: every migration after 0001 requires PostgreSQL.
    DATABASE_URL: str

    JWT_SECRET_KEY: str = _JWT_DEV_DEFAULT
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    REFRESH_TOKEN_LEEWAY_SECONDS: float = 10.0

    LLM_API_KEY: str = ""
    LLM_MODEL: str = "claude-sonnet-5"
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"

    CORS_ORIGINS: str = "http://localhost:5173"

    # Restricted to known values; any other string causes immediate startup failure.
    ENV: Literal["development", "staging", "production"] = "development"

    RESEND_API_KEY: str = ""
    EMAIL_FROM: str = "onboarding@resend.dev"

    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/api/v1/auth/google/callback"
    FRONTEND_URL: str = "http://localhost:5173"

    # ── Rate Limiting (WP5) ───────────────────────────────────────────────
    RATE_LIMIT_ENABLED: bool = True
    TRUSTED_PROXIES: str = "127.0.0.1,10.0.0.0/8,172.16.0.0/12,192.168.0.0/16"
    RATE_LIMIT_LOGIN_FAILURES_PER_IDENTIFIER: int = 5
    RATE_LIMIT_LOGIN_FAILURES_PER_IP: int = 20
    RATE_LIMIT_OTP_SEND_PER_IDENTIFIER: int = 3
    RATE_LIMIT_OTP_SEND_PER_IP: int = 10
    RATE_LIMIT_OTP_VERIFY_PER_IDENTIFIER: int = 10
    RATE_LIMIT_PASSWORD_RESET_PER_IDENTIFIER: int = 5

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @model_validator(mode="after")
    def _validate_non_development_settings(self) -> "Settings":
        """Reject startup when unsafe configuration is detected in staging or production.

        Guards are skipped entirely in development to preserve the existing
        developer workflow. All errors are collected before raising so that
        every violation is reported in a single startup failure.
        """
        if self.ENV == "development":
            return self

        env = self.ENV  # "staging" or "production"
        errors: list[str] = []

        # ── G1, G2, G3 — JWT Secret ──────────────────────────────────────────
        if self.JWT_SECRET_KEY == _JWT_DEV_DEFAULT:
            errors.append(
                f"JWT_SECRET_KEY must not use the development default in {env} "
                f"environments (generate a replacement with: openssl rand -hex 32)"
            )
        elif "development" in self.JWT_SECRET_KEY.lower():
            errors.append(
                f'JWT_SECRET_KEY contains the word "development" — replace it with '
                f"a securely generated secret (run: openssl rand -hex 32)"
            )
        elif len(self.JWT_SECRET_KEY) < 32:
            errors.append(
                f"JWT_SECRET_KEY must be at least 32 characters in {env} environments "
                f"(run: openssl rand -hex 32)"
            )

        # ── G4, G5, G5b, G6 — Database URL ───────────────────────────────────
        parsed = urlparse(self.DATABASE_URL)
        scheme_base = parsed.scheme.split("+")[0]       # "postgresql" from "postgresql+psycopg2"
        db_name = parsed.path.lstrip("/").strip().lower()  # exact, case-normalised
        host = parsed.hostname or ""

        if scheme_base == "sqlite":
            # G4
            errors.append(
                f"SQLite is not permitted as the application database in {env}. "
                f"Use PostgreSQL."
            )
        else:
            if db_name in _RESERVED_NON_DEV_DB_NAMES:
                # G5 + G5b
                suggestion = "campusgpt_staging" if env == "staging" else "campusgpt_prod"
                errors.append(
                    f"DATABASE_URL points to reserved database '{db_name}'. "
                    f"Use a dedicated {env} database (recommended: '{suggestion}')."
                )
            if env == "production" and host in _LOCALHOST_HOSTS:
                # G6 — production only; localhost is valid in staging.
                # Note: urlparse correctly extracts "::1" from IPv6 URLs using
                # RFC 3986 bracket notation: postgresql://user:pw@[::1]:5432/db
                errors.append(
                    f"DATABASE_URL points to localhost in a production environment. "
                    f"Use a network-accessible database host."
                )

        # ── G7 — CORS Origins ────────────────────────────────────────────────
        for origin in self.CORS_ORIGINS.split(","):
            if origin.strip().startswith("http://localhost"):
                errors.append(
                    f"CORS_ORIGINS includes a localhost origin ('{origin.strip()}') — "
                    f"this is not permitted in {env} environments"
                )
                break

        # ── G8 — Partial Google OAuth ─────────────────────────────────────────
        google_flags = [bool(self.GOOGLE_CLIENT_ID), bool(self.GOOGLE_CLIENT_SECRET)]
        if any(google_flags) and not all(google_flags):
            missing = (
                "GOOGLE_CLIENT_SECRET" if self.GOOGLE_CLIENT_ID else "GOOGLE_CLIENT_ID"
            )
            errors.append(
                f"GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET must both be set or both "
                f"be empty — '{missing}' is missing"
            )

        if errors:
            bullet_list = "\n".join(f"  \u2022 {e}" for e in errors)
            raise ValueError(
                f"CampusGPT cannot start in {env} mode due to unsafe configuration:\n"
                + bullet_list
            )

        return self


settings = Settings()
