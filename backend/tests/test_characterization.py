from unittest.mock import MagicMock, patch
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.auth import service
from app.models.user import CollegeName, User, UserRole


def test_health_endpoint(client: TestClient):
    """Characterization test: GET /health returns ok status without exposing env (sanitized in WP3)."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data == {"status": "ok"}
    assert "env" not in data


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
    test_nonce = "test_nonce_characterization_1234567890123456"
    client.cookies.set("oauth_binding_nonce", test_nonce)
    state = service.create_oauth_state(CollegeName.PICT, nonce=test_nonce)

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
        # Callback creates new Google user - redirects with code, NOT tokens
        res_new = client.get(
            f"/api/v1/auth/google/callback?code=mock_code&state={state}",
            follow_redirects=False,
        )
        assert res_new.status_code == 307
        redirect_url = res_new.headers["location"]
        assert "/auth/callback?code=" in redirect_url
        assert "access_token" not in redirect_url
        assert "refresh_token" not in redirect_url

        # Exchange code for tokens
        code = redirect_url.split("code=")[1]
        exchange_res = client.post(
            "/api/v1/auth/google/exchange",
            json={"code": code},
            headers={"Origin": "http://localhost:5173"},
        )
        assert exchange_res.status_code == 200
        token_data = exchange_res.json()
        assert "access_token" in token_data
        assert "refresh_token" in token_data

        # Callback for existing Google user
        # Re-set cookie since exchange cleared it
        client.cookies.set("oauth_binding_nonce", test_nonce)
        res_existing = client.get(
            f"/api/v1/auth/google/callback?code=mock_code&state={state}",
            follow_redirects=False,
        )
        assert res_existing.status_code == 307
        assert "/auth/callback?code=" in res_existing.headers["location"]
        assert "access_token" not in res_existing.headers["location"]


# ==============================================================================
# Security Defect Verification Tests (Resolved in WP2)
# ==============================================================================


def test_c1_google_user_null_password_bypass(client: TestClient):
    """Defect C1 verification:
    A user created via Google OAuth has hashed_password=None.
    A secure system MUST reject local password login for null-password accounts with 401.
    """
    google_email = "c1.victim@vit.edu"
    test_nonce = "test_nonce_c1_1234567890123456"
    client.cookies.set("oauth_binding_nonce", test_nonce)
    state = service.create_oauth_state(CollegeName.VIT, nonce=test_nonce)

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

    # Attempt to log in with an arbitrary password. Must return 401 Unauthorized.
    response = client.post(
        "/api/v1/auth/login",
        json={"email": google_email, "password": "arbitrary_password", "college": "VIT"},
    )
    assert response.status_code == 401, (
        f"Expected 401 Unauthorized for null-password account, but got {response.status_code}"
    )


def test_c2_five_failed_otp_verification_bypass(client: TestClient):
    """Defect C2 verification:
    When an OTP is guessed incorrectly 5 times, verify_otp locks the code without setting verified_at.
    A secure system MUST refuse registration if OTP was never verified successfully.
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

    # Attempt registration. A secure system must reject this with 400 Bad Request.
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


def test_c3_role_escalation_on_public_register(client: TestClient):
    """Defect C3 verification:
    Public registration endpoint strictly forbids ADMIN self-assignment (returning 422).
    FACULTY requests create a STUDENT account with a PENDING role request.
    """
    admin_attempt_email = "c3.admin.attempt@vit.edu"
    otp = "456789"

    with patch("app.auth.service.generate_otp", return_value=otp):
        client.post(
            "/api/v1/auth/send-otp",
            json={"email": admin_attempt_email, "purpose": "EMAIL_VERIFY", "college": "VIT"},
        )
        client.post(
            "/api/v1/auth/verify-otp",
            json={"email": admin_attempt_email, "otp": otp, "purpose": "EMAIL_VERIFY"},
        )

    # Public request for ADMIN role must be rejected with 422 Unprocessable Entity
    admin_reg_res = client.post(
        "/api/v1/auth/register",
        json={
            "email": admin_attempt_email,
            "password": "Password123!",
            "full_name": "Admin Wannabe",
            "role": "ADMIN",
            "college": "VIT",
        },
    )
    assert admin_reg_res.status_code == 422, (
        f"Expected ADMIN registration to be rejected with 422, but got {admin_reg_res.status_code}"
    )

    # Now verify FACULTY request creates STUDENT with PENDING role_request
    faculty_attempt_email = "c3.faculty.applicant@vit.edu"
    with patch("app.auth.service.generate_otp", return_value=otp):
        client.post(
            "/api/v1/auth/send-otp",
            json={"email": faculty_attempt_email, "purpose": "EMAIL_VERIFY", "college": "VIT"},
        )
        client.post(
            "/api/v1/auth/verify-otp",
            json={"email": faculty_attempt_email, "otp": otp, "purpose": "EMAIL_VERIFY"},
        )

    faculty_reg_res = client.post(
        "/api/v1/auth/register",
        json={
            "email": faculty_attempt_email,
            "password": "Password123!",
            "full_name": "Faculty Applicant",
            "role": "FACULTY",
            "college": "VIT",
        },
    )
    assert faculty_reg_res.status_code == 201
    user_data = faculty_reg_res.json()
    assert user_data["role"] == "STUDENT", "User role must be STUDENT upon initial registration"
    assert user_data["pending_role_request"] is not None, "A pending role request must be attached"
    assert user_data["pending_role_request"]["requested_role"] == "FACULTY"
    assert user_data["pending_role_request"]["status"] == "PENDING"
