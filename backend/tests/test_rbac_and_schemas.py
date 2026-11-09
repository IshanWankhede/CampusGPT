"""WP9 RBAC Authorization Matrix and Response Schema Tests.

Covers:
1. 401 Unauthorized for unauthenticated requests to protected endpoints.
2. 403 Forbidden for unauthorized roles (STUDENT / FACULTY accessing ADMIN endpoints).
3. 404 Not Found for non-existent entities (role request review).
4. 409 Conflict for invalid entity state transitions (reviewing already reviewed requests).
5. Full HTTP role-request approval lifecycle:
   - Admin approves -> applicant promoted to FACULTY, reviewer metadata populated.
   - Admin rejects -> applicant remains STUDENT, reviewer metadata populated.
6. Response schema validation:
   - /api/v1/auth/me matches UserResponse schema.
   - /api/v1/auth/login matches TokenResponse schema.
   - /api/v1/admin/role-requests matches RoleRequestResponse schema.
"""

import uuid
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.auth import service
from app.auth.schemas import RoleRequestResponse, TokenResponse, UserResponse
from app.models.role_request import RoleRequest, RoleRequestStatus
from app.models.user import AuthProvider, CollegeName, User, UserRole


# ==============================================================================
# 1. 401 Unauthorized Matrix (Unauthenticated Requests)
# ==============================================================================


def test_unauthenticated_requests_return_401(client: TestClient):
    """Verifies that all protected endpoints return 401 when no token is supplied."""
    random_id = uuid.uuid4()
    protected_endpoints = [
        ("GET", "/api/v1/auth/me"),
        ("GET", "/api/v1/auth/admin-test"),
        ("GET", "/api/v1/admin/role-requests"),
        ("POST", f"/api/v1/admin/role-requests/{random_id}/approve"),
        ("POST", f"/api/v1/admin/role-requests/{random_id}/reject"),
        ("POST", "/api/v1/auth/logout-all"),
    ]

    for method, path in protected_endpoints:
        if method == "GET":
            res = client.get(path)
        else:
            res = client.post(path)
        assert res.status_code == 401, f"Expected 401 for {method} {path}, got {res.status_code}: {res.text}"


def test_unauthenticated_logout_is_graceful(client: TestClient):
    """Verifies that POST /api/v1/auth/logout returns 204 even without credentials for client safety."""
    res = client.post("/api/v1/auth/logout")
    assert res.status_code == 204


# ==============================================================================
# 2. 403 Forbidden Matrix (Role Enforcement)
# ==============================================================================


def test_student_forbidden_from_admin_endpoints(client: TestClient, rbac_student_token: str):
    """Verifies that a STUDENT user receives 403 on all admin endpoints."""
    headers = {"Authorization": f"Bearer {rbac_student_token}"}
    random_id = uuid.uuid4()

    assert client.get("/api/v1/auth/admin-test", headers=headers).status_code == 403
    assert client.get("/api/v1/admin/role-requests", headers=headers).status_code == 403
    assert client.post(f"/api/v1/admin/role-requests/{random_id}/approve", headers=headers).status_code == 403
    assert client.post(f"/api/v1/admin/role-requests/{random_id}/reject", headers=headers).status_code == 403


def test_faculty_forbidden_from_admin_endpoints(client: TestClient, rbac_faculty_token: str):
    """Verifies that a FACULTY user receives 403 on all admin endpoints."""
    headers = {"Authorization": f"Bearer {rbac_faculty_token}"}
    random_id = uuid.uuid4()

    assert client.get("/api/v1/auth/admin-test", headers=headers).status_code == 403
    assert client.get("/api/v1/admin/role-requests", headers=headers).status_code == 403
    assert client.post(f"/api/v1/admin/role-requests/{random_id}/approve", headers=headers).status_code == 403
    assert client.post(f"/api/v1/admin/role-requests/{random_id}/reject", headers=headers).status_code == 403


def test_admin_permitted_on_admin_endpoints(client: TestClient, rbac_admin_token: str):
    """Verifies that an ADMIN user is successfully authorized on admin endpoints."""
    headers = {"Authorization": f"Bearer {rbac_admin_token}"}

    res_test = client.get("/api/v1/auth/admin-test", headers=headers)
    assert res_test.status_code == 200
    assert res_test.json()["role"] == "ADMIN"

    res_list = client.get("/api/v1/admin/role-requests", headers=headers)
    assert res_list.status_code == 200
    assert isinstance(res_list.json(), list)


# ==============================================================================
# 3. Role Request HTTP Lifecycle (Approve, Reject, 404, 409)
# ==============================================================================


def test_admin_approve_role_request_promotes_user(
    client: TestClient,
    db_session: Session,
    rbac_admin_token: str,
    rbac_admin_user: User,
    rbac_student_user: User,
):
    """Admin approves pending role request via HTTP: user is promoted to FACULTY."""
    # Create pending role request for the student
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
    res = client.post(
        f"/api/v1/admin/role-requests/{role_req.id}/approve",
        headers=headers,
        json={"note": "Verified faculty appointment"},
    )
    assert res.status_code == 200
    data = res.json()

    # Validate response schema
    validated = RoleRequestResponse.model_validate(data)
    assert validated.status == RoleRequestStatus.APPROVED
    assert validated.reviewed_by == rbac_admin_user.id
    assert validated.note == "Verified faculty appointment"
    assert validated.reviewed_at is not None

    # Verify user record in database was promoted to FACULTY
    db_session.refresh(rbac_student_user)
    assert rbac_student_user.role == UserRole.FACULTY


def test_admin_reject_role_request_leaves_role_unchanged(
    client: TestClient,
    db_session: Session,
    rbac_admin_token: str,
    rbac_admin_user: User,
    rbac_student_user: User,
):
    """Admin rejects pending role request via HTTP: applicant remains STUDENT."""
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
    res = client.post(
        f"/api/v1/admin/role-requests/{role_req.id}/reject",
        headers=headers,
        json={"note": "Incomplete verification"},
    )
    assert res.status_code == 200
    data = res.json()

    validated = RoleRequestResponse.model_validate(data)
    assert validated.status == RoleRequestStatus.REJECTED
    assert validated.reviewed_by == rbac_admin_user.id

    db_session.refresh(rbac_student_user)
    assert rbac_student_user.role == UserRole.STUDENT


def test_admin_review_non_existent_role_request_returns_404(client: TestClient, rbac_admin_token: str):
    """Reviewing a non-existent role request returns 404 Not Found."""
    headers = {"Authorization": f"Bearer {rbac_admin_token}"}
    fake_id = uuid.uuid4()

    res_approve = client.post(f"/api/v1/admin/role-requests/{fake_id}/approve", headers=headers)
    assert res_approve.status_code == 404
    assert "not found" in res_approve.json()["detail"].lower()

    res_reject = client.post(f"/api/v1/admin/role-requests/{fake_id}/reject", headers=headers)
    assert res_reject.status_code == 404
    assert "not found" in res_reject.json()["detail"].lower()


def test_admin_review_already_reviewed_role_request_returns_409(
    client: TestClient,
    db_session: Session,
    rbac_admin_token: str,
    rbac_student_user: User,
):
    """Attempting to approve or reject an already reviewed request returns 409 Conflict."""
    role_req = RoleRequest(
        user_id=rbac_student_user.id,
        applicant_email=rbac_student_user.email,
        requested_role=UserRole.FACULTY,
        status=RoleRequestStatus.APPROVED,
    )
    db_session.add(role_req)
    db_session.commit()
    db_session.refresh(role_req)

    headers = {"Authorization": f"Bearer {rbac_admin_token}"}

    res_approve = client.post(f"/api/v1/admin/role-requests/{role_req.id}/approve", headers=headers)
    assert res_approve.status_code == 409
    assert "already" in res_approve.json()["detail"].lower()

    res_reject = client.post(f"/api/v1/admin/role-requests/{role_req.id}/reject", headers=headers)
    assert res_reject.status_code == 409
    assert "already" in res_reject.json()["detail"].lower()


# ==============================================================================
# 4. Strict Response Schema Validation
# ==============================================================================


def test_me_endpoint_strict_schema_validation(
    client: TestClient,
    rbac_student_token: str,
    rbac_student_user: User,
):
    """Verifies that GET /api/v1/auth/me strictly matches UserResponse schema."""
    headers = {"Authorization": f"Bearer {rbac_student_token}"}
    res = client.get("/api/v1/auth/me", headers=headers)
    assert res.status_code == 200

    payload = res.json()
    validated = UserResponse.model_validate(payload)
    assert validated.id == rbac_student_user.id
    assert validated.email == rbac_student_user.email
    assert validated.role == UserRole.STUDENT
    assert validated.college == CollegeName.COEP
    assert validated.is_email_verified is True
    assert validated.auth_provider == AuthProvider.LOCAL


def test_login_endpoint_strict_schema_validation(client: TestClient, rbac_student_user: User):
    """Verifies that POST /api/v1/auth/login strictly matches TokenResponse schema."""
    res = client.post(
        "/api/v1/auth/login",
        json={
            "email": rbac_student_user.email,
            "password": "StudentPassword123!",
            "college": "COEP",
        },
    )
    assert res.status_code == 200

    payload = res.json()
    validated = TokenResponse.model_validate(payload)
    assert len(validated.access_token) > 20
    assert len(validated.refresh_token) > 20
    assert validated.token_type.lower() == "bearer"
