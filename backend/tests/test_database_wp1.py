import os
import pytest
from sqlalchemy import text
from alembic.migration import MigrationContext
from alembic.autogenerate import compare_metadata

from app.database.base import Base
import app.models
from tests.conftest import TEST_DATABASE_URL, assert_test_database, test_engine


def test_metadata_contains_all_models():
    """WP1 verification: Base.metadata registers all application models."""
    tables = Base.metadata.tables
    assert "users" in tables, "Table 'users' is missing from Base.metadata"
    assert "otp_verifications" in tables, "Table 'otp_verifications' is missing from Base.metadata"
    assert "role_requests" in tables, "Table 'role_requests' is missing from Base.metadata"
    assert "login_codes" in tables, "Table 'login_codes' is missing from Base.metadata"
    assert "auth_attempts" in tables, "Table 'auth_attempts' is missing from Base.metadata"

    auth_attempt_cols = {c.name for c in tables["auth_attempts"].columns}
    expected_auth_attempt_cols = {
        "id",
        "action",
        "identifier_hash",
        "ip_hash",
        "success",
        "created_at",
    }
    assert expected_auth_attempt_cols.issubset(auth_attempt_cols), f"Missing auth_attempts columns: {expected_auth_attempt_cols - auth_attempt_cols}"

    login_code_cols = {c.name for c in tables["login_codes"].columns}
    expected_login_code_cols = {
        "id",
        "user_id",
        "code_hash",
        "nonce_hash",
        "expires_at",
        "used_at",
        "created_at",
    }
    assert expected_login_code_cols.issubset(login_code_cols), f"Missing login_codes columns: {expected_login_code_cols - login_code_cols}"

    user_cols = {c.name for c in tables["users"].columns}
    expected_user_cols = {
        "id",
        "email",
        "hashed_password",
        "full_name",
        "role",
        "college",
        "auth_provider",
        "google_id",
        "profile_picture",
        "is_active",
        "is_email_verified",
        "created_at",
        "updated_at",
    }
    assert expected_user_cols.issubset(user_cols), f"Missing user columns: {expected_user_cols - user_cols}"

    otp_cols = {c.name for c in tables["otp_verifications"].columns}
    expected_otp_cols = {
        "id",
        "user_id",
        "email",
        "otp_hash",
        "purpose",
        "expires_at",
        "attempts",
        "is_used",
        "verified_at",
        "created_at",
    }
    assert expected_otp_cols.issubset(otp_cols), f"Missing otp columns: {expected_otp_cols - otp_cols}"

    role_req_cols = {c.name for c in tables["role_requests"].columns}
    expected_role_req_cols = {
        "id",
        "user_id",
        "applicant_email",
        "requested_role",
        "status",
        "reviewed_by",
        "reviewed_at",
        "note",
        "created_at",
    }
    assert expected_role_req_cols.issubset(role_req_cols), f"Missing role_requests columns: {expected_role_req_cols - role_req_cols}"


def test_pgvector_extension_enabled():
    """WP1 verification: pgvector extension is installed and available in test database."""
    assert_test_database(TEST_DATABASE_URL)
    with test_engine.connect() as conn:
        result = conn.execute(
            text("SELECT extname FROM pg_extension WHERE extname = 'vector';")
        ).scalar()
        assert result == "vector", "Extension 'vector' is not present in pg_extension"


def test_alembic_autogenerate_zero_drift():
    """WP1 verification: Autogenerate against the migrated test database yields zero drift operations."""
    assert_test_database(TEST_DATABASE_URL)
    with test_engine.connect() as conn:
        mc = MigrationContext.configure(conn, opts={"compare_type": True})
        diff = compare_metadata(mc, Base.metadata)
        assert diff == [], f"Expected zero schema drift, but autogenerate detected: {diff}"
