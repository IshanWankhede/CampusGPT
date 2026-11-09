"""WP11 Logging, Request Correlation, Redaction and Audit Tests.

Covers:
1. Sentinel-based secret redaction in structured logs.
2. Request ID validation, generation, and response header propagation.
3. Persistent audit trail for authentication, OTP, token, and admin events.
4. Persistence of failed authentication events.
5. Append-only properties and metadata sanitization.
"""

import io
import json
import logging
import uuid
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.audit.service import record_audit_event, sanitize_audit_metadata
from app.core.logging import (
    JSONLogFormatter,
    RedactionFilter,
    get_current_request_id,
    redact_sensitive_value,
    set_current_request_id,
)
from app.models.audit_log import AuditLog
from app.models.role_request import RoleRequest, RoleRequestStatus
from app.models.user import User, UserRole


# ==============================================================================
# 1. Secret Redaction Tests
# ==============================================================================


def test_secret_redaction_dictionary_and_strings():
    """Confirms sensitive keys and values are strictly masked with [REDACTED]."""
    sentinel_password = "SuperSecretPassword123!"
    sentinel_jwt = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.doNotLeakThisSignature123456789"
    sentinel_otp = "849201"

    payload = {
        "email": "student@coep.ac.in",
        "password": sentinel_password,
        "refresh_token": sentinel_jwt,
        "otp": sentinel_otp,
        "nested": {
            "client_secret": "my-client-secret-999",
            "safe_field": "public_data",
        },
    }

    cleaned = redact_sensitive_value(payload)

    assert cleaned["password"] == "[REDACTED]"
    assert cleaned["refresh_token"] == "[REDACTED]"
    assert cleaned["otp"] == "[REDACTED]"
    assert cleaned["nested"]["client_secret"] == "[REDACTED]"
    assert cleaned["nested"]["safe_field"] == "public_data"
    assert cleaned["email"] == "student@coep.ac.in"


def test_redaction_filter_and_json_formatter():
    """Confirms that sensitive log records formatted as JSON redact secrets completely."""
    logger = logging.getLogger("test_redaction_logger")
    logger.setLevel(logging.INFO)

    stream = io.StringIO()
    handler = logging.StreamHandler(stream)
    handler.setFormatter(JSONLogFormatter())
    handler.addFilter(RedactionFilter())
    logger.addHandler(handler)

    sentinel_secret = "UltraSecretPassword987!"
    set_current_request_id("test-corr-id-12345")

    try:
        logger.info("User login attempt with password=%s", sentinel_secret)
        output = stream.getvalue()

        # The sentinel secret must NEVER appear in raw output
        assert sentinel_secret not in output, f"Sentinel password leaked into log output: {output}"
        assert "[REDACTED]" in output

        log_json = json.loads(output.strip().split("\n")[-1])
        assert log_json["request_id"] == "test-corr-id-12345"
        assert log_json["level"] == "INFO"
    finally:
        set_current_request_id(None)
        logger.removeHandler(handler)


# ==============================================================================
# 2. Correlation ID Middleware Tests
# ==============================================================================


def test_request_id_generated_when_missing(client: TestClient):
    """When X-Request-ID is omitted by client, middleware generates a valid UUID4."""
    res = client.get("/health")
    assert res.status_code == 200
    assert "X-Request-ID" in res.headers
    req_id = res.headers["X-Request-ID"]
    # Verify it is a valid UUID
    parsed = uuid.UUID(req_id)
    assert parsed.version == 4


def test_request_id_propagated_when_valid(client: TestClient):
    """When a valid X-Request-ID is supplied, it is preserved and echoed in response headers."""
    client_req_id = "client-req-id-abcdef-123456"
    res = client.get("/health", headers={"X-Request-ID": client_req_id})
    assert res.status_code == 200
    assert res.headers.get("X-Request-ID") == client_req_id


def test_request_id_replaced_when_malformed(client: TestClient):
    """When an invalid X-Request-ID (e.g. containing illegal chars or too short) is supplied, a fresh UUID4 is generated."""
    res = client.get("/health", headers={"X-Request-ID": "bad;injection<script>"})
    assert res.status_code == 200
    returned_id = res.headers.get("X-Request-ID")
    assert returned_id != "bad;injection<script>"
    assert uuid.UUID(returned_id).version == 4


# ==============================================================================
# 3. Audit Log Metadata Sanitization & Allowlist
# ==============================================================================


def test_audit_metadata_allowlist_filtering():
    """Confirms audit metadata only retains safe keys from the allowlist."""
    raw_metadata = {
        "email": "test@coep.ac.in",
        "password": "Password123!",  # Must be stripped
        "token": "secret_token",     # Must be stripped
        "role": "STUDENT",           # Allowed
        "status": "APPROVED",        # Allowed
        "random_unapproved": "val",  # Must be stripped
    }

    sanitized = sanitize_audit_metadata(raw_metadata)
    assert sanitized is not None
    assert "password" not in sanitized
    assert "token" not in sanitized
    assert "random_unapproved" not in sanitized
    assert sanitized["email"] == "test@coep.ac.in"
    assert sanitized["role"] == "STUDENT"
    assert sanitized["status"] == "APPROVED"


# ==============================================================================
# 4. Authentication & Administrative Event Persistence Tests
# ==============================================================================


def test_audit_login_success_and_failure(client: TestClient, db_session: Session, rbac_student_user: User):
    """Verifies that login success and failed login attempts create persistent audit rows."""
    # 1. Failed login attempt
    fail_res = client.post(
        "/api/v1/auth/login",
        json={
            "email": rbac_student_user.email,
            "password": "WrongPassword999!",
            "college": "COEP",
        },
    )
    assert fail_res.status_code == 401

    # Verify failed audit row was committed
    fail_logs = db_session.execute(
        select(AuditLog).where(AuditLog.action == "AUTH_LOGIN", AuditLog.outcome == "FAILURE")
    ).scalars().all()
    assert len(fail_logs) >= 1
    assert fail_logs[-1].metadata_["email"] == rbac_student_user.email

    # 2. Successful login attempt
    succ_res = client.post(
        "/api/v1/auth/login",
        json={
            "email": rbac_student_user.email,
            "password": "StudentPassword123!",
            "college": "COEP",
        },
    )
    assert succ_res.status_code == 200

    succ_logs = db_session.execute(
        select(AuditLog).where(AuditLog.action == "AUTH_LOGIN", AuditLog.outcome == "SUCCESS")
    ).scalars().all()
    assert len(succ_logs) >= 1
    assert succ_logs[-1].actor_id == rbac_student_user.id
    assert succ_logs[-1].metadata_["role"] == "STUDENT"


def test_audit_otp_and_password_reset(client: TestClient, db_session: Session, rbac_student_user: User):
    """Verifies audit entries for OTP verification failure and password reset."""
    # Failed OTP verification
    client.post(
        "/api/v1/auth/verify-otp",
        json={
            "email": rbac_student_user.email,
            "otp": "000000",
            "purpose": "EMAIL_VERIFY",
        },
    )

    otp_logs = db_session.execute(
        select(AuditLog).where(AuditLog.action == "OTP_VERIFIED", AuditLog.outcome == "FAILURE")
    ).scalars().all()
    assert len(otp_logs) >= 1
    assert otp_logs[-1].metadata_["reason"] == "INVALID_OR_EXPIRED"


def test_audit_role_request_review_lifecycle(
    client: TestClient,
    db_session: Session,
    rbac_admin_token: str,
    rbac_admin_user: User,
    rbac_student_user: User,
):
    """Verifies that admin approving a role request writes an audit log with reviewer metadata."""
    role_req = RoleRequest(
        user_id=rbac_student_user.id,
        applicant_email=rbac_student_user.email,
        requested_role=UserRole.FACULTY,
        status=RoleRequestStatus.PENDING,
    )
    db_session.add(role_req)
    db_session.commit()
    db_session.refresh(role_req)

    headers = {"Authorization": f"Bearer {rbac_admin_token}"}
    res = client.post(f"/api/v1/admin/role-requests/{role_req.id}/approve", headers=headers)
    assert res.status_code == 200

    audit_entry = db_session.execute(
        select(AuditLog).where(
            AuditLog.action == "ROLE_REQUEST_APPROVED",
            AuditLog.target_id == role_req.id,
        )
    ).scalar_one_or_none()

    assert audit_entry is not None
    assert audit_entry.actor_id == rbac_admin_user.id
    assert audit_entry.outcome == "SUCCESS"
    assert audit_entry.metadata_["applicant_email"] == rbac_student_user.email
    assert audit_entry.metadata_["requested_role"] == "FACULTY"


def test_audit_logout_events(client: TestClient, db_session: Session, rbac_student_token: str, rbac_student_user: User):
    """Verifies audit log recording for logout and logout-all."""
    headers = {"Authorization": f"Bearer {rbac_student_token}"}

    res_all = client.post("/api/v1/auth/logout-all", headers=headers)
    assert res_all.status_code == 204

    audit_all = db_session.execute(
        select(AuditLog).where(
            AuditLog.action == "AUTH_LOGOUT_ALL",
            AuditLog.actor_id == rbac_student_user.id,
        )
    ).scalars().all()
    assert len(audit_all) >= 1
    assert audit_all[-1].metadata_["scope"] == "ALL"

