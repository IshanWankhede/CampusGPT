import os
import uuid
from typing import Generator
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from app.auth import service
from app.database.session import get_db
from app.main import app
from app.models.user import AuthProvider, CollegeName, User, UserRole

TEST_DB_DEFAULT = "postgresql+psycopg2://campusgpt:campusgpt_dev@campusgpt_db:5432/campusgpt_test"
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", TEST_DB_DEFAULT)


def assert_test_database(url: str) -> None:
    """Refuses any database URL whose database name does not end with '_test'."""
    clean_url = url.split("?")[0]
    dbname = clean_url.rsplit("/", 1)[-1]
    if not dbname.endswith("_test"):
        raise RuntimeError(
            f"CRITICAL SAFETY VIOLATION: Refusing to run tests against non-test database: '{dbname}'. "
            f"Database name MUST end with '_test'."
        )


assert_test_database(TEST_DATABASE_URL)

test_engine = create_engine(TEST_DATABASE_URL, pool_pre_ping=True)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(autouse=True)
def clean_database():
    """Wipes test database tables before each test to guarantee test isolation."""
    assert_test_database(TEST_DATABASE_URL)
    with test_engine.begin() as conn:
        conn.execute(text("TRUNCATE TABLE audit_logs, auth_attempts, login_codes, refresh_tokens, otp_verifications, role_requests, users CASCADE;"))
    yield
    with test_engine.begin() as conn:
        conn.execute(text("TRUNCATE TABLE audit_logs, auth_attempts, login_codes, refresh_tokens, otp_verifications, role_requests, users CASCADE;"))


@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(autouse=True)
def mock_email_sender():
    """Fakes Resend email delivery so tests never perform external HTTP requests."""
    with patch("app.core.email.send_email", return_value=None) as mock_send:
        yield mock_send


@pytest.fixture
def mock_google_oauth():
    """Reusable mock for Google OAuth token and userinfo endpoints."""
    mock_instance = MagicMock()
    mock_token_res = MagicMock(status_code=200, is_success=True)
    mock_token_res.json.return_value = {"access_token": "mock_google_access_token"}

    mock_userinfo_res = MagicMock(status_code=200, is_success=True)
    mock_userinfo_res.json.return_value = {
        "email": f"google.user.{uuid.uuid4().hex[:8]}@coep.ac.in",
        "email_verified": True,
        "sub": f"google-sub-{uuid.uuid4().hex[:12]}",
        "name": "Google Test User",
        "picture": "https://example.com/avatar.jpg",
    }

    mock_instance.post.return_value = mock_token_res
    mock_instance.get.return_value = mock_userinfo_res
    mock_instance.__enter__.return_value = mock_instance
    mock_instance.__exit__.return_value = None

    with patch("app.auth.router.httpx.Client", return_value=mock_instance):
        yield mock_instance


@pytest.fixture
def rbac_student_user(db_session: Session) -> User:
    """Provides a verified student user."""
    student = User(
        email=f"student.{uuid.uuid4().hex[:8]}@coep.ac.in",
        hashed_password=service.hash_password("StudentPassword123!"),
        full_name="RBAC Student",
        role=UserRole.STUDENT,
        college=CollegeName.COEP,
        auth_provider=AuthProvider.LOCAL,
        is_active=True,
        is_email_verified=True,
    )
    db_session.add(student)
    db_session.commit()
    db_session.refresh(student)
    return student


@pytest.fixture
def rbac_faculty_user(db_session: Session) -> User:
    """Provides a verified faculty user."""
    faculty = User(
        email=f"faculty.{uuid.uuid4().hex[:8]}@coep.ac.in",
        hashed_password=service.hash_password("FacultyPassword123!"),
        full_name="RBAC Faculty",
        role=UserRole.FACULTY,
        college=CollegeName.COEP,
        auth_provider=AuthProvider.LOCAL,
        is_active=True,
        is_email_verified=True,
    )
    db_session.add(faculty)
    db_session.commit()
    db_session.refresh(faculty)
    return faculty


@pytest.fixture
def rbac_admin_user(db_session: Session) -> User:
    """Provides a verified admin user."""
    admin = User(
        email=f"admin.{uuid.uuid4().hex[:8]}@campusgpt.dev",
        hashed_password=service.hash_password("AdminPassword123!"),
        full_name="RBAC Admin",
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
def rbac_student_token(rbac_student_user: User) -> str:
    return service.create_access_token(rbac_student_user)


@pytest.fixture
def rbac_faculty_token(rbac_faculty_user: User) -> str:
    return service.create_access_token(rbac_faculty_user)


@pytest.fixture
def rbac_admin_token(rbac_admin_user: User) -> str:
    return service.create_access_token(rbac_admin_user)


@pytest.fixture
def client(db_session: Session) -> Generator[TestClient, None, None]:
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


