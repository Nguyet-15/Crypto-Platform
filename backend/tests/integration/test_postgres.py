"""Opt-in real PostgreSQL check; unit tests do not require a database."""

import os

import pytest

from app.db.session import check_database


@pytest.mark.skipif(
    os.getenv("RUN_DB_TESTS") != "1", reason="Set RUN_DB_TESTS=1 for PostgreSQL"
)
def test_postgres_connection():
    check_database()
