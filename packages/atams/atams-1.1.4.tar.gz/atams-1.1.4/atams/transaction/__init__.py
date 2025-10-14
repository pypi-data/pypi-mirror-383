"""
Transaction Management
=====================
Database transaction utilities for complex operations.

Usage:
    from atams.transaction import Transaction, transaction, savepoint

    # Context manager
    with transaction(db):
        # Your operations
        pass

    # Savepoint
    with savepoint(db, "my_savepoint"):
        # Your operations
        pass
"""
from atams.transaction.manager import Transaction, transaction, savepoint

__all__ = [
    "Transaction",
    "transaction",
    "savepoint",
]
