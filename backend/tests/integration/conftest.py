"""Integration test fixtures.

Provides a real PostgreSQL session via Alembic migrations.
Each test runs inside a transaction that is rolled back at the end,
so tests are fully isolated and leave no residual data.
"""

import subprocess
from pathlib import Path

import pytest
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import Session

from app.core.config import settings

BACKEND_DIR = Path(__file__).resolve().parent.parent.parent


def _db_is_reachable(url: str) -> bool:
    """Try to connect to the database; return False on failure."""
    try:
        eng = create_engine(url, pool_pre_ping=True)
        with eng.connect() as conn:
            conn.execute(text("SELECT 1"))
        eng.dispose()
        return True
    except Exception:
        return False


_DB_URL = settings.DATABASE_URL


@pytest.fixture(scope="session")
def integration_engine():
    """Create engine and run Alembic migrations once per test session.

    Skips the entire integration suite when PostgreSQL is not reachable
    (e.g. running locally without a test database).
    """
    if not _db_is_reachable(_DB_URL):
        pytest.skip("PostgreSQL not reachable — skipping integration tests")

    eng = create_engine(_DB_URL, echo=False)

    result = subprocess.run(
        ["alembic", "upgrade", "head"],
        cwd=str(BACKEND_DIR),
        capture_output=True,
        text=True,
        env={**__import__("os").environ, "DATABASE_URL": _DB_URL},
    )
    if result.returncode != 0:
        pytest.fail(f"Alembic migration failed:\n{result.stderr}")

    yield eng

    eng.dispose()


@pytest.fixture()
def db(integration_engine):
    """Transactional session that rolls back after each test.

    Uses the nested-transaction (SAVEPOINT) pattern so that every
    ``session.commit()`` inside the services releases a SAVEPOINT
    instead of the real transaction.  At the end of the test the
    outer transaction is rolled back, leaving no residual data.
    """
    connection = integration_engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)

    session.begin_nested()

    @event.listens_for(session, "after_transaction_end")
    def _restart_savepoint(sess, trans):
        if trans.nested and not trans._parent.nested:
            session.begin_nested()

    yield session

    session.close()
    transaction.rollback()
    connection.close()
