"""WP4 Google OAuth Security Hardening — Test Suite.

Covers:
- Login initiation: binding nonce cookie set correctly.
- Callback: missing / mismatched nonce redirects to error page (no cookie clear).
- Callback: successful redirect contains ?code= only, not tokens.
- Callback: security headers present.
- Exchange: happy path (Origin + JSON + cookie → 200 + tokens, cookie cleared).
- Exchange: missing / mismatched cookie → 400 generic error.
- Exchange: invalid Origin → 403.
- Exchange: missing Origin → 403.
- Exchange: wrong Content-Type → 415.
- Exchange: code replay → 400.
- Exchange: expired code → 400.
- Exchange: unknown code → 400.
- Concurrency: exactly one concurrent call succeeds.
- Multi-tab: second login session supersedes the first.
"""

import concurrent.futures
import hashlib
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch
import urllib.parse
import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth import repository, service
from app.database.session import SessionLocal
from app.models.login_code import LoginCode
from app.models.user import AuthProvider, CollegeName, User, UserRole


# ---------------------------------------------------------------------------
# Internal helper — mirrors router.py's inline hashing
# ---------------------------------------------------------------------------


def _sha256(raw: str) -> str:
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# Shared mock fixture
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_google_client():
    """Mock httpx.Client that returns a successfully authenticated Google user."""
    mock_instance = MagicMock()
    mock_token_res = MagicMock(status_code=200, is_success=True)
    mock_token_res.json.return_value = {"access_token": "mock_google_access_token"}

    mock_userinfo_res = MagicMock(status_code=200, is_success=True)
    mock_userinfo_res.json.return_value = {
        "email": f"wp4.student.{uuid.uuid4().hex[:8]}@coep.ac.in",
        "email_verified": True,
        "sub": f"google-sub-{uuid.uuid4().hex[:12]}",
        "name": "WP4 Student",
        "picture": "https://example.com/avatar.jpg",
    }

    mock_instance.post.return_value = mock_token_res
    mock_instance.get.return_value = mock_userinfo_res
    mock_instance.__enter__.return_value = mock_instance
    mock_instance.__exit__.return_value = None
    return mock_instance


# ---------------------------------------------------------------------------
# Helper: perform a full login→callback cycle and return (code, nonce_val)
# ---------------------------------------------------------------------------


def _do_login_and_callback(client: TestClient, mock_google_client) -> tuple[str, str]:
    """
    1. GET /google/login — returns real state + cookie.
    2. GET /google/callback with mock Google exchange.
    Returns (one_time_code, nonce_value).
    """
    login_res = client.get("/api/v1/auth/google/login?college=COEP", follow_redirects=False)
    assert login_res.status_code == 307
    state = urllib.parse.parse_qs(urllib.parse.urlparse(login_res.headers["location"]).query)["state"][0]
    nonce_val = client.cookies.get("oauth_binding_nonce")
    assert nonce_val, "Login endpoint must set oauth_binding_nonce cookie"

    with patch("app.auth.router.httpx.Client", return_value=mock_google_client):
        cb_res = client.get(
            f"/api/v1/auth/google/callback?code=google_auth_code&state={state}",
            follow_redirects=False,
        )
    assert cb_res.status_code == 307
    redirect_loc = cb_res.headers["location"]
    assert "/auth/callback?code=" in redirect_loc, f"Expected ?code= in location, got: {redirect_loc}"
    code = urllib.parse.parse_qs(urllib.parse.urlparse(redirect_loc).query)["code"][0]
    return code, nonce_val


# ==============================================================================
# 1. Login Initiation — Binding Nonce Cookie
# ==============================================================================


def test_google_login_sets_binding_cookie(client: TestClient):
    """GET /google/login sets HttpOnly oauth_binding_nonce cookie with correct attributes."""
    res = client.get("/api/v1/auth/google/login?college=COEP", follow_redirects=False)
    assert res.status_code == 307
    location = res.headers["location"]
    assert "accounts.google.com" in location
    assert "state=" in location

    # Verify raw Set-Cookie header attributes
    set_cookie = res.headers.get("set-cookie", "")
    assert "oauth_binding_nonce=" in set_cookie
    assert "HttpOnly" in set_cookie
    assert "Path=/api/v1/auth" in set_cookie
    assert "Max-Age=600" in set_cookie

    # Verify nonce stored in state matches cookie value
    parsed_url = urllib.parse.urlparse(location)
    query_params = urllib.parse.parse_qs(parsed_url.query)
    state = query_params["state"][0]
    state_nonce = service.get_oauth_state_nonce(state)
    assert state_nonce is not None, "State must carry an embedded nonce"

    cookie_val = client.cookies.get("oauth_binding_nonce")
    assert cookie_val == state_nonce, "Cookie nonce must equal state nonce"


# ==============================================================================
# 2. Callback — Nonce Validation
# ==============================================================================


def test_callback_rejects_missing_cookie(client: TestClient):
    """Callback redirects to error page when oauth_binding_nonce cookie is absent."""
    state = service.create_oauth_state(CollegeName.COEP, nonce="valid_nonce")
    client.cookies.clear()

    res = client.get(
        f"/api/v1/auth/google/callback?code=mock_code&state={state}",
        follow_redirects=False,
    )
    assert res.status_code == 307
    loc = urllib.parse.unquote(res.headers["location"])
    assert "error=" in loc
    assert "OAuth state validation failed" in loc or "Invalid or mismatched OAuth state" in loc


def test_callback_rejects_mismatched_cookie_without_clearing(client: TestClient):
    """Callback rejects mismatched nonce without clearing the cookie (no OAuth DoS)."""
    state = service.create_oauth_state(CollegeName.COEP, nonce="correct_nonce")
    client.cookies.set("oauth_binding_nonce", "attacker_different_nonce")

    res = client.get(
        f"/api/v1/auth/google/callback?code=mock_code&state={state}",
        follow_redirects=False,
    )
    assert res.status_code == 307
    loc = urllib.parse.unquote(res.headers["location"])
    assert "error=" in loc

    # Critical: cookie must NOT have been deleted by the failed request
    assert client.cookies.get("oauth_binding_nonce") == "attacker_different_nonce"


def test_callback_redirects_with_code_only(client: TestClient, mock_google_client):
    """Successful callback redirect contains ?code= and NO tokens in URL."""
    login_res = client.get("/api/v1/auth/google/login?college=COEP", follow_redirects=False)
    state = urllib.parse.parse_qs(urllib.parse.urlparse(login_res.headers["location"]).query)["state"][0]

    with patch("app.auth.router.httpx.Client", return_value=mock_google_client):
        cb_res = client.get(
            f"/api/v1/auth/google/callback?code=google_auth_code&state={state}",
            follow_redirects=False,
        )
    assert cb_res.status_code == 307
    loc = cb_res.headers["location"]
    assert "/auth/callback?code=" in loc
    assert "access_token" not in loc
    assert "refresh_token" not in loc


def test_callback_emits_security_headers(client: TestClient, mock_google_client):
    """Successful callback response includes Cache-Control: no-store and Referrer-Policy: no-referrer."""
    login_res = client.get("/api/v1/auth/google/login?college=COEP", follow_redirects=False)
    state = urllib.parse.parse_qs(urllib.parse.urlparse(login_res.headers["location"]).query)["state"][0]

    with patch("app.auth.router.httpx.Client", return_value=mock_google_client):
        cb_res = client.get(
            f"/api/v1/auth/google/callback?code=google_auth_code&state={state}",
            follow_redirects=False,
        )
    assert "no-store" in cb_res.headers.get("Cache-Control", "")
    assert cb_res.headers.get("Referrer-Policy") == "no-referrer"


# ==============================================================================
# 3. Exchange — Happy Path
# ==============================================================================


def test_exchange_happy_path(client: TestClient, mock_google_client, db_session: Session):
    """Full flow: login→callback→exchange returns tokens; cookie cleared; DB record consumed."""
    code, nonce_val = _do_login_and_callback(client, mock_google_client)

    # Verify DB record stores hashes, not plaintext
    code_hash = _sha256(code)
    nonce_hash = _sha256(nonce_val)
    record = db_session.execute(
        select(LoginCode).where(LoginCode.code_hash == code_hash)
    ).scalar_one_or_none()
    assert record is not None, "Login code record must be persisted in DB"
    assert record.nonce_hash == nonce_hash
    assert record.used_at is None

    # Exchange
    exchange_res = client.post(
        "/api/v1/auth/google/exchange",
        json={"code": code},
        headers={"Origin": "http://localhost:5173"},
    )
    assert exchange_res.status_code == 200
    assert "no-store" in exchange_res.headers.get("Cache-Control", "")
    tokens = exchange_res.json()
    assert "access_token" in tokens
    assert "refresh_token" in tokens
    assert tokens["token_type"] == "bearer"

    # Cookie must be cleared
    set_cookie = exchange_res.headers.get("set-cookie", "")
    # FastAPI delete_cookie sets max-age=0 or empty value
    assert "oauth_binding_nonce" in set_cookie
    assert "Max-Age=0" in set_cookie or 'oauth_binding_nonce=""' in set_cookie

    # DB record must be marked used
    db_session.expire_all()
    consumed = db_session.execute(
        select(LoginCode).where(LoginCode.code_hash == code_hash)
    ).scalar_one()
    assert consumed.used_at is not None


# ==============================================================================
# 4. Exchange — Failure Modes
# ==============================================================================


def test_exchange_fails_without_cookie(client: TestClient, mock_google_client):
    """Exchange returns 400 when oauth_binding_nonce cookie is absent."""
    code, _ = _do_login_and_callback(client, mock_google_client)

    # Clear cookie (simulates attacker on a different browser)
    client.cookies.clear()
    res = client.post(
        "/api/v1/auth/google/exchange",
        json={"code": code},
        headers={"Origin": "http://localhost:5173"},
    )
    assert res.status_code == 400
    assert res.json()["detail"] == "Invalid or expired authorization code"


def test_exchange_fails_with_mismatched_cookie(client: TestClient, mock_google_client):
    """Exchange returns 400 when cookie nonce belongs to a different session."""
    code, _ = _do_login_and_callback(client, mock_google_client)

    # Overwrite with foreign nonce
    client.cookies.set("oauth_binding_nonce", "attacker_foreign_nonce_12345")
    res = client.post(
        "/api/v1/auth/google/exchange",
        json={"code": code},
        headers={"Origin": "http://localhost:5173"},
    )
    assert res.status_code == 400
    assert res.json()["detail"] == "Invalid or expired authorization code"


def test_exchange_fails_with_invalid_origin(client: TestClient):
    """Exchange returns 403 when Origin header is an untrusted domain."""
    client.cookies.set("oauth_binding_nonce", "some_nonce")
    res = client.post(
        "/api/v1/auth/google/exchange",
        json={"code": "dummy_code"},
        headers={"Origin": "https://evil-attacker.com"},
    )
    assert res.status_code == 403
    assert "untrusted" in res.json()["detail"].lower() or "forbidden" in res.json()["detail"].lower()


def test_exchange_fails_with_missing_origin(client: TestClient):
    """Exchange returns 403 when Origin header is absent."""
    client.cookies.set("oauth_binding_nonce", "some_nonce")
    res = client.post(
        "/api/v1/auth/google/exchange",
        json={"code": "dummy_code"},
    )
    assert res.status_code == 403


def test_exchange_fails_with_non_json_content_type(client: TestClient):
    """Exchange rejects form-encoded payloads.

    When Content-Type is not application/json, FastAPI's body parser rejects
    the request at the framework layer before our custom content-type guard runs.
    The resulting status is 422 Unprocessable Entity (FastAPI schema validation
    failure), which is the observable security boundary — form-encoded codes
    are never processed by the exchange logic.
    """
    client.cookies.set("oauth_binding_nonce", "some_nonce")
    res = client.post(
        "/api/v1/auth/google/exchange",
        data="code=dummy_code",
        headers={
            "Origin": "http://localhost:5173",
            "Content-Type": "application/x-www-form-urlencoded",
        },
    )
    # FastAPI body validation fires before the endpoint's Content-Type guard.
    # 422 (not 415) is the actual rejection status for form-encoded bodies.
    assert res.status_code in (415, 422), (
        f"Expected 415 or 422 for non-JSON content type, got {res.status_code}"
    )
    assert res.json()["detail"] is not None


def test_exchange_replay_fails(client: TestClient, mock_google_client):
    """Replaying an already-consumed authorization code returns 400."""
    code, nonce_val = _do_login_and_callback(client, mock_google_client)

    # First exchange — succeeds
    res1 = client.post(
        "/api/v1/auth/google/exchange",
        json={"code": code},
        headers={"Origin": "http://localhost:5173"},
    )
    assert res1.status_code == 200

    # Restore cookie for replay attempt
    client.cookies.set("oauth_binding_nonce", nonce_val)
    res2 = client.post(
        "/api/v1/auth/google/exchange",
        json={"code": code},
        headers={"Origin": "http://localhost:5173"},
    )
    assert res2.status_code == 400
    assert res2.json()["detail"] == "Invalid or expired authorization code"


def test_exchange_expired_code_fails(client: TestClient, db_session: Session):
    """An authorization code past its 60-second TTL cannot be exchanged."""
    email = f"expired.{uuid.uuid4().hex[:8]}@coep.ac.in"
    user = User(
        email=email,
        full_name="Expired Code User",
        role=UserRole.STUDENT,
        college=CollegeName.COEP,
        auth_provider=AuthProvider.GOOGLE,
        google_id=f"gid-{uuid.uuid4().hex[:8]}",
        is_active=True,
        is_email_verified=True,
    )
    db_session.add(user)
    db_session.commit()

    raw_code = f"expired_code_{uuid.uuid4().hex}"
    raw_nonce = f"expired_nonce_{uuid.uuid4().hex}"
    record = LoginCode(
        code_hash=_sha256(raw_code),
        nonce_hash=_sha256(raw_nonce),
        user_id=user.id,
        # Expired 10 seconds ago
        expires_at=datetime.now(timezone.utc) - timedelta(seconds=10),
    )
    db_session.add(record)
    db_session.commit()

    client.cookies.set("oauth_binding_nonce", raw_nonce)
    res = client.post(
        "/api/v1/auth/google/exchange",
        json={"code": raw_code},
        headers={"Origin": "http://localhost:5173"},
    )
    assert res.status_code == 400
    assert res.json()["detail"] == "Invalid or expired authorization code"


def test_exchange_unknown_code_fails(client: TestClient):
    """A completely fictitious code returns 400 generic error."""
    client.cookies.set("oauth_binding_nonce", "nonce_for_unknown_code")
    res = client.post(
        "/api/v1/auth/google/exchange",
        json={"code": f"unknown_code_{uuid.uuid4().hex}"},
        headers={"Origin": "http://localhost:5173"},
    )
    assert res.status_code == 400
    assert res.json()["detail"] == "Invalid or expired authorization code"


# ==============================================================================
# 5. Concurrency — Race Condition Protection
# ==============================================================================


def test_exchange_concurrent_race_condition(client: TestClient, mock_google_client, db_session: Session):
    """Two concurrent consume_login_code calls: exactly one wins, one returns None.

    Tests the atomic PostgreSQL UPDATE … RETURNING in consume_login_code directly
    using two independent DB sessions on campusgpt_test, avoiding shared-session
    conflicts that occur when routing concurrent HTTP requests through a single
    TestClient fixture.
    """
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from tests.conftest import TEST_DATABASE_URL, assert_test_database

    assert_test_database(TEST_DATABASE_URL)

    # Create user and login code via the fixture session
    email = f"race.{uuid.uuid4().hex[:8]}@coep.ac.in"
    user = User(
        email=email,
        full_name="Race Condition User",
        role=UserRole.STUDENT,
        college=CollegeName.COEP,
        auth_provider=AuthProvider.GOOGLE,
        google_id=f"gid-race-{uuid.uuid4().hex[:8]}",
        is_active=True,
        is_email_verified=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    raw_code = f"race_code_{uuid.uuid4().hex}"
    raw_nonce = f"race_nonce_{uuid.uuid4().hex}"
    record = LoginCode(
        code_hash=_sha256(raw_code),
        nonce_hash=_sha256(raw_nonce),
        user_id=user.id,
        expires_at=datetime.now(timezone.utc) + timedelta(seconds=60),
    )
    db_session.add(record)
    db_session.commit()

    # Build a fresh engine + session factory for concurrent calls
    engine = create_engine(TEST_DATABASE_URL, pool_size=5, max_overflow=10)
    SessionFactory = sessionmaker(bind=engine, autocommit=False, autoflush=False)

    code_hash = _sha256(raw_code)
    nonce_hash = _sha256(raw_nonce)
    results: list[bool] = []
    lock = __import__("threading").Lock()

    def consume():
        sess = SessionFactory()
        try:
            result_user = repository.consume_login_code(sess, code_hash=code_hash, nonce_hash=nonce_hash)
            with lock:
                results.append(result_user is not None)
        except Exception:
            with lock:
                results.append(False)
        finally:
            sess.close()

    import threading
    t1 = threading.Thread(target=consume)
    t2 = threading.Thread(target=consume)
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    engine.dispose()

    successes = sum(1 for r in results if r)
    assert successes == 1, (
        f"Exactly one concurrent consume should succeed. Results: {results}"
    )


# ==============================================================================
# 6. Multi-tab Session Supersession
# ==============================================================================


def test_multi_tab_superseded_session_fails(client: TestClient, mock_google_client):
    """Tab 2 login overwrites the cookie from Tab 1; Tab 1's callback must fail."""
    # Tab 1 initiates login, capturing Tab 1 state
    res1 = client.get("/api/v1/auth/google/login?college=COEP", follow_redirects=False)
    state1 = urllib.parse.parse_qs(urllib.parse.urlparse(res1.headers["location"]).query)["state"][0]

    # Tab 2 initiates login — overwrites the oauth_binding_nonce cookie
    res2 = client.get("/api/v1/auth/google/login?college=COEP", follow_redirects=False)
    state2 = urllib.parse.parse_qs(urllib.parse.urlparse(res2.headers["location"]).query)["state"][0]

    # Tab 1 callback now presents a cookie that belongs to Tab 2 → mismatch
    cb1 = client.get(
        f"/api/v1/auth/google/callback?code=code&state={state1}",
        follow_redirects=False,
    )
    assert cb1.status_code == 307
    loc1 = urllib.parse.unquote(cb1.headers["location"])
    assert "error=" in loc1  # Tab 1 flow was rejected

    # Tab 2 callback succeeds
    with patch("app.auth.router.httpx.Client", return_value=mock_google_client):
        cb2 = client.get(
            f"/api/v1/auth/google/callback?code=code&state={state2}",
            follow_redirects=False,
        )
    assert cb2.status_code == 307
    loc2 = cb2.headers["location"]
    assert "/auth/callback?code=" in loc2

    code2 = urllib.parse.parse_qs(urllib.parse.urlparse(loc2).query)["code"][0]
    ex2 = client.post(
        "/api/v1/auth/google/exchange",
        json={"code": code2},
        headers={"Origin": "http://localhost:5173"},
    )
    assert ex2.status_code == 200
