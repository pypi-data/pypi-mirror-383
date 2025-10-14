"""
Transaction Management Utilities for ATAMS

Provides explicit transaction control for complex operations
that require multiple database operations to succeed or fail together.

USAGE PATTERNS (in user project):

1. AUTOMATIC COMMIT (ORM Methods):
   ```python
   # Repository methods auto-commit
   user = repo.create(db, {"u_name": "John"})  # Auto-commits
   ```

2. MANUAL TRANSACTION (Multiple Operations):
   ```python
   from atams.transaction import transaction

   with transaction(db):
       repo.execute_raw_sql(db, "INSERT INTO ...", params)
       repo.execute_raw_sql(db, "UPDATE ...", params)
       # Auto-commits at end, or rolls back on exception
   ```

3. EXPLICIT ROLLBACK:
   ```python
   from atams.transaction import transaction

   with transaction(db) as tx:
       try:
           # ... operations ...
           if some_condition:
               tx.rollback()  # Explicit rollback
               return
       except Exception:
           tx.rollback()  # Rollback on error
           raise
   ```
"""
from contextlib import contextmanager
from typing import Generator, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy import text

# Optional logger - will work without it
logger: Optional[Any] = None
try:
    from atams.logging import get_logger
    logger = get_logger(__name__)
except ImportError:
    pass


class Transaction:
    """
    Transaction wrapper for explicit control

    Provides methods for commit and rollback
    """

    def __init__(self, db: Session):
        self.db = db
        self.committed = False
        self.rolled_back = False

    def commit(self):
        """Commit transaction"""
        if not self.rolled_back:
            self.db.commit()
            self.committed = True
            if logger:
                logger.debug("Transaction committed")

    def rollback(self):
        """Rollback transaction"""
        if not self.committed:
            self.db.rollback()
            self.rolled_back = True
            if logger:
                logger.debug("Transaction rolled back")


@contextmanager
def transaction(db: Session) -> Generator[Transaction, None, None]:
    """
    Context manager for database transactions

    Features:
    - Auto-commit on success
    - Auto-rollback on exception
    - Explicit commit/rollback methods

    Args:
        db: Database session

    Yields:
        Transaction object

    Example:
        ```python
        from app.core.transaction import transaction

        with transaction(db) as tx:
            # Multiple operations
            repo.execute_raw_sql(db, "INSERT INTO ...", params)
            repo.execute_raw_sql(db, "UPDATE ...", params)

            if validation_fails:
                tx.rollback()
                return

            # Auto-commits here if no exception
        ```
    """
    tx = Transaction(db)

    try:
        yield tx

        # Auto-commit if not already committed or rolled back
        if not tx.committed and not tx.rolled_back:
            tx.commit()

    except Exception as e:
        # Auto-rollback on exception
        if not tx.rolled_back:
            tx.rollback()
            if logger:
                logger.error(f"Transaction rolled back due to exception: {str(e)}")
        raise


@contextmanager
def savepoint(db: Session, name: str = "savepoint") -> Generator[None, None, None]:
    """
    Create a savepoint for nested transactions

    Savepoints allow you to rollback to a specific point without
    rolling back the entire transaction.

    Args:
        db: Database session
        name: Savepoint name

    Example:
        ```python
        from atams.transaction import transaction, savepoint

        with transaction(db):
            # Insert user
            repo.execute_raw_sql(db, "INSERT INTO users ...", params)

            # Create savepoint before risky operation
            with savepoint(db, "before_update"):
                try:
                    repo.execute_raw_sql(db, "UPDATE ...", params)
                except Exception:
                    # Rolls back to savepoint, user insert is preserved
                    raise

            # Continue with other operations
        ```
    """
    # Create savepoint
    db.execute(text("SAVEPOINT :name"), {"name": name})
    if logger:
        logger.debug(f"Savepoint created: {name}")

    try:
        yield

    except Exception as e:
        # Rollback to savepoint
        db.execute(f"ROLLBACK TO SAVEPOINT {name}")
        if logger:
            logger.error(f"Rolled back to savepoint {name}: {str(e)}")
        raise

    finally:
        # Release savepoint
        db.execute(f"RELEASE SAVEPOINT {name}")
        if logger:
            logger.debug(f"Savepoint released: {name}")
