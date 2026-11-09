from unittest.mock import MagicMock, patch
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.auth import service
from app.models.user import CollegeName, User, UserRole


def test_health_endpoint(client: TestClient):
    """Characterization test: GET /health returns ok status."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "env" in data


def test_register_verify_login_happy_path(client: TestClient):
    """Characterization test: Full local authentication happy path."""
    email = "test.student@vit.edu"
    fixed_otp = "654321"

    with patch("app.auth.service.generate_otp", return_value=fixed_otp):
        # 1. Send OTP
        send_res = client.post(
            "/api/v1/auth/send-otp",
            json={"email": email, "purpose": "EMAIL_VERIFY", "college": "VIT"},
        )
        assert send_res.status_code == 200
        assert send_res.json()["message"] == "Verification code sent"

        # 2. Verify OTP
        verify_res = client.post(
            "/api/v1/auth/verify-otp",
            json={"email": email, "otp": fixed_otp, "purpose": "EMAIL_VERIFY"},
        )
        assert verify_res.status_code == 200
        assert verify_res.json()["message"] == "Code verified"

        # 3. Register
        reg_res = client.post(
            "/api/v1/auth/register",
            json={
                "email": email,
                "password": "ValidPassword123!",
                "full_name": "Test Student",
                "college": "VIT",
            },
        )
        assert reg_res.status_code == 201
        reg_data = reg_res.json()
        assert reg_data["email"] == email
        assert reg_data["is_email_verified"] is True

        # 4. Login
        login_res = client.post(
            "/api/v1/auth/login",
            json={"email": email, "password": "ValidPassword123!", "college": "VIT"},
        )
        assert login_res.status_code == 200
        login_data = login_res.json()
        assert "access_token" in login_data
        assert "refresh_token" in login_data
        assert login_data["user"]["email"] == email


def test_me_and_refresh_endpoints(client: TestClient):
    """Characterization test: /me identity inspection and /refresh token renewal."""
    email = "vit.user@vit.edu"
    fixed_otp = "112233"

    with patch("app.auth.service.generate_otp", return_value=fixed_otp):
        client.post(
            "/api/v1/auth/send-otp",
            json={"email": email, "purpose": "EMAIL_VERIFY", "college": "VIT"},
        )
        client.post(
            "/api/v1/auth/verify-otp",
            json={"email": email, "otp": fixed_otp, "purpose": "EMAIL_VERIFY"},
        )
        client.post(
            "/api/v1/auth/register",
            json={
                "email": email,
                "password": "Password123!",
                "full_name": "VIT User",
                "college": "VIT",
            },
        )

    login_res = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "Password123!", "college": "VIT"},
    )
    tokens = login_res.json()
    access_token = tokens["access_token"]
    refresh_token = tokens["refresh_token"]

    # Test /me
    me_res = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert me_res.status_code == 200
    assert me_res.json()["email"] == email

    # Test /refresh
    refresh_res = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert refresh_res.status_code == 200
    new_token_data = refresh_res.json()
    assert "access_token" in new_token_data
    assert new_token_data["token_type"] == "bearer"


def test_forgot_and_reset_password(client: TestClient):
    """Characterization test: Forgot password code issuance and password reset."""
    email = "reset.student@coep.ac.in"
    fixed_otp = "998877"

    # Setup user
    with patch("app.auth.service.generate_otp", return_value="123456"):
        client.post(
            "/api/v1/auth/send-otp",
            json={"email": email, "purpose": "EMAIL_VERIFY", "college": "COEP"},
        )
        client.post(
            "/api/v1/auth/verify-otp",
            json={"email": email, "otp": "123456", "purpose": "EMAIL_VERIFY"},
        )
        client.post(
            "/api/v1/auth/register",
            json={
                "email": email,
                "password": "InitialPassword1!",
                "full_name": "Reset Student",
                "college": "COEP",
            },
        )

    with patch("app.auth.service.generate_otp", return_value=fixed_otp):
        forgot_res = client.post(
            "/api/v1/auth/forgot-password",
            json={"email": email},
        )
        assert forgot_res.status_code == 200

        reset_res = client.post(
            "/api/v1/auth/reset-password",
            json={
                "email": email,
                "otp": fixed_otp,
                "new_password": "NewValidPassword2!",
            },
        )
        assert reset_res.status_code == 200
        assert reset_res.json()["message"] == "Password updated"

    # Verify old password fails and new password works
    old_login = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "InitialPassword1!", "college": "COEP"},
    )
    assert old_login.status_code == 401

    new_login = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "NewValidPassword2!", "college": "COEP"},
    )
    assert new_login.status_code == 200


def test_google_oauth_callback_new_and_existing_user(client: TestClient):
    """Characterization test: Google OAuth callback code exchange with mocked Google API."""
    google_email = "scholar@pict.edu"
    state = service.create_oauth_state(CollegeName.PICT)

    mock_client_instance = MagicMock()
    mock_token_res = MagicMock(status_code=200, is_success=True)
    mock_token_res.json.return_value = {"access_token": "mock_google_token"}

    mock_userinfo_res = MagicMock(status_code=200, is_success=True)
    mock_userinfo_res.json.return_value = {
        "email": google_email,
        "email_verified": True,
        "sub": "google-sub-123456",
        "name": "PICT Scholar",
        "picture": "https://example.com/avatar.jpg",
    }

    mock_client_instance.post.return_value = mock_token_res
    mock_client_instance.get.return_value = mock_userinfo_res
    mock_client_instance.__enter__.return_value = mock_client_instance
    mock_client_instance.__exit__.return_value = None

    with patch("app.auth.router.httpx.Client", return_value=mock_client_instance):
        # Callback creates new Google user
        res_new = client.get(
            f"/api/v1/auth/google/callback?code=mock_code&state={state}",
            follow_redirects=False,
        )
        assert res_new.status_code == 307
        redirect_url = res_new.headers["location"]
        assert "/auth/callback?access_token=" in redirect_url
        assert "refresh_token=" in redirect_url

        # Callback for existing Google user
        res_existing = client.get(
            f"/api/v1/auth/google/callback?code=mock_code&state={state}",
            follow_redirects=False,
        )
        assert res_existing.status_code == 307


# ==============================================================================
# Known Defects (Marked xfail(strict=True) per WP0 requirements)
# ==============================================================================


@pytest.mark.xfail(
    strict=True,
    reason="Defect C1: Google users with null password hash bypass auth and can log in with any password",
)
def test_c1_google_user_null_password_bypass(client: TestClient):
    """Defect C1 characterization:
    A user created via Google OAuth has hashed_password=None.
    A secure system MUST reject local password login for null-password accounts.
    Under current defective code, authenticate_user allows any password, returning 200.
    Asserting 401 Unauthorized fails on current code, confirming defect C1.
    """
    google_email = "c1.victim@vit.edu"
    state = service.create_oauth_state(CollegeName.VIT)

    mock_client_instance = MagicMock()
    mock_token_res = MagicMock(status_code=200, is_success=True)
    mock_token_res.json.return_value = {"access_token": "token"}
    mock_userinfo_res = MagicMock(status_code=200, is_success=True)
    mock_userinfo_res.json.return_value = {
        "email": google_email,
        "email_verified": True,
        "sub": "sub-c1",
        "name": "Victim",
    }
    mock_client_instance.post.return_value = mock_token_res
    mock_client_instance.get.return_value = mock_userinfo_res
    mock_client_instance.__enter__.return_value = mock_client_instance
    mock_client_instance.__exit__.return_value = None

    with patch("app.auth.router.httpx.Client", return_value=mock_client_instance):
        client.get(
            f"/api/v1/auth/google/callback?code=code&state={state}",
            follow_redirects=False,
        )

    # Attempt to log in with an arbitrary password.
    # In secure code, this MUST return 401. Current code returns 200.
    response = client.post(
        "/api/v1/auth/login",
        json={"email": google_email, "password": "arbitrary_password", "college": "VIT"},
    )
    assert response.status_code == 401, (
        f"Expected 401 Unauthorized for null-password account, but got {response.status_code}"
    )


@pytest.mark.xfail(
    strict=True,
    reason="Defect C2: 5 failed OTP attempts mark is_used=True and permit email verification bypass",
)
def test_c2_five_failed_otp_verification_bypass(client: TestClient):
    """Defect C2 characterization:
    When an OTP is guessed incorrectly 5 times, verify_otp sets record.is_used = True.
    has_recent_used_email_otp mistakenly treats is_used=True as 'verified'.
    A secure system MUST refuse registration if OTP was never guessed correctly.
    Under current defective code, registration succeeds with 201 Created.
    Asserting 400 Bad Request fails on current code, confirming defect C2.
    """
    email = "c2.attacker@vit.edu"
    real_otp = "123456"

    with patch("app.auth.service.generate_otp", return_value=real_otp):
        client.post(
            "/api/v1/auth/send-otp",
            json={"email": email, "purpose": "EMAIL_VERIFY", "college": "VIT"},
        )

    # 5 wrong attempts to trigger lock
    for _ in range(5):
        client.post(
            "/api/v1/auth/verify-otp",
            json={"email": email, "otp": "000000", "purpose": "EMAIL_VERIFY"},
        )

    # Attempt registration. A secure system must reject this.
    reg_response = client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "Password123!",
            "full_name": "Attacker",
            "college": "VIT",
        },
    )
    assert reg_response.status_code == 400, (
        f"Expected registration to be rejected with 400, but got {reg_response.status_code}"
    )


@pytest.mark.xfail(
    strict=True,
    reason="Defect C3: Public registration allows client self-assignment of ADMIN/FACULTY role",
)
def test_c3_role_escalation_on_public_register(client: TestClient):
    """Defect C3 characterization:
    Public registration endpoint accepts role from client payload.
    A secure system MUST ignore client-supplied privileged roles or reject the request.
    Under current defective code, the user is created directly with role ADMIN.
    Asserting that role is downgraded to STUDENT (or rejected) fails on current code, confirming C3.
    """
    email = "c3.escalated@vit.edu"
    otp = "456789"

    with patch("app.auth.service.generate_otp", return_value=otp):
        client.post(
            "/api/v1/auth/send-otp",
            json={"email": email, "purpose": "EMAIL_VERIFY", "college": "VIT"},
        )
        client.post(
            "/api/v1/auth/verify-otp",
            json={"email": email, "otp": otp, "purpose": "EMAIL_VERIFY"},
        )

    reg_response = client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "Password123!",
            "full_name": "Privilege Escalator",
            "role": "ADMIN",
            "college": "VIT",
        },
    )
    assert reg_response.status_code == 201
    user_data = reg_response.json()
    assert user_data["role"] == "STUDENT", (
        f"Expected role to be restricted to STUDENT, but was granted {user_data['role']}"
    )
