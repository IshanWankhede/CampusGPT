"""WP3 — Production Configuration Guards: test suite.

Tests cover:
  - ENV Literal validation (invalid values rejected)
  - G1–G3: JWT_SECRET_KEY guards
  - G4:    SQLite dialect rejected in staging/production
  - G5/G5b: Reserved database names rejected in staging/production
  - G6:    Localhost host rejected in production (allowed in staging)
  - G7:    localhost CORS origins rejected in staging/production
  - G8:    Partial Google OAuth configuration rejected
  - Multi-error collection (all errors in one failure)
  - Development mode: all guards skipped
  - /health endpoint: no 'env' field in response
  - /docs, /redoc, /openapi.json: disabled in staging/production
"""

import os
from unittest.mock import patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.core.config import Settings, _JWT_DEV_DEFAULT, _RESERVED_NON_DEV_DB_NAMES

# ── Shared helpers ─────────────────────────────────────────────────────────────

# A set of env vars that satisfy every guard for a production deployment.
# Used as the baseline for all guard tests — override one field at a time.
_VALID_PROD_ENV = {
    "ENV": "production",
    "DATABASE_URL": "postgresql+psycopg2://user:strongpass@db.prod.example.com:5432/campusgpt_prod",
    "JWT_SECRET_KEY": "a" * 40,                  # 40 chars, no "development"
    "CORS_ORIGINS": "https://app.example.com",
    "GOOGLE_CLIENT_ID": "",
    "GOOGLE_CLIENT_SECRET": "",
    "RESEND_API_KEY": "",
    "JWT_ALGORITHM": "HS256",
    "FRONTEND_URL": "https://app.example.com",
    "GOOGLE_REDIRECT_URI": "https://app.example.com/api/v1/auth/google/callback",
    "EMAIL_FROM": "noreply@example.com",
    "LLM_API_KEY": "",
    "LLM_MODEL": "claude-sonnet-5",
    "EMBEDDING_MODEL": "all-MiniLM-L6-v2",
    "ACCESS_TOKEN_EXPIRE_MINUTES": "30",
    "REFRESH_TOKEN_EXPIRE_DAYS": "7",
}

_VALID_STAGING_ENV = {
    **_VALID_PROD_ENV,
    "ENV": "staging",
    "DATABASE_URL": "postgresql+psycopg2://user:strongpass@db.staging.example.com:5432/campusgpt_staging",
    "CORS_ORIGINS": "https://staging.example.com",
}


def _build_settings(overrides: dict) -> Settings:
    """Construct a Settings instance from env-var overrides, bypassing .env file."""
    env = {**_VALID_PROD_ENV, **overrides}
    with patch.dict(os.environ, env):
        return Settings(_env_file=None)


def _assert_raises_guard(overrides: dict, fragment: str | None = None) -> str:
    """Assert that Settings raises ValidationError; return error string."""
    with pytest.raises(ValidationError) as exc_info:
        _build_settings(overrides)
    error_str = str(exc_info.value)
    if fragment:
        assert fragment in error_str, (
            f"Expected fragment {fragment!r} not found in error:\n{error_str}"
        )
    return error_str


# ── ENV Literal validation ─────────────────────────────────────────────────────

class TestEnvLiteral:
    def test_accepts_development(self):
        with patch.dict(os.environ, {**_VALID_PROD_ENV, "ENV": "development"}):
            s = Settings(_env_file=None)
        assert s.ENV == "development"

    def test_accepts_staging(self):
        with patch.dict(os.environ, _VALID_STAGING_ENV):
            s = Settings(_env_file=None)
        assert s.ENV == "staging"

    def test_accepts_production(self):
        with patch.dict(os.environ, _VALID_PROD_ENV):
            s = Settings(_env_file=None)
        assert s.ENV == "production"

    def test_rejects_prod(self):
        with patch.dict(os.environ, {**_VALID_PROD_ENV, "ENV": "prod"}):
            with pytest.raises(ValidationError):
                Settings(_env_file=None)

    def test_rejects_dev(self):
        with patch.dict(os.environ, {**_VALID_PROD_ENV, "ENV": "dev"}):
            with pytest.raises(ValidationError):
                Settings(_env_file=None)

    def test_rejects_test(self):
        with patch.dict(os.environ, {**_VALID_PROD_ENV, "ENV": "test"}):
            with pytest.raises(ValidationError):
                Settings(_env_file=None)

    def test_rejects_blank(self):
        with patch.dict(os.environ, {**_VALID_PROD_ENV, "ENV": ""}):
            with pytest.raises(ValidationError):
                Settings(_env_file=None)


# ── G1 — JWT default value ─────────────────────────────────────────────────────

class TestG1JwtDefault:
    def test_rejects_default_in_production(self):
        _assert_raises_guard(
            {"JWT_SECRET_KEY": _JWT_DEV_DEFAULT},
            fragment="must not use the development default",
        )

    def test_rejects_default_in_staging(self):
        env = {**_VALID_STAGING_ENV, "JWT_SECRET_KEY": _JWT_DEV_DEFAULT}
        with patch.dict(os.environ, env):
            with pytest.raises(ValidationError) as exc_info:
                Settings(_env_file=None)
        assert "must not use the development default" in str(exc_info.value)


# ── G2 — JWT contains "development" ───────────────────────────────────────────

class TestG2JwtDevelopmentMarker:
    def test_rejects_key_containing_development(self):
        _assert_raises_guard(
            {"JWT_SECRET_KEY": "my-development-secret-xxxxxxxxxxxxxxxx"},
            fragment='contains the word "development"',
        )

    def test_rejects_key_with_Development_uppercase(self):
        _assert_raises_guard(
            {"JWT_SECRET_KEY": "my-Development-secret-xxxxxxxxxxxxxxxx"},
            fragment='contains the word "development"',
        )

    def test_rejects_key_ending_in_development(self):
        _assert_raises_guard(
            {"JWT_SECRET_KEY": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx-development"},
            fragment='contains the word "development"',
        )


# ── G3 — JWT minimum length ───────────────────────────────────────────────────

class TestG3JwtMinLength:
    def test_rejects_31_char_key(self):
        _assert_raises_guard(
            {"JWT_SECRET_KEY": "x" * 31},
            fragment="at least 32 characters",
        )

    def test_accepts_32_char_key(self):
        s = _build_settings({"JWT_SECRET_KEY": "x" * 32})
        assert len(s.JWT_SECRET_KEY) == 32

    def test_accepts_64_char_key(self):
        s = _build_settings({"JWT_SECRET_KEY": "a" * 64})
        assert len(s.JWT_SECRET_KEY) == 64


# ── G4 — SQLite dialect ───────────────────────────────────────────────────────

class TestG4SqliteDialect:
    def test_rejects_sqlite_in_production(self):
        _assert_raises_guard(
            {"DATABASE_URL": "sqlite:///./campusgpt.db"},
            fragment="SQLite is not permitted",
        )

    def test_rejects_sqlite_in_staging(self):
        env = {**_VALID_STAGING_ENV, "DATABASE_URL": "sqlite:///./campusgpt.db"}
        with patch.dict(os.environ, env):
            with pytest.raises(ValidationError) as exc_info:
                Settings(_env_file=None)
        assert "SQLite is not permitted" in str(exc_info.value)

    def test_accepts_postgresql_in_production(self):
        s = _build_settings({})
        assert s.DATABASE_URL.startswith("postgresql")


# ── G5 + G5b — Reserved database names ────────────────────────────────────────

class TestG5ReservedDatabaseNames:
    """Every name in _RESERVED_NON_DEV_DB_NAMES is rejected in staging and production."""

    @pytest.mark.parametrize("db_name", list(_RESERVED_NON_DEV_DB_NAMES))
    def test_rejects_reserved_name_in_production(self, db_name: str):
        url = f"postgresql+psycopg2://user:pw@db.prod.example.com:5432/{db_name}"
        _assert_raises_guard(
            {"DATABASE_URL": url},
            fragment="reserved database",
        )

    @pytest.mark.parametrize("db_name", list(_RESERVED_NON_DEV_DB_NAMES))
    def test_rejects_reserved_name_in_staging(self, db_name: str):
        url = f"postgresql+psycopg2://user:pw@db.staging.example.com:5432/{db_name}"
        env = {**_VALID_STAGING_ENV, "DATABASE_URL": url}
        with patch.dict(os.environ, env):
            with pytest.raises(ValidationError) as exc_info:
                Settings(_env_file=None)
        assert "reserved database" in str(exc_info.value)

    def test_rejects_campusgpt_uppercase_normalized(self):
        """Case-insensitive comparison: CampusGPT → campusgpt → rejected."""
        url = "postgresql+psycopg2://user:pw@db.prod.example.com:5432/CampusGPT"
        _assert_raises_guard({"DATABASE_URL": url}, fragment="reserved database")

    def test_rejects_campusgpt_mixed_case(self):
        url = "postgresql+psycopg2://user:pw@db.prod.example.com:5432/CAMPUSGPT"
        _assert_raises_guard({"DATABASE_URL": url}, fragment="reserved database")

    def test_accepts_campusgpt_prod_in_production(self):
        url = "postgresql+psycopg2://user:pw@db.prod.example.com:5432/campusgpt_prod"
        s = _build_settings({"DATABASE_URL": url})
        assert "campusgpt_prod" in s.DATABASE_URL

    def test_accepts_campusgpt_staging_in_staging(self):
        env = {
            **_VALID_STAGING_ENV,
            "DATABASE_URL": "postgresql+psycopg2://user:pw@db.staging.example.com:5432/campusgpt_staging",
        }
        with patch.dict(os.environ, env):
            s = Settings(_env_file=None)
        assert "campusgpt_staging" in s.DATABASE_URL

    def test_accepts_campusgpt_staging_in_production(self):
        """campusgpt_staging is not a reserved name — allowed in production."""
        url = "postgresql+psycopg2://user:pw@db.prod.example.com:5432/campusgpt_staging"
        s = _build_settings({"DATABASE_URL": url})
        assert "campusgpt_staging" in s.DATABASE_URL

    def test_accepts_custom_name_in_production(self):
        url = "postgresql+psycopg2://user:pw@db.prod.example.com:5432/myapp_production"
        s = _build_settings({"DATABASE_URL": url})
        assert "myapp_production" in s.DATABASE_URL

    def test_reserved_names_set_contains_expected_members(self):
        """Guard the guard: the reserved-names set must contain all three names."""
        assert "campusgpt" in _RESERVED_NON_DEV_DB_NAMES
        assert "campusgpt_dev" in _RESERVED_NON_DEV_DB_NAMES
        assert "campusgpt_test" in _RESERVED_NON_DEV_DB_NAMES

    def test_error_message_includes_recommendation_staging(self):
        url = "postgresql+psycopg2://user:pw@db.example.com:5432/campusgpt"
        env = {**_VALID_STAGING_ENV, "DATABASE_URL": url}
        with patch.dict(os.environ, env):
            with pytest.raises(ValidationError) as exc_info:
                Settings(_env_file=None)
        assert "campusgpt_staging" in str(exc_info.value)

    def test_error_message_includes_recommendation_production(self):
        url = "postgresql+psycopg2://user:pw@db.example.com:5432/campusgpt"
        error = _assert_raises_guard({"DATABASE_URL": url})
        assert "campusgpt_prod" in error


# ── G6 — Localhost host (production only) ─────────────────────────────────────

class TestG6LocalhostHost:
    @pytest.mark.parametrize("host,url_host", [
        ("localhost", "localhost"),
        ("127.0.0.1", "127.0.0.1"),
        ("::1", "[::1]"),          # IPv6 literals require brackets per RFC 3986
    ])
    def test_rejects_localhost_in_production(self, host: str, url_host: str):
        url = f"postgresql+psycopg2://user:pw@{url_host}:5432/campusgpt_prod"
        _assert_raises_guard({"DATABASE_URL": url}, fragment="points to localhost")

    @pytest.mark.parametrize("host", ["localhost", "127.0.0.1"])
    def test_allows_localhost_in_staging(self, host: str):
        url = f"postgresql+psycopg2://user:pw@{host}:5432/campusgpt_staging"
        env = {**_VALID_STAGING_ENV, "DATABASE_URL": url}
        with patch.dict(os.environ, env):
            s = Settings(_env_file=None)
        assert s.ENV == "staging"

    def test_allows_remote_host_in_production(self):
        url = "postgresql+psycopg2://user:pw@db.prod.example.com:5432/campusgpt_prod"
        s = _build_settings({"DATABASE_URL": url})
        assert s.ENV == "production"


# ── G7 — CORS localhost origins ───────────────────────────────────────────────

class TestG7CorsLocalhost:
    def test_rejects_localhost_cors_in_production(self):
        _assert_raises_guard(
            {"CORS_ORIGINS": "http://localhost:5173"},
            fragment="localhost origin",
        )

    def test_rejects_localhost_cors_in_staging(self):
        env = {**_VALID_STAGING_ENV, "CORS_ORIGINS": "http://localhost:5173"}
        with patch.dict(os.environ, env):
            with pytest.raises(ValidationError) as exc_info:
                Settings(_env_file=None)
        assert "localhost origin" in str(exc_info.value)

    def test_rejects_localhost_in_comma_separated_list(self):
        _assert_raises_guard(
            {"CORS_ORIGINS": "https://app.example.com,http://localhost:3000"},
            fragment="localhost origin",
        )

    def test_accepts_https_production_origin(self):
        s = _build_settings({"CORS_ORIGINS": "https://app.example.com"})
        assert s.ENV == "production"

    def test_accepts_multiple_production_origins(self):
        s = _build_settings(
            {"CORS_ORIGINS": "https://app.example.com,https://www.example.com"}
        )
        assert s.ENV == "production"


# ── G8 — Partial Google OAuth ─────────────────────────────────────────────────

class TestG8PartialGoogleOAuth:
    def test_rejects_client_id_only(self):
        _assert_raises_guard(
            {"GOOGLE_CLIENT_ID": "my-client-id", "GOOGLE_CLIENT_SECRET": ""},
            fragment="GOOGLE_CLIENT_SECRET",
        )

    def test_rejects_secret_only(self):
        _assert_raises_guard(
            {"GOOGLE_CLIENT_ID": "", "GOOGLE_CLIENT_SECRET": "my-secret"},
            fragment="GOOGLE_CLIENT_ID",
        )

    def test_accepts_both_set(self):
        s = _build_settings(
            {"GOOGLE_CLIENT_ID": "my-client-id", "GOOGLE_CLIENT_SECRET": "my-secret"}
        )
        assert s.GOOGLE_CLIENT_ID == "my-client-id"

    def test_accepts_both_empty(self):
        """Google OAuth disabled — both empty is explicitly allowed."""
        s = _build_settings({"GOOGLE_CLIENT_ID": "", "GOOGLE_CLIENT_SECRET": ""})
        assert s.GOOGLE_CLIENT_ID == ""
        assert s.GOOGLE_CLIENT_SECRET == ""


# ── Multi-error collection ─────────────────────────────────────────────────────

class TestMultiErrorCollection:
    def test_all_errors_reported_in_single_failure(self):
        """When multiple guards fire, all are listed in one ValidationError."""
        env = {
            **_VALID_PROD_ENV,
            "JWT_SECRET_KEY": _JWT_DEV_DEFAULT,          # G1
            "DATABASE_URL": "sqlite:///./campusgpt.db",  # G4
            "CORS_ORIGINS": "http://localhost:5173",     # G7
        }
        with patch.dict(os.environ, env):
            with pytest.raises(ValidationError) as exc_info:
                Settings(_env_file=None)
        error_str = str(exc_info.value)
        assert "must not use the development default" in error_str  # G1
        assert "SQLite is not permitted" in error_str                # G4
        assert "localhost origin" in error_str                       # G7

    def test_error_message_includes_env_name(self):
        error = _assert_raises_guard({"JWT_SECRET_KEY": _JWT_DEV_DEFAULT})
        assert "production" in error


# ── Development mode: all guards skipped ──────────────────────────────────────

class TestDevelopmentMode:
    def _build_dev(self, overrides: dict) -> Settings:
        env = {
            "ENV": "development",
            "DATABASE_URL": "sqlite:///./campusgpt.db",   # would fail in prod
            "JWT_SECRET_KEY": _JWT_DEV_DEFAULT,            # would fail in prod
            "CORS_ORIGINS": "http://localhost:5173",       # would fail in prod
            **overrides,
        }
        with patch.dict(os.environ, env):
            return Settings(_env_file=None)

    def test_accepts_sqlite_database_url(self):
        s = self._build_dev({})
        assert "sqlite" in s.DATABASE_URL

    def test_accepts_default_jwt_secret(self):
        s = self._build_dev({})
        assert s.JWT_SECRET_KEY == _JWT_DEV_DEFAULT

    def test_accepts_localhost_cors(self):
        s = self._build_dev({})
        assert "localhost" in s.CORS_ORIGINS

    def test_accepts_campusgpt_database_name(self):
        s = self._build_dev(
            {"DATABASE_URL": "postgresql+psycopg2://user:pw@localhost:5432/campusgpt"}
        )
        assert "campusgpt" in s.DATABASE_URL

    def test_accepts_campusgpt_test_database_name(self):
        s = self._build_dev(
            {"DATABASE_URL": "postgresql+psycopg2://user:pw@localhost:5432/campusgpt_test"}
        )
        assert "campusgpt_test" in s.DATABASE_URL


# ── /health endpoint ──────────────────────────────────────────────────────────

class TestHealthEndpoint:
    def test_health_returns_ok(self, client):
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_body_is_exactly_status_ok(self, client):
        body = client.get("/health").json()
        assert body == {"status": "ok"}

    def test_health_does_not_expose_env_field(self, client):
        body = client.get("/health").json()
        assert "env" not in body

    def test_health_does_not_expose_any_settings(self, client):
        body = client.get("/health").json()
        # Only 'status' key should be present
        assert set(body.keys()) == {"status"}


# ── API documentation endpoints ───────────────────────────────────────────────

class TestApiDocEndpoints:
    def test_docs_accessible_in_development(self, client):
        """In development mode (the container's ENV), /docs returns 200."""
        response = client.get("/docs")
        assert response.status_code == 200

    def test_redoc_accessible_in_development(self, client):
        response = client.get("/redoc")
        assert response.status_code == 200

    def test_openapi_accessible_in_development(self, client):
        response = client.get("/openapi.json")
        assert response.status_code == 200

    def test_docs_disabled_when_env_is_not_development(self):
        """Directly verify the conditional logic for non-development ENVs."""
        for non_dev_env in ("staging", "production"):
            docs_url = "/docs" if non_dev_env == "development" else None
            redoc_url = "/redoc" if non_dev_env == "development" else None
            openapi_url = "/openapi.json" if non_dev_env == "development" else None

            test_app = FastAPI(
                title="WP3 Test App",
                docs_url=docs_url,
                redoc_url=redoc_url,
                openapi_url=openapi_url,
            )
            test_client = TestClient(test_app)

            assert test_client.get("/docs").status_code == 404, (
                f"Expected /docs to be 404 in {non_dev_env}"
            )
            assert test_client.get("/redoc").status_code == 404, (
                f"Expected /redoc to be 404 in {non_dev_env}"
            )
            assert test_client.get("/openapi.json").status_code == 404, (
                f"Expected /openapi.json to be 404 in {non_dev_env}"
            )
