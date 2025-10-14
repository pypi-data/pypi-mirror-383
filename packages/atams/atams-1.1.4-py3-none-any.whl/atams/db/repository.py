"""
Base Repository Pattern
Provides standardized methods for ORM and Native SQL operations

IMPORTANT PATTERNS:

1. ORM USAGE (Recommended for simple CRUD):
   - Use built-in methods: get(), get_multi(), create(), update(), delete()
   - SQLAlchemy handles transactions automatically
   - Type-safe with model validation

   Example:
   ```python
   # In repository
   from atams.db.repository import BaseRepository
   from app.models.user import User as UserModel

   class UserRepository(BaseRepository[UserModel]):
       def __init__(self):
           super().__init__(UserModel)

   # In service
   user_repo = UserRepository()
   user = user_repo.get(db, user_id=1)
   new_user = user_repo.create(db, {"u_name": "John"})
   ```

2. NATIVE SQL USAGE (For complex queries):
   - Use execute_raw_sql() or execute_raw_sql_dict()
   - Always use parameterized queries to prevent SQL injection
   - Must handle transaction manually if needed

   Example:
   ```python
   # In repository
   def get_users_with_stats(self, db: Session, min_age: int):
       query = '''
           SELECT u.u_id, u.u_name, COUNT(o.order_id) as total_orders
           FROM users u
           LEFT JOIN orders o ON u.u_id = o.user_id
           WHERE u.age >= :min_age
           GROUP BY u.u_id, u.u_name
       '''
       return self.execute_raw_sql_dict(db, query, {"min_age": min_age})

   # In service
   users_stats = user_repo.get_users_with_stats(db, min_age=18)
   ```

3. TRANSACTION HANDLING:
   - ORM methods auto-commit
   - For Native SQL with multiple operations, use db.begin()

   Example:
   ```python
   with db.begin():
       self.execute_raw_sql(db, "INSERT INTO ...", params)
       self.execute_raw_sql(db, "UPDATE ...", params)
   ```
"""
from typing import TypeVar, Generic, Type, Optional, List, Any, Dict
from sqlalchemy.orm import Session
from sqlalchemy import func, text, inspect

from atams.db.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """
    Base repository for database operations
    Supports both ORM and Native SQL approaches
    Hybrid: Use ORM for simple operations, Native SQL for complex queries
    """

    def __init__(self, model: Type[ModelType]):
        self.model = model
        # Get primary key column name dynamically
        self._pk_column = self._get_primary_key_column()

    def _get_primary_key_column(self):
        """Get primary key column name from model"""
        mapper = inspect(self.model)
        pk_columns = [col.name for col in mapper.primary_key]
        return pk_columns[0] if pk_columns else 'id'

    # ==================== ORM METHODS ====================

    def get(self, db: Session, id: Any) -> Optional[ModelType]:
        """
        Get single record by ID using ORM

        Args:
            db: Database session
            id: Primary key value

        Returns:
            Model instance or None if not found

        Example:
            user = user_repo.get(db, 1)
        """
        pk_attr = getattr(self.model, self._pk_column)
        return db.query(self.model).filter(pk_attr == id).first()

    def get_multi(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100
    ) -> List[ModelType]:
        """
        Get multiple records with pagination using ORM

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of model instances
        """
        return db.query(self.model).offset(skip).limit(limit).all()

    def create(self, db: Session, obj_in: Dict[str, Any]) -> ModelType:
        """
        Create new record using ORM

        Args:
            db: Database session
            obj_in: Dictionary with field values

        Returns:
            Created model instance

        Example:
            user = repo.create(db, {"u_name": "John", "u_email": "john@example.com"})
        """
        db_obj = self.model(**obj_in)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self,
        db: Session,
        db_obj: ModelType,
        obj_in: Dict[str, Any]
    ) -> ModelType:
        """
        Update existing record using ORM

        Args:
            db: Database session
            db_obj: Existing model instance to update
            obj_in: Dictionary with fields to update

        Returns:
            Updated model instance

        Example:
            user = repo.get(db, user_id=1)
            updated = repo.update(db, user, {"u_name": "Jane"})
        """
        for field, value in obj_in.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, id: Any) -> Optional[ModelType]:
        """
        Delete record using ORM

        Args:
            db: Database session
            id: Primary key value

        Returns:
            Deleted model instance or None if not found

        Example:
            deleted_user = user_repo.delete(db, user_id=1)
        """
        pk_attr = getattr(self.model, self._pk_column)
        obj = db.query(self.model).filter(pk_attr == id).first()
        if obj:
            db.delete(obj)
            db.commit()
        return obj

    def count(self, db: Session) -> int:
        """
        Count total records using ORM

        Args:
            db: Database session

        Returns:
            Total count

        Example:
            total_users = user_repo.count(db)
        """
        pk_attr = getattr(self.model, self._pk_column)
        return db.query(func.count(pk_attr)).scalar()

    # ==================== NATIVE SQL METHODS ====================

    def execute_raw_sql(
        self,
        db: Session,
        query: str,
        params: Optional[Dict[str, Any]] = None
    ) -> List[Any]:
        """
        Execute raw SQL query and return results as tuples

        IMPORTANT: Always use parameterized queries!

        Args:
            db: Database session
            query: SQL query string with :param placeholders
            params: Dictionary of parameter values

        Returns:
            List of tuples (raw query results)

        Example:
            query = "SELECT * FROM users WHERE u_id = :user_id"
            results = repo.execute_raw_sql(db, query, {"user_id": 1})
        """
        result = db.execute(text(query), params or {})
        return result.fetchall()

    def execute_raw_sql_dict(
        self,
        db: Session,
        query: str,
        params: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Execute raw SQL query and return results as dictionaries

        IMPORTANT: Always use parameterized queries!

        Args:
            db: Database session
            query: SQL query string with :param placeholders
            params: Dictionary of parameter values

        Returns:
            List of dictionaries (column_name: value)

        Example:
            query = '''
                SELECT u_id, u_name, u_email
                FROM users
                WHERE u_created_at >= :start_date
            '''
            results = repo.execute_raw_sql_dict(db, query, {"start_date": "2024-01-01"})
            # Returns: [{"u_id": 1, "u_name": "John", "u_email": "john@example.com"}, ...]
        """
        result = db.execute(text(query), params or {})
        columns = result.keys()
        return [dict(zip(columns, row)) for row in result.fetchall()]

    def check_database_health(self, db: Session) -> bool:
        """
        Check if database connection is healthy

        Args:
            db: Database session

        Returns:
            True if database is healthy, False otherwise

        Example:
            if repo.check_database_health(db):
                print("Database is healthy")
        """
        try:
            db.execute(text("SELECT 1"))
            return True
        except Exception:
            return False

    def execute_raw_sql_scalar(
        self,
        db: Session,
        query: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Any:
        """
        Execute raw SQL query and return single scalar value

        Args:
            db: Database session
            query: SQL query string
            params: Dictionary of parameter values

        Returns:
            Single value (useful for COUNT, SUM, etc.)

        Example:
            query = "SELECT COUNT(*) FROM users WHERE u_status = :status"
            total = repo.execute_raw_sql_scalar(db, query, {"status": "active"})
        """
        result = db.execute(text(query), params or {})
        return result.scalar()

    # ==================== ADVANCED CRUD METHODS ====================

    def exists(self, db: Session, id: Any) -> bool:
        """
        Check if record exists by ID (fast query)

        Args:
            db: Database session
            id: Primary key value

        Returns:
            True if exists, False otherwise

        Example:
            if user_repo.exists(db, user_id=1):
                print("User exists")
        """
        pk_attr = getattr(self.model, self._pk_column)
        return db.query(pk_attr).filter(pk_attr == id).first() is not None

    def filter(
        self,
        db: Session,
        filters: Optional[Dict[str, Any]] = None,
        skip: int = 0,
        limit: int = 100,
        order_by: Optional[str] = None
    ) -> List[ModelType]:
        """
        Get filtered records with pagination and ordering

        Args:
            db: Database session
            filters: Dictionary of field:value pairs
            skip: Number of records to skip
            limit: Maximum number of records to return
            order_by: Column name to order by (prefix with - for DESC)

        Returns:
            List of model instances

        Example:
            users = repo.filter(
                db,
                filters={"u_is_active": True},
                order_by="-u_created_at",
                limit=10
            )
        """
        query = db.query(self.model)

        # Apply filters
        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field):
                    query = query.filter(getattr(self.model, field) == value)

        # Apply ordering
        if order_by:
            if order_by.startswith('-'):
                # Descending order
                column_name = order_by[1:]
                if hasattr(self.model, column_name):
                    query = query.order_by(getattr(self.model, column_name).desc())
            else:
                # Ascending order
                if hasattr(self.model, order_by):
                    query = query.order_by(getattr(self.model, order_by))

        return query.offset(skip).limit(limit).all()

    def first(
        self,
        db: Session,
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[str] = None
    ) -> Optional[ModelType]:
        """
        Get first record matching filters

        Args:
            db: Database session
            filters: Dictionary of field:value pairs
            order_by: Column name to order by (prefix with - for DESC)

        Returns:
            First matching model instance or None

        Example:
            user = repo.first(db, filters={"u_email": "john@example.com"})
        """
        results = self.filter(db, filters=filters, skip=0, limit=1, order_by=order_by)
        return results[0] if results else None

    def count_filtered(self, db: Session, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Count records matching filters

        Args:
            db: Database session
            filters: Dictionary of field:value pairs

        Returns:
            Count of matching records

        Example:
            active_count = repo.count_filtered(db, {"u_is_active": True})
        """
        pk_attr = getattr(self.model, self._pk_column)
        query = db.query(func.count(pk_attr))

        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field):
                    query = query.filter(getattr(self.model, field) == value)

        return query.scalar()

    def bulk_create(self, db: Session, objects: List[Dict[str, Any]]) -> List[ModelType]:
        """
        Bulk insert multiple records (much faster than loop)

        Args:
            db: Database session
            objects: List of dictionaries with field values

        Returns:
            List of created model instances

        Example:
            users = repo.bulk_create(db, [
                {"u_name": "John"},
                {"u_name": "Jane"},
                {"u_name": "Bob"}
            ])
        """
        db_objects = [self.model(**obj) for obj in objects]
        db.bulk_save_objects(db_objects, return_defaults=True)
        db.commit()
        return db_objects

    def bulk_update(self, db: Session, objects: List[ModelType]) -> None:
        """
        Bulk update multiple records

        Args:
            db: Database session
            objects: List of model instances with updated values

        Example:
            users = repo.get_multi(db, limit=100)
            for user in users:
                user.u_is_active = True
            repo.bulk_update(db, users)
        """
        db.bulk_save_objects(objects)
        db.commit()

    def delete_many(self, db: Session, ids: List[Any]) -> int:
        """
        Delete multiple records by IDs

        Args:
            db: Database session
            ids: List of primary key values

        Returns:
            Number of deleted records

        Example:
            deleted_count = repo.delete_many(db, [1, 2, 3, 4, 5])
        """
        pk_attr = getattr(self.model, self._pk_column)
        deleted_count = db.query(self.model).filter(pk_attr.in_(ids)).delete(synchronize_session=False)
        db.commit()
        return deleted_count

    def partial_update(
        self,
        db: Session,
        id: Any,
        data: Dict[str, Any]
    ) -> Optional[ModelType]:
        """
        Update record without fetching it first (more efficient)

        Args:
            db: Database session
            id: Primary key value
            data: Dictionary of fields to update

        Returns:
            Updated model instance or None if not found

        Example:
            user = repo.partial_update(db, 1, {"u_name": "New Name"})
        """
        pk_attr = getattr(self.model, self._pk_column)

        # Update query
        db.query(self.model).filter(pk_attr == id).update(data, synchronize_session=False)
        db.commit()

        # Fetch updated object
        return db.query(self.model).filter(pk_attr == id).first()

    def get_or_create(
        self,
        db: Session,
        defaults: Optional[Dict[str, Any]] = None,
        **filters
    ) -> tuple[ModelType, bool]:
        """
        Get existing record or create new one (atomic operation)

        Args:
            db: Database session
            defaults: Default values for creation
            **filters: Filter criteria for lookup

        Returns:
            Tuple of (model_instance, created)
            - created=True if new record was created
            - created=False if existing record was found

        Example:
            user, created = repo.get_or_create(
                db,
                defaults={"u_name": "John Doe"},
                u_email="john@example.com"
            )
            if created:
                print("New user created")
        """
        # Try to get existing
        obj = self.first(db, filters=filters)

        if obj:
            return obj, False

        # Create new
        create_data = {**(defaults or {}), **filters}
        obj = self.create(db, create_data)
        return obj, True

    def update_or_create(
        self,
        db: Session,
        filters: Dict[str, Any],
        defaults: Dict[str, Any]
    ) -> tuple[ModelType, bool]:
        """
        Update existing record or create new one (upsert)

        Args:
            db: Database session
            filters: Filter criteria for lookup
            defaults: Values to set (for both update and create)

        Returns:
            Tuple of (model_instance, created)
            - created=True if new record was created
            - created=False if existing record was updated

        Example:
            user, created = repo.update_or_create(
                db,
                filters={"u_email": "john@example.com"},
                defaults={"u_name": "John Doe", "u_is_active": True}
            )
        """
        obj = self.first(db, filters=filters)

        if obj:
            # Update existing
            for field, value in defaults.items():
                if hasattr(obj, field):
                    setattr(obj, field, value)
            db.add(obj)
            db.commit()
            db.refresh(obj)
            return obj, False

        # Create new
        create_data = {**filters, **defaults}
        obj = self.create(db, create_data)
        return obj, True

    def soft_delete(self, db: Session, id: Any, deleted_at_field: str = "deleted_at") -> Optional[ModelType]:
        """
        Soft delete record (set deleted_at timestamp instead of removing)

        Args:
            db: Database session
            id: Primary key value
            deleted_at_field: Name of the deleted_at column (default: "deleted_at")

        Returns:
            Soft-deleted model instance or None if not found

        Note:
            Requires model to have a deleted_at column

        Example:
            user = repo.soft_delete(db, user_id=1)
        """
        from datetime import datetime

        if not hasattr(self.model, deleted_at_field):
            raise AttributeError(f"Model {self.model.__name__} does not have field '{deleted_at_field}'")

        pk_attr = getattr(self.model, self._pk_column)
        obj = db.query(self.model).filter(pk_attr == id).first()

        if obj:
            setattr(obj, deleted_at_field, datetime.now())
            db.add(obj)
            db.commit()
            db.refresh(obj)

        return obj

    def restore(self, db: Session, id: Any, deleted_at_field: str = "deleted_at") -> Optional[ModelType]:
        """
        Restore soft-deleted record (set deleted_at to NULL)

        Args:
            db: Database session
            id: Primary key value
            deleted_at_field: Name of the deleted_at column (default: "deleted_at")

        Returns:
            Restored model instance or None if not found

        Example:
            user = repo.restore(db, user_id=1)
        """
        if not hasattr(self.model, deleted_at_field):
            raise AttributeError(f"Model {self.model.__name__} does not have field '{deleted_at_field}'")

        pk_attr = getattr(self.model, self._pk_column)
        obj = db.query(self.model).filter(pk_attr == id).first()

        if obj:
            setattr(obj, deleted_at_field, None)
            db.add(obj)
            db.commit()
            db.refresh(obj)

        return obj
