from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch
import urllib.parse
import uuid
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth import repository, service
from app.auth.service import DUMMY_BCRYPT_HASH
from app.database.session import SessionLocal
from app.models.otp_verification import OtpPurpose, OtpVerification
from app.models.role_request import RoleRequest, RoleRequestStatus
from app.models.user import AuthProvider, CollegeName, User, UserRole


# ==============================================================================
# Helper Fixtures & Setup
# ==============================================================================


@pytest.fixture
def admin_user(db_session: Session) -> User:
    """Fixture providing a verified admin user."""
    email = f"admin.{uuid.uuid4().hex[:8]}@campusgpt.dev"
    admin = User(
        email=email,
        hashed_password=service.hash_password("AdminSecurePassword123!"),
        full_name="System Admin",
        role=UserRole.ADMIN,
        college=None,
        auth_provider=AuthProvider.LOCAL,
        is_active=True,
        is_email_verified=True,
    )
    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)
    return admin


@pytest.fixture
def admin_token(admin_user: User) -> str:
    """Fixture providing an access token for the admin user."""
    return service.create_access_token(admin_user)


# ==============================================================================
# 1. Defect C1: Passwordless Google Account Protection & Timing Equalization
# ==============================================================================


def test_dummy_bcrypt_hash_validity():
    """Verify that DUMMY_BCRYPT_HASH is a valid bcrypt hash and executes correctly."""
    assert DUMMY_BCRYPT_HASH.startswith("$2b$") or DUMMY_BCRYPT_HASH.startswith("$2a$")
    # Verify against wrong password returns False without error
    result = service.verify_password("wrong_password", DUMMY_BCRYPT_HASH)
    assert result is False


def test_c1_null_password_user_cannot_login(client: TestClient, db_session: Session):
    """Ensure an account with hashed_password=None cannot log in with any password."""
    email = f"c1.google.{uuid.uuid4().hex[:8]}@vit.edu"
    user = User(
        email=email,
        hashed_password=None,
        full_name="Google Only User",
        role=UserRole.STUDENT,
        college=CollegeName.VIT,
        auth_provider=AuthProvider.GOOGLE,
        google_id=f"gid-{uuid.uuid4().hex}",
        is_active=True,
        is_email_verified=True,
    )
    db_session.add(user)
    db_session.commit()

    # Attempt password login
    res = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "AnyPassword123!", "college": "VIT"},
    )
    assert res.status_code == 401
    assert res.json()["detail"] == "Invalid email or password"


def test_c1_verified_local_user_can_login(client: TestClient, db_session: Session):
    """Ensure a normal local user with valid password can log in successfully."""
    email = f"c1.local.{uuid.uuid4().hex[:8]}@vit.edu"
    password = "CorrectPassword123!"
    user = User(
        email=email,
        hashed_password=service.hash_password(password),
        full_name="Local User",
        role=UserRole.STUDENT,
        college=CollegeName.VIT,
        auth_provider=AuthProvider.LOCAL,
        is_active=True,
        is_email_verified=True,
    )
    db_session.add(user)
    db_session.commit()

    res = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password, "college": "VIT"},
    )
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["user"]["email"] == email


# ==============================================================================
# 2. Defect C2: OTP Lockout Bypass Defense & Institutional Domain Checks
# ==============================================================================


def test_c2_otp_lockout_prevents_registration(client: TestClient):
    """5 failed OTP guesses lock the OTP; registration without valid verified_at fails."""
    email = f"c2.lockout.{uuid.uuid4().hex[:8]}@coep.ac.in"
    otp = "654321"

    with patch("app.auth.service.generate_otp", return_value=otp):
        client.post(
            "/api/v1/auth/send-otp",
            json={"email": email, "purpose": "EMAIL_VERIFY", "college": "COEP"},
        )

    # 5 wrong attempts
    for _ in range(5):
        client.post(
            "/api/v1/auth/verify-otp",
            json={"email": email, "otp": "000000", "purpose": "EMAIL_VERIFY"},
        )

    # Attempt registration: must be rejected with 400
    res = client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "Password123!",
            "full_name": "Lockout Victim",
            "college": "COEP",
        },
    )
    assert res.status_code == 400
    assert "verify your email" in res.json()["detail"].lower()


def test_c2_successful_otp_allows_registration(client: TestClient):
    """Correct OTP sets verified_at and allows registration."""
    email = f"c2.success.{uuid.uuid4().hex[:8]}@pict.edu"
    otp = "123456"

    with patch("app.auth.service.generate_otp", return_value=otp):
        client.post(
            "/api/v1/auth/send-otp",
            json={"email": email, "purpose": "EMAIL_VERIFY", "college": "PICT"},
        )
        verify_res = client.post(
            "/api/v1/auth/verify-otp",
            json={"email": email, "otp": otp, "purpose": "EMAIL_VERIFY"},
        )
        assert verify_res.status_code == 200

    reg_res = client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "Password123!",
            "full_name": "Verified User",
            "college": "PICT",
        },
    )
    assert reg_res.status_code == 201
    assert reg_res.json()["is_email_verified"] is True


def test_c2_expired_verification_window_fails(client: TestClient, db_session: Session):
    """An OTP verified > 15 minutes ago cannot be used to register."""
    email = f"c2.expired.{uuid.uuid4().hex[:8]}@vit.edu"
    otp = "111222"

    with patch("app.auth.service.generate_otp", return_value=otp):
        client.post(
            "/api/v1/auth/send-otp",
            json={"email": email, "purpose": "EMAIL_VERIFY", "college": "VIT"},
        )
        client.post(
            "/api/v1/auth/verify-otp",
            json={"email": email, "otp": otp, "purpose": "EMAIL_VERIFY"},
        )

    # Manually age verified_at by 20 minutes
    record = db_session.scalar(
        select(OtpVerification).where(OtpVerification.email == email)
    )
    assert record is not None
    record.verified_at = datetime.now(timezone.utc) - timedelta(minutes=20)
    db_session.commit()

    reg_res = client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "Password123!",
            "full_name": "Expired User",
            "college": "VIT",
        },
    )
    assert reg_res.status_code == 400
    assert "verify your email" in reg_res.json()["detail"].lower()


def test_c2_unrecognized_domain_rejected(client: TestClient):
    """An email with non-institutional domain is rejected on send-otp with 400."""
    res = client.post(
        "/api/v1/auth/send-otp",
        json={"email": "attacker@gmail.com", "purpose": "EMAIL_VERIFY"},
    )
    assert res.status_code == 400
    assert "domain is not associated" in res.json()["detail"].lower()


def test_c2_email_provider_failure_returns_503(client: TestClient):
    """When the email sending service raises an error, send-otp returns 503."""
    email = f"c2.provider.error.{uuid.uuid4().hex[:8]}@vit.edu"
    with patch("app.auth.service.send_email", side_effect=RuntimeError("Resend API down")):
        res = client.post(
            "/api/v1/auth/send-otp",
            json={"email": email, "purpose": "EMAIL_VERIFY", "college": "VIT"},
        )
        assert res.status_code == 503
        assert "temporarily unavailable" in res.json()["detail"].lower()


# ==============================================================================
# 3. Defect C3: Role Escalation Defense & Role Requests Lifecycle
# ==============================================================================


def test_c3_public_admin_registration_rejected(client: TestClient):
    """Registration with role=ADMIN returns HTTP 422 Unprocessable Entity."""
    email = f"c3.admin.{uuid.uuid4().hex[:8]}@vit.edu"
    otp = "888999"

    with patch("app.auth.service.generate_otp", return_value=otp):
        client.post(
            "/api/v1/auth/send-otp",
            json={"email": email, "purpose": "EMAIL_VERIFY", "college": "VIT"},
        )
        client.post(
            "/api/v1/auth/verify-otp",
            json={"email": email, "otp": otp, "purpose": "EMAIL_VERIFY"},
        )

    res = client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "Password123!",
            "full_name": "Admin Escalation",
            "role": "ADMIN",
            "college": "VIT",
        },
    )
    assert res.status_code == 422


def test_c3_faculty_registration_creates_student_and_pending_request(
    client: TestClient, admin_token: str
):
    """Registering as FACULTY creates a STUDENT account with a PENDING role request."""
    email = f"c3.faculty.{uuid.uuid4().hex[:8]}@vit.edu"
    otp = "333444"

    with patch("app.auth.service.generate_otp", return_value=otp):
        client.post(
            "/api/v1/auth/send-otp",
            json={"email": email, "purpose": "EMAIL_VERIFY", "college": "VIT"},
        )
        client.post(
            "/api/v1/auth/verify-otp",
            json={"email": email, "otp": otp, "purpose": "EMAIL_VERIFY"},
        )

    reg_res = client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "Password123!",
            "full_name": "Faculty Applicant",
            "role": "FACULTY",
            "college": "VIT",
        },
    )
    assert reg_res.status_code == 201
    user_data = reg_res.json()
    assert user_data["role"] == "STUDENT"
    assert user_data["pending_role_request"] is not None
    req_id = user_data["pending_role_request"]["id"]

    # Student cannot access admin endpoints
    login_res = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "Password123!", "college": "VIT"},
    )
    student_token = login_res.json()["access_token"]

    admin_probe = client.get(
        "/api/v1/admin/role-requests",
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert admin_probe.status_code == 403

    # Admin can list role requests and see the pending request
    admin_list = client.get(
        "/api/v1/admin/role-requests?status=PENDING",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert admin_list.status_code == 200
    items = admin_list.json()
    matching = [i for i in items if i["id"] == req_id]
    assert len(matching) == 1
    assert matching[0]["applicant_email"] == email

    # Admin approves the role request
    approve_res = client.post(
        f"/api/v1/admin/role-requests/{req_id}/approve",
        json={"note": "Verified faculty credentials"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert approve_res.status_code == 200
    assert approve_res.json()["status"] == "APPROVED"

    # Subsequent approve/reject returns 409 Conflict
    re_approve = client.post(
        f"/api/v1/admin/role-requests/{req_id}/approve",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert re_approve.status_code == 409

    # The user's role in database is now FACULTY
    me_res = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert me_res.status_code == 200
    assert me_res.json()["role"] == "FACULTY"


def test_c3_admin_rejects_role_request(client: TestClient, admin_token: str):
    """Admin rejects a pending role request; user role remains STUDENT."""
    email = f"c3.reject.{uuid.uuid4().hex[:8]}@coep.ac.in"
    otp = "555666"

    with patch("app.auth.service.generate_otp", return_value=otp):
        client.post(
            "/api/v1/auth/send-otp",
            json={"email": email, "purpose": "EMAIL_VERIFY", "college": "COEP"},
        )
        client.post(
            "/api/v1/auth/verify-otp",
            json={"email": email, "otp": otp, "purpose": "EMAIL_VERIFY"},
        )

    reg_res = client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "Password123!",
            "full_name": "Rejected Applicant",
            "role": "FACULTY",
            "college": "COEP",
        },
    )
    req_id = reg_res.json()["pending_role_request"]["id"]

    # Reject request
    reject_res = client.post(
        f"/api/v1/admin/role-requests/{req_id}/reject",
        json={"note": "Invalid faculty affiliation"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert reject_res.status_code == 200
    assert reject_res.json()["status"] == "REJECTED"

    # User remains STUDENT
    login_res = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "Password123!", "college": "COEP"},
    )
    student_token = login_res.json()["access_token"]
    me_res = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert me_res.json()["role"] == "STUDENT"


def test_c3_admin_self_approval_forbidden(
    client: TestClient, admin_user: User, admin_token: str, db_session: Session
):
    """An admin cannot approve their own role request."""
    # Create a role request for the admin
    req = RoleRequest(
        user_id=admin_user.id,
        applicant_email=admin_user.email,
        requested_role=UserRole.FACULTY,
        status=RoleRequestStatus.PENDING,
    )
    db_session.add(req)
    db_session.commit()
    db_session.refresh(req)

    res = client.post(
        f"/api/v1/admin/role-requests/{req.id}/approve",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert res.status_code == 400
    assert "own role request" in res.json()["detail"].lower()


# ==============================================================================
# 4. User Enumeration Protection
# ==============================================================================


def test_enumeration_protection_login(client: TestClient, db_session: Session):
    """Login with wrong password for existing vs non-existing user returns identical 401."""
    existing_email = f"enum.exists.{uuid.uuid4().hex[:8]}@vit.edu"
    user = User(
        email=existing_email,
        hashed_password=service.hash_password("RealPassword123!"),
        full_name="Enum Target",
        role=UserRole.STUDENT,
        college=CollegeName.VIT,
        auth_provider=AuthProvider.LOCAL,
        is_active=True,
        is_email_verified=True,
    )
    db_session.add(user)
    db_session.commit()

    non_existing_email = f"enum.notfound.{uuid.uuid4().hex[:8]}@vit.edu"

    res_exist = client.post(
        "/api/v1/auth/login",
        json={"email": existing_email, "password": "WrongPassword1!", "college": "VIT"},
    )
    res_nonexist = client.post(
        "/api/v1/auth/login",
        json={"email": non_existing_email, "password": "WrongPassword1!", "college": "VIT"},
    )

    assert res_exist.status_code == 401
    assert res_nonexist.status_code == 401
    assert res_exist.json() == res_nonexist.json()


def test_enumeration_protection_forgot_password(client: TestClient, db_session: Session):
    """Forgot password returns identical 200 message for existing and non-existing email."""
    existing_email = f"enum.forgot.exist.{uuid.uuid4().hex[:8]}@pict.edu"
    user = User(
        email=existing_email,
        hashed_password=service.hash_password("RealPassword123!"),
        full_name="Forgot Target",
        role=UserRole.STUDENT,
        college=CollegeName.PICT,
        auth_provider=AuthProvider.LOCAL,
        is_active=True,
        is_email_verified=True,
    )
    db_session.add(user)
    db_session.commit()

    non_existing_email = f"enum.forgot.notfound.{uuid.uuid4().hex[:8]}@pict.edu"

    with patch("app.auth.service.send_email"):
        res_exist = client.post("/api/v1/auth/forgot-password", json={"email": existing_email})
        res_nonexist = client.post("/api/v1/auth/forgot-password", json={"email": non_existing_email})

    assert res_exist.status_code == 200
    assert res_nonexist.status_code == 200
    assert res_exist.json() == res_nonexist.json()
    assert "If an account with this email exists" in res_exist.json()["message"]


def test_enumeration_protection_send_otp_existing_verified(client: TestClient, db_session: Session):
    """send-otp returns generic success without generating a new OTP if account is already verified."""
    verified_email = f"enum.verified.{uuid.uuid4().hex[:8]}@coep.ac.in"
    user = User(
        email=verified_email,
        hashed_password=service.hash_password("RealPassword123!"),
        full_name="Already Verified",
        role=UserRole.STUDENT,
        college=CollegeName.COEP,
        auth_provider=AuthProvider.LOCAL,
        is_active=True,
        is_email_verified=True,
    )
    db_session.add(user)
    db_session.commit()

    with patch("app.auth.service.send_email") as mock_send:
        res = client.post(
            "/api/v1/auth/send-otp",
            json={"email": verified_email, "purpose": "EMAIL_VERIFY", "college": "COEP"},
        )
        assert res.status_code == 200
        assert res.json()["message"] == "Verification code sent"
        # Email sender should NOT be called for already-verified account
        mock_send.assert_not_called()


# ==============================================================================
# 5. Account Linking and Google Identity Hardening
# ==============================================================================


def test_google_login_rejects_unverified_local_account(client: TestClient, db_session: Session):
    """Google OAuth callback refuses to link to an unverified local account (pre-reg takeover defense)."""
    email = f"unverified.local.{uuid.uuid4().hex[:8]}@vit.edu"
    user = User(
        email=email,
        hashed_password=service.hash_password("LocalPass123!"),
        full_name="Unverified Target",
        role=UserRole.STUDENT,
        college=CollegeName.VIT,
        auth_provider=AuthProvider.LOCAL,
        is_active=True,
        is_email_verified=False,  # Unverified!
    )
    db_session.add(user)
    db_session.commit()

    state = service.create_oauth_state(CollegeName.VIT)

    mock_client_instance = MagicMock()
    mock_token_res = MagicMock(status_code=200, is_success=True)
    mock_token_res.json.return_value = {"access_token": "mock_token"}
    mock_userinfo_res = MagicMock(status_code=200, is_success=True)
    mock_userinfo_res.json.return_value = {
        "email": email,
        "email_verified": True,
        "sub": "attacker-google-sub",
        "name": "Attacker Name",
    }
    mock_client_instance.post.return_value = mock_token_res
    mock_client_instance.get.return_value = mock_userinfo_res
    mock_client_instance.__enter__.return_value = mock_client_instance
    mock_client_instance.__exit__.return_value = None

    with patch("app.auth.router.httpx.Client", return_value=mock_client_instance):
        res = client.get(
            f"/api/v1/auth/google/callback?code=code&state={state}",
            follow_redirects=False,
        )
        assert res.status_code == 307
        redirect_url = res.headers["location"]
        assert "Cannot link Google account to an unverified local account." in urllib.parse.unquote(redirect_url)


def test_google_login_links_verified_local_account(client: TestClient, db_session: Session):
    """Google OAuth callback links to an existing verified local account."""
    email = f"verified.local.{uuid.uuid4().hex[:8]}@vit.edu"
    google_sub = f"google-sub-{uuid.uuid4().hex[:8]}"
    user = User(
        email=email,
        hashed_password=service.hash_password("LocalPass123!"),
        full_name="Verified Target",
        role=UserRole.STUDENT,
        college=CollegeName.VIT,
        auth_provider=AuthProvider.LOCAL,
        google_id=None,
        is_active=True,
        is_email_verified=True,  # Verified!
    )
    db_session.add(user)
    db_session.commit()

    state = service.create_oauth_state(CollegeName.VIT)

    mock_client_instance = MagicMock()
    mock_token_res = MagicMock(status_code=200, is_success=True)
    mock_token_res.json.return_value = {"access_token": "mock_token"}
    mock_userinfo_res = MagicMock(status_code=200, is_success=True)
    mock_userinfo_res.json.return_value = {
        "email": email,
        "email_verified": True,
        "sub": google_sub,
        "name": "Verified Target",
    }
    mock_client_instance.post.return_value = mock_token_res
    mock_client_instance.get.return_value = mock_userinfo_res
    mock_client_instance.__enter__.return_value = mock_client_instance
    mock_client_instance.__exit__.return_value = None

    with patch("app.auth.router.httpx.Client", return_value=mock_client_instance):
        res = client.get(
            f"/api/v1/auth/google/callback?code=code&state={state}",
            follow_redirects=False,
        )
        assert res.status_code == 307
        redirect_url = res.headers["location"]
        assert "/auth/callback?access_token=" in redirect_url

    # Check that google_id was linked in the database
    db_session.refresh(user)
    assert user.google_id == google_sub


# ==============================================================================
# 6. CLI Role Requests Management Test
# ==============================================================================


def test_manage_role_requests_cli(capsys, db_session: Session, admin_user: User):
    """Test CLI commands for listing, approving, and rejecting role requests."""
    from app.manage_role_requests import list_requests, review_request

    # Create test pending request
    test_email = f"cli.applicant.{uuid.uuid4().hex[:8]}@vit.edu"
    test_user = User(
        email=test_email,
        hashed_password=service.hash_password("Pass123!"),
        full_name="CLI Applicant",
        role=UserRole.STUDENT,
        college=CollegeName.VIT,
        auth_provider=AuthProvider.LOCAL,
        is_active=True,
        is_email_verified=True,
    )
    db_session.add(test_user)
    db_session.commit()
    db_session.refresh(test_user)

    req = RoleRequest(
        user_id=test_user.id,
        applicant_email=test_email,
        requested_role=UserRole.FACULTY,
        status=RoleRequestStatus.PENDING,
    )
    db_session.add(req)
    db_session.commit()
    db_session.refresh(req)

    # Test list
    list_requests("PENDING", db=db_session)
    captured = capsys.readouterr()
    assert test_email in captured.out

    # Test approve via CLI
    review_request(str(req.id), "approve", "Approved via CLI test", admin_user.email, db=db_session)
    captured = capsys.readouterr()
    assert "Successfully approved role request" in captured.out

    db_session.refresh(req)
    assert req.status == RoleRequestStatus.APPROVED
    db_session.refresh(test_user)
    assert test_user.role == UserRole.FACULTY

