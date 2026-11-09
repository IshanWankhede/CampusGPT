"""WP6 Refresh Token Rotation and Revocation Test Suite.

Covers:
- Issuance of tracked refresh tokens with unique jti and family_id.
- Refresh token rotation on every successful refresh.
- Reuse detection outside leeway revoking the entire family.
- Reuse detection inside leeway (10s) tolerating benign tab races without family revocation.
- Guardrail: unknown / invalid tokens cannot trigger family revocation.
- Deterministic concurrency handling.
- Logout and logout-all session revocation.
- Cascading revocation on password reset.
- Deactivated user rejection.
- Expiration validation.
- 15-minute access token lifetime (PD-03).
- Google OAuth exchange integration.
"""

from datetime import datetime, timedelta, timezone
import threading
from unittest.mock import MagicMock, patch
import urllib.parse
import uuid

from fastapi.testclient import TestClient
from jose import jwt
import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth import repository, service
from app.core.config import settings
from app.models.refresh_token import RefreshToken
from app.models.user import AuthProvider, CollegeName, User, UserRole


# ==============================================================================
# Helper Fixtures & Setup
# ==============================================================================


@pytest.fixture
def test_user(db_session: Session) -> User:
    """Fixture providing a registered, verified local user."""
    email = f"wp6.user.{uuid.uuid4().hex[:8]}@coep.ac.in"
    password = "CorrectPassword123!"
    user = User(
        email=email,
        hashed_password=service.hash_password(password),
        full_name="WP6 Test User",
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
# 1. Issuance & Claims
# ==============================================================================


def test_login_issues_tracked_refresh_token_with_jti(client: TestClient, test_user: User, db_session: Session):
    """Login returns access and refresh tokens, and records the refresh token in the database."""
    res = client.post(
        "/api/v1/auth/login",
        json={"email": test_user.email, "password": "CorrectPassword123!", "college": "COEP"},
    )
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert "refresh_token" in data

    # Decode refresh token JWT and inspect claims
    payload = service.decode_token(data["refresh_token"], "refresh")
    assert "jti" in payload
    assert "family_id" in payload
    assert payload["sub"] == str(test_user.id)

    # Verify database record
    jti = uuid.UUID(payload["jti"])
    record = db_session.execute(select(RefreshToken).where(RefreshToken.jti == jti)).scalar_one_or_none()
    assert record is not None
    assert record.user_id == test_user.id
    assert record.family_id == uuid.UUID(payload["family_id"])
    assert record.revoked_at is None
    assert record.replaced_by is None


def test_access_token_15_minutes_lifetime(client: TestClient, test_user: User):
    """Access token lifetime is exactly 15 minutes (900 seconds) per PD-03."""
    res = client.post(
        "/api/v1/auth/login",
        json={"email": test_user.email, "password": "CorrectPassword123!", "college": "COEP"},
    )
    assert res.status_code == 200
    access_token = res.json()["access_token"]
    payload = service.decode_token(access_token, "access")
    duration_seconds = payload["exp"] - payload["iat"]
    expected_seconds = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    assert duration_seconds == expected_seconds, (
        f"Expected {expected_seconds} seconds ({settings.ACCESS_TOKEN_EXPIRE_MINUTES} min), got {duration_seconds}"
    )


# ==============================================================================
# 2. Rotation & Reuse Detection
# ==============================================================================


def test_refresh_happy_path_rotates_tokens(client: TestClient, test_user: User, db_session: Session):
    """Calling /refresh returns rotated access and refresh tokens; old row marked revoked."""
    login_res = client.post(
        "/api/v1/auth/login",
        json={"email": test_user.email, "password": "CorrectPassword123!", "college": "COEP"},
    )
    old_refresh = login_res.json()["refresh_token"]
    old_payload = service.decode_token(old_refresh, "refresh")
    old_jti = uuid.UUID(old_payload["jti"])
    family_id = uuid.UUID(old_payload["family_id"])

    # Rotate
    refresh_res = client.post("/api/v1/auth/refresh", json={"refresh_token": old_refresh})
    assert refresh_res.status_code == 200
    rotated_data = refresh_res.json()
    new_refresh = rotated_data["refresh_token"]
    assert new_refresh != old_refresh
    assert "access_token" in rotated_data

    new_payload = service.decode_token(new_refresh, "refresh")
    new_jti = uuid.UUID(new_payload["jti"])
    assert new_jti != old_jti
    assert new_payload["family_id"] == str(family_id), "Rotated token must retain the family_id"

    # Verify DB: old token is revoked with replaced_by pointing to new_jti
    db_session.expire_all()
    old_record = db_session.execute(select(RefreshToken).where(RefreshToken.jti == old_jti)).scalar_one()
    assert old_record.revoked_at is not None
    assert old_record.replaced_by == new_jti

    # Verify DB: new token is active
    new_record = db_session.execute(select(RefreshToken).where(RefreshToken.jti == new_jti)).scalar_one()
    assert new_record.revoked_at is None
    assert new_record.family_id == family_id


def test_old_refresh_token_fails_after_rotation(client: TestClient, test_user: User):
    """Using an old refresh token after rotation fails with 401."""
    login_res = client.post(
        "/api/v1/auth/login",
        json={"email": test_user.email, "password": "CorrectPassword123!", "college": "COEP"},
    )
    old_refresh = login_res.json()["refresh_token"]

    # 1st rotation succeeds
    client.post("/api/v1/auth/refresh", json={"refresh_token": old_refresh})

    # Attempting to refresh again with the old token fails
    replay_res = client.post("/api/v1/auth/refresh", json={"refresh_token": old_refresh})
    assert replay_res.status_code == 401


def test_refresh_token_reuse_inside_leeway_window_tolerates_race(
    client: TestClient, test_user: User, db_session: Session
):
    """Replaying a rotated token within the 10s leeway window fails without revoking the family."""
    login_res = client.post(
        "/api/v1/auth/login",
        json={"email": test_user.email, "password": "CorrectPassword123!", "college": "COEP"},
    )
    t1_refresh = login_res.json()["refresh_token"]

    # Rotate t1 -> t2
    rotate_res = client.post("/api/v1/auth/refresh", json={"refresh_token": t1_refresh})
    t2_refresh = rotate_res.json()["refresh_token"]

    # Immediate replay of t1 (within seconds, well inside the 10s leeway)
    replay_res = client.post("/api/v1/auth/refresh", json={"refresh_token": t1_refresh})
    assert replay_res.status_code == 401
    assert "already rotated" in replay_res.json()["detail"].lower()

    # The family must NOT have been revoked! t2 must still be active and usable
    t2_rotate_res = client.post("/api/v1/auth/refresh", json={"refresh_token": t2_refresh})
    assert t2_rotate_res.status_code == 200, "t2 should still be valid because replay was within leeway"


def test_refresh_token_reuse_outside_leeway_revokes_entire_family(
    client: TestClient, test_user: User, db_session: Session
):
    """Replaying a rotated token outside the leeway (>10s) revokes the whole family."""
    login_res = client.post(
        "/api/v1/auth/login",
        json={"email": test_user.email, "password": "CorrectPassword123!", "college": "COEP"},
    )
    t1_refresh = login_res.json()["refresh_token"]
    t1_jti = uuid.UUID(service.decode_token(t1_refresh, "refresh")["jti"])

    # Rotate t1 -> t2
    rotate_res = client.post("/api/v1/auth/refresh", json={"refresh_token": t1_refresh})
    t2_refresh = rotate_res.json()["refresh_token"]

    # Artificially age t1's revoked_at to simulate reuse 30 seconds later (outside 10s leeway)
    db_session.expire_all()
    t1_record = db_session.execute(select(RefreshToken).where(RefreshToken.jti == t1_jti)).scalar_one()
    t1_record.revoked_at = datetime.now(timezone.utc) - timedelta(seconds=30)
    db_session.commit()

    # Malicious replay of aged t1
    malicious_res = client.post("/api/v1/auth/refresh", json={"refresh_token": t1_refresh})
    assert malicious_res.status_code == 401
    assert "compromised" in malicious_res.json()["detail"].lower()

    # Crucial assertion: the entire family is now terminated. t2 is now revoked!
    t2_res = client.post("/api/v1/auth/refresh", json={"refresh_token": t2_refresh})
    assert t2_res.status_code == 401


# ==============================================================================
# 3. Guardrails: Invalid and Unknown Tokens
# ==============================================================================


def test_stateless_legacy_token_without_jti_rejected(client: TestClient, test_user: User):
    """Stateless legacy tokens lacking jti or family_id are rejected with 401."""
    # Create an old-format JWT without jti/family_id
    legacy_jwt = jwt.encode(
        {"sub": str(test_user.id), "type": "refresh", "exp": datetime.now(timezone.utc) + timedelta(days=7)},
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )
    res = client.post("/api/v1/auth/refresh", json={"refresh_token": legacy_jwt})
    assert res.status_code == 401


def test_unknown_jti_token_cannot_trigger_revocation(client: TestClient, test_user: User, db_session: Session):
    """An unknown token with a fictitious jti fails with 401 and does not affect existing families."""
    # Legitimate session
    login_res = client.post(
        "/api/v1/auth/login",
        json={"email": test_user.email, "password": "CorrectPassword123!", "college": "COEP"},
    )
    legit_refresh = login_res.json()["refresh_token"]
    legit_family_id = service.decode_token(legit_refresh, "refresh")["family_id"]

    # Attacker crafts a token targeting the same family_id but with an unknown jti
    fake_jwt = jwt.encode(
        {
            "sub": str(test_user.id),
            "jti": str(uuid.uuid4()),  # Not in database!
            "family_id": legit_family_id,
            "type": "refresh",
            "exp": datetime.now(timezone.utc) + timedelta(days=7),
        },
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )

    fake_res = client.post("/api/v1/auth/refresh", json={"refresh_token": fake_jwt})
    assert fake_res.status_code == 401
    assert fake_res.json()["detail"] == "Invalid refresh token"

    # Legitimate session must remain completely intact!
    legit_res = client.post("/api/v1/auth/refresh", json={"refresh_token": legit_refresh})
    assert legit_res.status_code == 200


# ==============================================================================
# 4. Deterministic Concurrency
# ==============================================================================


def test_concurrent_refresh_calls_deterministic_outcome(mock_email_sender, test_user: User, db_session: Session):
    """Two concurrent threads calling rotate_refresh_token with the same token: exactly 1 succeeds."""
    from tests.conftest import TEST_DATABASE_URL, assert_test_database
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    assert_test_database(TEST_DATABASE_URL)

    # Seed a tracked refresh token directly via service (uses db_session → campusgpt_test)
    refresh_token = service.create_refresh_token(
        test_user, db_session, user_agent="test-agent", ip_hash="aabbcc"
    )

    engine = create_engine(TEST_DATABASE_URL, pool_size=5, max_overflow=10)
    SessionFactory = sessionmaker(bind=engine, autocommit=False, autoflush=False)

    results = []
    lock = threading.Lock()

    def do_rotate():
        sess = SessionFactory()
        try:
            new_a, new_r, u = service.rotate_refresh_token(sess, refresh_token)
            with lock:
                results.append((True, 200))
        except Exception as exc:
            with lock:
                results.append((False, str(exc)))
        finally:
            sess.close()

    t1 = threading.Thread(target=do_rotate)
    t2 = threading.Thread(target=do_rotate)
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    engine.dispose()

    successes = sum(1 for success, _ in results if success)
    assert successes == 1, f"Expected exactly one successful rotation, got results: {results}"


# ==============================================================================
# 5. Logout & Logout-All
# ==============================================================================


def test_logout_revokes_token_family(client: TestClient, test_user: User):
    """Calling POST /logout with a refresh token revokes the token family."""
    login_res = client.post(
        "/api/v1/auth/login",
        json={"email": test_user.email, "password": "CorrectPassword123!", "college": "COEP"},
    )
    refresh_tok = login_res.json()["refresh_token"]

    logout_res = client.post("/api/v1/auth/logout", json={"refresh_token": refresh_tok})
    assert logout_res.status_code == 204

    # Subsequent refresh is blocked
    refresh_res = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_tok})
    assert refresh_res.status_code == 401


def test_logout_all_revokes_all_user_tokens(client: TestClient, test_user: User):
    """Calling POST /logout-all revokes all active refresh tokens for the user."""
    # Device 1 login
    res1 = client.post(
        "/api/v1/auth/login",
        json={"email": test_user.email, "password": "CorrectPassword123!", "college": "COEP"},
    )
    token1 = res1.json()["refresh_token"]
    access1 = res1.json()["access_token"]

    # Device 2 login
    res2 = client.post(
        "/api/v1/auth/login",
        json={"email": test_user.email, "password": "CorrectPassword123!", "college": "COEP"},
    )
    token2 = res2.json()["refresh_token"]

    # Logout all from Device 1
    logout_all_res = client.post(
        "/api/v1/auth/logout-all",
        headers={"Authorization": f"Bearer {access1}"},
    )
    assert logout_all_res.status_code == 204

    # Both tokens are now revoked
    assert client.post("/api/v1/auth/refresh", json={"refresh_token": token1}).status_code == 401
    assert client.post("/api/v1/auth/refresh", json={"refresh_token": token2}).status_code == 401


def test_password_reset_revokes_all_refresh_tokens(client: TestClient, test_user: User, db_session: Session):
    """Resetting password immediately revokes all active refresh tokens for the user."""
    login_res = client.post(
        "/api/v1/auth/login",
        json={"email": test_user.email, "password": "CorrectPassword123!", "college": "COEP"},
    )
    refresh_token = login_res.json()["refresh_token"]

    # Seed verified OTP for password reset (must use user_id so get_latest_active_otp matches)
    from app.models.otp_verification import OtpPurpose, OtpVerification
    otp_rec = OtpVerification(
        user_id=test_user.id,
        email=test_user.email,
        otp_hash=service.hash_password("112233"),
        purpose=OtpPurpose.PASSWORD_RESET,
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=10),
        is_used=False,
    )
    db_session.add(otp_rec)
    db_session.commit()

    # Reset password
    reset_res = client.post(
        "/api/v1/auth/reset-password",
        json={"email": test_user.email, "otp": "112233", "new_password": "NewStrongPass123!"},
    )
    assert reset_res.status_code == 200

    # Old refresh token is revoked
    assert client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token}).status_code == 401


def test_deactivated_user_cannot_refresh(client: TestClient, test_user: User, db_session: Session):
    """Deactivating a user prevents refresh."""
    login_res = client.post(
        "/api/v1/auth/login",
        json={"email": test_user.email, "password": "CorrectPassword123!", "college": "COEP"},
    )
    refresh_token = login_res.json()["refresh_token"]

    # Deactivate user
    test_user.is_active = False
    db_session.commit()

    res = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert res.status_code == 401
    assert "deactivated" in res.json()["detail"].lower()


def test_expired_refresh_token_rejected(client: TestClient, test_user: User, db_session: Session):
    """An expired refresh token is rejected."""
    login_res = client.post(
        "/api/v1/auth/login",
        json={"email": test_user.email, "password": "CorrectPassword123!", "college": "COEP"},
    )
    refresh_tok = login_res.json()["refresh_token"]
    payload = service.decode_token(refresh_tok, "refresh")
    jti = uuid.UUID(payload["jti"])

    # Age token in DB
    db_session.expire_all()
    record = db_session.execute(select(RefreshToken).where(RefreshToken.jti == jti)).scalar_one()
    record.expires_at = datetime.now(timezone.utc) - timedelta(seconds=1)
    db_session.commit()

    res = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_tok})
    assert res.status_code == 401


def test_google_oauth_exchange_issues_tracked_refresh_token(client: TestClient, db_session: Session):
    """WP4 Google OAuth exchange produces a tracked refresh token."""
    login_res = client.get("/api/v1/auth/google/login?college=COEP", follow_redirects=False)
    state = urllib.parse.parse_qs(urllib.parse.urlparse(login_res.headers["location"]).query)["state"][0]

    mock_client = MagicMock()
    mock_token_res = MagicMock(status_code=200, is_success=True)
    mock_token_res.json.return_value = {"access_token": "mock_google_token"}
    mock_userinfo = MagicMock(status_code=200, is_success=True)
    mock_userinfo.json.return_value = {
        "email": f"google.wp6.{uuid.uuid4().hex[:8]}@coep.ac.in",
        "email_verified": True,
        "sub": f"google-sub-{uuid.uuid4().hex[:8]}",
        "name": "Google User WP6",
    }
    mock_client.post.return_value = mock_token_res
    mock_client.get.return_value = mock_userinfo
    mock_client.__enter__.return_value = mock_client
    mock_client.__exit__.return_value = None

    with patch("app.auth.router.httpx.Client", return_value=mock_client):
        cb_res = client.get(f"/api/v1/auth/google/callback?code=mock_code&state={state}", follow_redirects=False)
        code = urllib.parse.parse_qs(urllib.parse.urlparse(cb_res.headers["location"]).query)["code"][0]

    exchange_res = client.post(
        "/api/v1/auth/google/exchange",
        json={"code": code},
        headers={"Origin": "http://localhost:5173"},
    )
    assert exchange_res.status_code == 200
    refresh_tok = exchange_res.json()["refresh_token"]

    payload = service.decode_token(refresh_tok, "refresh")
    jti = uuid.UUID(payload["jti"])

    record = db_session.execute(select(RefreshToken).where(RefreshToken.jti == jti)).scalar_one_or_none()
    assert record is not None
    assert record.revoked_at is None

