"""Database dependencies.

Provides database session for dependency injection.
"""

from typing import Generator

from sqlalchemy.orm import Session

from app.infrastructure.database import get_db


def get_database() -> Generator[Session, None, None]:
    """Get database session dependency.

    Yields:
        Database session

    Example:
        ```python
        @app.get("/items")
        def read_items(db: Session = Depends(get_database)):
            return db.query(Item).all()
        ```
    """
    yield from get_db()
