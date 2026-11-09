"""WP5 Authentication Rate Limiting Test Suite.

Covers:
- Database-backed rate limiting for login, OTP send, OTP verify, password reset.
- Dual-dimension throttling: per-identifier and per-IP.
- HTTP 429 Too Many Requests with Retry-After header.
- Uniform non-revealing error messages (no enumeration oracle).
- Cumulative OTP guess limit across new code issuances.
- Trusted proxy verification vs untrusted X-Forwarded-For spoofing defense.
- Counter reset on successful login.
- Lazy pruning of old auth attempts.
"""

from datetime import datetime, timedelta, timezone
import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth import rate_limiter, service
from app.auth.rate_limiter import hash_identifier, hash_ip
from app.core.config import settings
from app.models.auth_attempt import AuthAttempt
from app.models.user import AuthProvider, CollegeName, User, UserRole


# ==============================================================================
# Helper Functions & Fixtures
# ==============================================================================


@pytest.fixture
def test_user(db_session: Session) -> User:
    """Fixture providing a registered, verified local user."""
    email = f"rate.user.{uuid.uuid4().hex[:8]}@coep.ac.in"
    password = "CorrectPassword123!"
    user = User(
        email=email,
        hashed_password=service.hash_password(password),
        full_name="Rate Limited User",
        role=UserRole.STUDENT,
        college=CollegeName.COEP,
        auth_provider=AuthProvider.LOCAL,
        is_active=True,
        is_email_verified=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


# ==============================================================================
# 1. Login Rate Limiting (Account & IP)
# ==============================================================================


def test_login_account_rate_limit(client: TestClient, test_user: User):
    """5 failed login attempts for an email triggers 429 with Retry-After.
    A different email is unaffected.
    """
    email = test_user.email
    # 5 failed attempts
    for _ in range(5):
        res = client.post(
            "/api/v1/auth/login",
            json={"email": email, "password": "WrongPassword1!", "college": "COEP"},
        )
        assert res.status_code == 401

    # 6th attempt is blocked by rate limiter
    blocked_res = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "WrongPassword1!", "college": "COEP"},
    )
    assert blocked_res.status_code == 429
    assert "Retry-After" in blocked_res.headers
    retry_after = int(blocked_res.headers["Retry-After"])
    assert 0 < retry_after <= 900
    assert "Too many failed login attempts" in blocked_res.json()["detail"]

    # Even with the correct password, the account is locked out during the window
    locked_res = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "CorrectPassword123!", "college": "COEP"},
    )
    assert locked_res.status_code == 429

    # Another account is unaffected
    other_email = f"other.{uuid.uuid4().hex[:8]}@coep.ac.in"
    other_res = client.post(
        "/api/v1/auth/login",
        json={"email": other_email, "password": "AnyPassword1!", "college": "COEP"},
    )
    assert other_res.status_code == 401  # Not 429


def test_login_success_resets_failure_counter(client: TestClient, test_user: User):
    """4 failed logins followed by 1 successful login resets the counter."""
    email = test_user.email

    # 4 failures (one below threshold of 5)
    for _ in range(4):
        res = client.post(
            "/api/v1/auth/login",
            json={"email": email, "password": "WrongPassword1!", "college": "COEP"},
        )
        assert res.status_code == 401

    # Successful login resets the failure window
    success_res = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "CorrectPassword123!", "college": "COEP"},
    )
    assert success_res.status_code == 200

    # Next failed attempt is #1, not #5
    res_after = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "WrongPassword1!", "college": "COEP"},
    )
    assert res_after.status_code == 401  # Not 429


def test_login_ip_rate_limit(client: TestClient, db_session: Session):
    """20 failed logins from a single IP triggers 429 even across different emails."""
    fake_ip = "192.0.2.55"  # Public IP simulation via trusted proxy header

    for i in range(20):
        res = client.post(
            "/api/v1/auth/login",
            json={"email": f"diff_user_{i}@coep.ac.in", "password": "WrongPassword1!", "college": "COEP"},
            headers={"X-Forwarded-For": fake_ip},
        )
        assert res.status_code == 401

    # 21st attempt from same IP is blocked
    blocked = client.post(
        "/api/v1/auth/login",
        json={"email": "fresh_user@coep.ac.in", "password": "WrongPassword1!", "college": "COEP"},
        headers={"X-Forwarded-For": fake_ip},
    )
    assert blocked.status_code == 429
    assert "Retry-After" in blocked.headers
    assert "network" in blocked.json()["detail"].lower()


# ==============================================================================
# 2. OTP Send Rate Limiting (Account & IP)
# ==============================================================================


def test_otp_send_account_rate_limit(client: TestClient):
    """3 OTP send requests in 15 minutes for an email triggers 429 with Retry-After."""
    email = f"otpsend.{uuid.uuid4().hex[:8]}@coep.ac.in"

    for _ in range(3):
        res = client.post(
            "/api/v1/auth/send-otp",
            json={"email": email, "purpose": "EMAIL_VERIFY", "college": "COEP"},
        )
        assert res.status_code == 200

    # 4th request triggers 429
    blocked = client.post(
        "/api/v1/auth/send-otp",
        json={"email": email, "purpose": "EMAIL_VERIFY", "college": "COEP"},
    )
    assert blocked.status_code == 429
    assert "Retry-After" in blocked.headers
    assert "Too many requests" in blocked.json()["detail"]


def test_otp_send_ip_rate_limit(client: TestClient):
    """10 OTP send requests from an IP in 60 minutes triggers 429."""
    fake_ip = "198.51.100.42"

    for i in range(10):
        res = client.post(
            "/api/v1/auth/send-otp",
            json={"email": f"ip_otp_{i}@coep.ac.in", "purpose": "EMAIL_VERIFY", "college": "COEP"},
            headers={"X-Forwarded-For": fake_ip},
        )
        assert res.status_code == 200

    # 11th request from same IP is blocked
    blocked = client.post(
        "/api/v1/auth/send-otp",
        json={"email": "fresh_otp_target@coep.ac.in", "purpose": "EMAIL_VERIFY", "college": "COEP"},
        headers={"X-Forwarded-For": fake_ip},
    )
    assert blocked.status_code == 429
    assert "Retry-After" in blocked.headers


# ==============================================================================
# 3. OTP Verify Cumulative Guess Rate Limiting
# ==============================================================================


def test_otp_verify_cumulative_guesses_limit(client: TestClient, db_session: Session):
    """Requesting a new OTP does NOT reset the cumulative guess limit (10 failed guesses / hour)."""
    email = f"cumulative.otp.{uuid.uuid4().hex[:8]}@coep.ac.in"

    # Send 1st OTP
    client.post(
        "/api/v1/auth/send-otp",
        json={"email": email, "purpose": "EMAIL_VERIFY", "college": "COEP"},
    )

    # 5 failed guesses (locks the 1st code)
    for _ in range(5):
        res = client.post(
            "/api/v1/auth/verify-otp",
            json={"email": email, "otp": "000000", "purpose": "EMAIL_VERIFY"},
        )
        assert res.status_code == 400

    # Send 2nd OTP (new code)
    client.post(
        "/api/v1/auth/send-otp",
        json={"email": email, "purpose": "EMAIL_VERIFY", "college": "COEP"},
    )

    # 5 more failed guesses on the 2nd code -> total 10 guesses reached
    for _ in range(5):
        res = client.post(
            "/api/v1/auth/verify-otp",
            json={"email": email, "otp": "000000", "purpose": "EMAIL_VERIFY"},
        )
        assert res.status_code == 400

    # 11th guess is blocked by the cumulative hourly limit (429)
    blocked = client.post(
        "/api/v1/auth/verify-otp",
        json={"email": email, "otp": "000000", "purpose": "EMAIL_VERIFY"},
    )
    assert blocked.status_code == 429
    assert "Retry-After" in blocked.headers
    assert "Too many failed verification attempts" in blocked.json()["detail"]


# ==============================================================================
# 4. Password Reset Rate Limiting
# ==============================================================================


def test_password_reset_rate_limit(client: TestClient, test_user: User):
    """5 password reset attempts in 60 min triggers 429 with Retry-After."""
    email = test_user.email

    for _ in range(5):
        res = client.post(
            "/api/v1/auth/reset-password",
            json={"email": email, "otp": "000000", "new_password": "NewValidPassword1!"},
        )
        assert res.status_code == 400

    # 6th attempt is rate-limited
    blocked = client.post(
        "/api/v1/auth/reset-password",
        json={"email": email, "otp": "000000", "new_password": "NewValidPassword1!"},
    )
    assert blocked.status_code == 429
    assert "Retry-After" in blocked.headers


# ==============================================================================
# 5. Non-Enumeration & Security
# ==============================================================================


def test_non_existent_account_rate_limited_uniformly(client: TestClient):
    """Non-existent emails trigger the exact same 429 responses as existing ones."""
    fake_email = "nonexistent.account.xyz@coep.ac.in"

    for _ in range(5):
        res = client.post(
            "/api/v1/auth/login",
            json={"email": fake_email, "password": "WrongPassword1!", "college": "COEP"},
        )
        assert res.status_code == 401

    blocked = client.post(
        "/api/v1/auth/login",
        json={"email": fake_email, "password": "WrongPassword1!", "college": "COEP"},
    )
    assert blocked.status_code == 429
    assert blocked.json()["detail"] == "Too many failed login attempts. Please try again later."


def test_spoofed_x_forwarded_for_from_untrusted_client_ignored():
    """Direct untrusted socket connections cannot spoof client IP via X-Forwarded-For."""
    from unittest.mock import MagicMock
    from fastapi import Request

    mock_request = MagicMock(spec=Request)
    # Untrusted external IP as socket host
    mock_request.client.host = "203.0.113.195"
    mock_request.headers = {"x-forwarded-for": "10.0.0.1, 1.2.3.4"}

    resolved_ip = rate_limiter.get_client_ip(mock_request)
    # Must ignore the header and return the direct socket IP
    assert resolved_ip == "203.0.113.195"


def test_trusted_proxy_forwarded_ip_honored():
    """Requests originating from a trusted proxy correctly extract the client IP."""
    from unittest.mock import MagicMock
    from fastapi import Request

    mock_request = MagicMock(spec=Request)
    # Trusted proxy socket host (e.g. localhost or internal docker network)
    mock_request.client.host = "127.0.0.1"
    mock_request.headers = {"x-forwarded-for": "203.0.113.50, 10.0.0.1"}

    resolved_ip = rate_limiter.get_client_ip(mock_request)
    assert resolved_ip == "203.0.113.50"


# ==============================================================================
# 6. Lazy Pruning
# ==============================================================================


def test_lazy_pruning_removes_old_records(db_session: Session):
    """Pruning deletes records older than 24 hours and preserves recent ones."""
    now = datetime.now(timezone.utc)
    old_time = now - timedelta(hours=25)
    recent_time = now - timedelta(hours=1)

    old_attempt = AuthAttempt(
        action="login",
        identifier_hash="old_ident",
        ip_hash="old_ip",
        success=False,
        created_at=old_time,
    )
    recent_attempt = AuthAttempt(
        action="login",
        identifier_hash="recent_ident",
        ip_hash="recent_ip",
        success=False,
        created_at=recent_time,
    )
    db_session.add_all([old_attempt, recent_attempt])
    db_session.commit()

    deleted_count = rate_limiter.prune_old_attempts(db_session, older_than_hours=24)
    assert deleted_count >= 1

    remaining = db_session.execute(
        select(AuthAttempt).where(AuthAttempt.identifier_hash.in_(["old_ident", "recent_ident"]))
    ).scalars().all()

    assert len(remaining) == 1
    assert remaining[0].identifier_hash == "recent_ident"

