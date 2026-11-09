import pytest
from tests.conftest import assert_test_database


def test_guard_accepts_test_database():
    """Confirms that database URLs ending with '_test' pass the safety guard."""
    assert_test_database("postgresql://campusgpt:campusgpt_dev@localhost:5433/campusgpt_test")
    assert_test_database("postgresql+psycopg2://user:pass@db:5432/my_app_test?sslmode=disable")
    assert_test_database("postgresql://localhost/unit_test")


def test_guard_refuses_non_test_databases():
    """Confirms that database URLs not ending with '_test' immediately raise a RuntimeError."""
    unsafe_urls = [
        "postgresql://campusgpt:campusgpt_dev@localhost:5433/campusgpt",
        "postgresql://user:pass@db:5432/production",
        "postgresql://user:pass@db:5432/postgres",
        "postgresql://user:pass@db:5432/campusgpt_testing",
        "postgresql://user:pass@db:5432/campusgpt_test_live",
    ]
    for url in unsafe_urls:
        with pytest.raises(RuntimeError) as exc_info:
            assert_test_database(url)
        assert "CRITICAL SAFETY VIOLATION" in str(exc_info.value)
        assert "MUST end with '_test'" in str(exc_info.value)
