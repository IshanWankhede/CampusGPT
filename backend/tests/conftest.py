import os
from typing import Generator
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from app.database.session import get_db
from app.main import app

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
        conn.execute(text("TRUNCATE TABLE auth_attempts, login_codes, otp_verifications, users CASCADE;"))
    yield
    with test_engine.begin() as conn:
        conn.execute(text("TRUNCATE TABLE auth_attempts, login_codes, otp_verifications, users CASCADE;"))


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

