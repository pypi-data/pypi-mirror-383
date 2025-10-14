"""
ATAMS Init Command
Initialize new AURA project
"""
import typer
from pathlib import Path
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from atams.utils import write_file, ensure_dir

console = Console()


def init_project(
    project_name: str = typer.Argument(..., help="Project name"),
    app_name: str = typer.Option(None, "--app-name", "-a", help="Application name (default: project_name)"),
    app_version: str = typer.Option("1.0.0", "--version", "-v", help="Application version"),
    db_schema: str = typer.Option("aura", "--schema", "-s", help="Database schema name"),
):
    """
    Initialize a new AURA project with proper structure

    Example:
        atams init my-aura-app
        atams init my-app --app-name "My Application" --schema myapp
    """
    if app_name is None:
        app_name = project_name.replace('-', '_').replace(' ', '_')

    console.print(f"\n[bold cyan]Initializing AURA project:[/bold cyan] {project_name}")
    console.print(f"[dim]App Name:[/dim] {app_name}")
    console.print(f"[dim]Version:[/dim] {app_version}")
    console.print(f"[dim]Schema:[/dim] {db_schema}")
    console.print()

    # Project root
    project_dir = Path.cwd() / project_name

    if project_dir.exists():
        console.print(f"[red]❌ Error: Directory '{project_name}' already exists[/red]")
        raise typer.Exit(1)

    # Create directory structure
    directories = [
        project_dir / "app",
        project_dir / "app" / "core",
        project_dir / "app" / "db",
        project_dir / "app" / "models",
        project_dir / "app" / "schemas",
        project_dir / "app" / "repositories",
        project_dir / "app" / "services",
        project_dir / "app" / "api",
        project_dir / "app" / "api" / "v1",
        project_dir / "app" / "api" / "v1" / "endpoints",
        project_dir / "tests",
    ]

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Creating directory structure...", total=len(directories))

        for directory in directories:
            ensure_dir(directory)
            progress.advance(task)

    console.print("[green]Created directory structure[/green]")

    # Create files
    files_created = []

    # main.py
    main_content = f'''"""
{app_name} - AURA Application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from atams.db import init_database
from atams.logging import setup_logging_from_settings
from atams.middleware import RequestIDMiddleware
from atams.exceptions import setup_exception_handlers
from atams.api import health_router

from app.core.config import settings
from app.api.v1.api import api_router

# Setup logging
setup_logging_from_settings(settings)

# Initialize database with connection pool settings
init_database(
    settings.DATABASE_URL,
    settings.DEBUG,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_recycle=settings.DB_POOL_RECYCLE,
    pool_timeout=settings.DB_POOL_TIMEOUT,
    pool_pre_ping=settings.DB_POOL_PRE_PING
)

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    description="AURA Application with Atlas SSO Integration",
    swagger_ui_parameters={{
        "persistAuthorization": True,
    }},
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.cors_methods_list,
    allow_headers=settings.cors_headers_list,
)

# Request ID middleware
app.add_middleware(RequestIDMiddleware)

# Exception handlers
setup_exception_handlers(app)

# Include routers
app.include_router(health_router, prefix="/health", tags=["Health"])
app.include_router(api_router, prefix="/api/v1")


@app.get("/", tags=["Root"])
async def root():
    """API Root - Basic information"""
    return {{"name": settings.APP_NAME, "version": settings.APP_VERSION}}
'''
    write_file(project_dir / "app" / "main.py", main_content)
    files_created.append("app/main.py")

    # config.py
    config_content = f'''from atams import AtamsBaseSettings


class Settings(AtamsBaseSettings):
    """
    Application Settings

    Inherits from AtamsBaseSettings which includes:
    - DATABASE_URL (required)
    - ATLAS_SSO_URL, ATLAS_APP_CODE, ATLAS_ENCRYPTION_KEY, ATLAS_ENCRYPTION_IV
    - ENCRYPTION_ENABLED, ENCRYPTION_KEY, ENCRYPTION_IV (response encryption)
    - LOGGING_ENABLED, LOG_LEVEL, LOG_TO_FILE, LOG_FILE_PATH
    - CORS_ORIGINS, CORS_ALLOW_CREDENTIALS, CORS_ALLOW_METHODS, CORS_ALLOW_HEADERS
    - RATE_LIMIT_ENABLED, RATE_LIMIT_REQUESTS, RATE_LIMIT_WINDOW
    - DEBUG

    All settings can be overridden via .env file or by redefining them here.
    """
    APP_NAME: str = "{app_name}"
    APP_VERSION: str = "{app_version}"


settings = Settings()
'''
    write_file(project_dir / "app" / "core" / "config.py", config_content)
    files_created.append("app/core/config.py")

    # __init__.py files
    write_file(project_dir / "app" / "__init__.py", "")
    write_file(project_dir / "app" / "core" / "__init__.py", "")
    write_file(project_dir / "app" / "db" / "__init__.py", "")
    write_file(project_dir / "app" / "models" / "__init__.py", "")
    write_file(project_dir / "app" / "schemas" / "__init__.py", "")
    write_file(project_dir / "app" / "repositories" / "__init__.py", "")
    write_file(project_dir / "app" / "services" / "__init__.py", "")
    write_file(project_dir / "app" / "api" / "__init__.py", "")
    write_file(project_dir / "app" / "api" / "v1" / "__init__.py", "")
    write_file(project_dir / "app" / "api" / "v1" / "endpoints" / "__init__.py", "")
    write_file(project_dir / "tests" / "__init__.py", "")

    # api.py
    api_content = '''from fastapi import APIRouter

api_router = APIRouter()

# Import and register routers here
# Example:
# from app.api.v1.endpoints import users
# api_router.include_router(users.router, prefix="/users", tags=["Users"])
'''
    write_file(project_dir / "app" / "api" / "v1" / "api.py", api_content)
    files_created.append("app/api/v1/api.py")

    # .env.example
    env_content = f'''# Application
APP_NAME={app_name}
APP_VERSION={app_version}
DEBUG=true

# Database
DATABASE_URL=postgresql://user:password@localhost/{project_name.replace('-', '_')}

# Database Connection Pool Settings
# IMPORTANT: Tune based on your database connection limit!
# For Aiven free tier (20 connections): DB_POOL_SIZE=3, DB_MAX_OVERFLOW=5 (max 8 per app)
# For production (100+ connections): Increase accordingly
# Formula: Total Connections = (DB_POOL_SIZE + DB_MAX_OVERFLOW) × Number of App Instances
DB_POOL_SIZE=3
DB_MAX_OVERFLOW=5
DB_POOL_RECYCLE=3600
DB_POOL_TIMEOUT=30
DB_POOL_PRE_PING=true

# Atlas SSO
# Configure these based on your Atlas SSO environment (dev/staging/production)
ATLAS_SSO_URL=https://api.atlas-microapi.atamsindonesia.com/api/v1
ATLAS_APP_CODE={app_name.upper().replace(' ', '_')}
ATLAS_ENCRYPTION_KEY=7c5f7132ba1a6e566bccc56416039bea
ATLAS_ENCRYPTION_IV=ce84582d0e6d2591

# Response Encryption (for GET endpoints)
# IMPORTANT: Generate secure keys using:
#   Key (32 chars): openssl rand -hex 16
#   IV (16 chars):  openssl rand -hex 8
ENCRYPTION_ENABLED=false
ENCRYPTION_KEY=change_me_32_characters_long!!
ENCRYPTION_IV=change_me_16char

# Logging
LOGGING_ENABLED=true
LOG_LEVEL=INFO
LOG_TO_FILE=false

# CORS (optional - defaults to *.atamsindonesia.com)
# CORS_ORIGINS=["*"]

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60
'''
    write_file(project_dir / ".env.example", env_content)
    files_created.append(".env.example")

    # requirements.txt
    requirements = '''# ATAMS Toolkit (includes fastapi, sqlalchemy, pydantic, email-validator, etc.)
atams>=1.0.0

# Database Driver (choose based on your database)
psycopg2-binary>=2.9.0  # PostgreSQL
# mysqlclient>=2.2.0    # MySQL
# cx_Oracle>=8.3.0      # Oracle

# FastAPI Server
uvicorn[standard]>=0.24.0

# Environment variables
python-dotenv>=1.0.0
'''
    write_file(project_dir / "requirements.txt", requirements)
    files_created.append("requirements.txt")

    # .gitignore
    gitignore = '''# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/

# Environment
.env
.env.local

# IDE
.vscode/
.idea/
*.swp
*.swo

# Logs
logs/
*.log

# OS
.DS_Store
Thumbs.db

# Database
*.db
*.sqlite3
'''
    write_file(project_dir / ".gitignore", gitignore)
    files_created.append(".gitignore")

    # README.md
    readme = f'''# {app_name}

AURA Application built with ATAMS toolkit.

## Setup

1. Create virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\\Scripts\\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure environment:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. Run application:
   ```bash
   uvicorn app.main:app --reload
   ```

5. Access API:
   - Docs: http://localhost:8000/docs
   - Health: http://localhost:8000/health
   - Example Users API: http://localhost:8000/api/v1/users

## Example Endpoints

This project includes a complete working example (Users CRUD) that demonstrates:
- Complete CRUD operations (GET, POST, PUT, DELETE)
- Two-level authorization (Route + Service)
- Atlas SSO authentication
- Response encryption for GET endpoints
- ORM and Native SQL examples in BaseRepository
- Proper commit/rollback handling
- Proper error handling

**Available endpoints:**
- GET /api/v1/users - List all users (requires role level >= 50)
- GET /api/v1/users/{{id}} - Get single user (requires role level >= 10)
- POST /api/v1/users - Create user (requires role level >= 50)
- PUT /api/v1/users/{{id}} - Update user (requires role level >= 10)
- DELETE /api/v1/users/{{id}} - Delete user (requires role level >= 50)

## Generate CRUD

```bash
atams generate <resource_name>
```

Example:
```bash
atams generate department
```

## Project Structure

```
{project_name}/
├── app/
│   ├── core/           # Configuration
│   ├── db/             # Database setup
│   ├── models/         # SQLAlchemy models
│   ├── schemas/        # Pydantic schemas
│   ├── repositories/   # Data access layer
│   ├── services/       # Business logic layer
│   └── api/            # API endpoints
├── tests/              # Test files
├── .env.example        # Environment template
└── requirements.txt    # Dependencies
```

## Documentation

See ATAMS documentation for more information.
'''
    write_file(project_dir / "README.md", readme)
    files_created.append("README.md")

    # deps.py - API dependencies with SSO
    deps_content = '''"""
API Dependencies
Provides authentication and authorization dependencies using ATAMS factory pattern
"""
from atams.sso import create_atlas_client, create_auth_dependencies
from app.core.config import settings

# Initialize Atlas SSO client using factory
atlas_client = create_atlas_client(settings)

# Create auth dependencies using factory
get_current_user, require_auth, require_min_role_level, require_role_level = create_auth_dependencies(atlas_client)

# Export for use in endpoints
__all__ = [
    "atlas_client",
    "get_current_user",
    "require_auth",
    "require_min_role_level",
    "require_role_level",
]
'''
    write_file(project_dir / "app" / "api" / "deps.py", deps_content)
    files_created.append("app/api/deps.py")

    # db/session.py
    session_content = '''"""
Database Session Management
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

from app.core.config import settings

# Create engine
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    echo=settings.DEBUG
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    Database session dependency

    Usage:
        @router.get("/")
        async def endpoint(db: Session = Depends(get_db)):
            # Use db here
            pass
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
'''
    write_file(project_dir / "app" / "db" / "session.py", session_content)
    files_created.append("app/db/session.py")

    # Example Model - User
    user_model = f'''"""
Example User Model
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func
from atams.db import Base


class User(Base):
    """User model for {db_schema} schema - Table: {db_schema}.user"""
    __tablename__ = "user"
    __table_args__ = {{"schema": "{db_schema}"}}

    u_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    u_name = Column(String, nullable=True)
    u_created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    u_updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
'''
    write_file(project_dir / "app" / "models" / "user.py", user_model)
    files_created.append("app/models/user.py")

    # Example Schema - User
    user_schema = '''from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict, field_validator


class UserBase(BaseModel):
    u_name: Optional[str] = None


class UserCreate(UserBase):
    pass


class UserUpdate(UserBase):
    pass


class UserInDB(UserBase):
    model_config = ConfigDict(from_attributes=True)

    u_id: int
    u_created_at: datetime
    u_updated_at: Optional[datetime] = None

    @field_validator('u_updated_at', 'u_created_at', mode='before')
    @classmethod
    def fix_datetime_timezone(cls, v):
        """
        Fix datetime timezone format from PostgreSQL
        PostgreSQL returns: '2025-10-01 09:17:39.587802+00'
        Pydantic expects: '2025-10-01 09:17:39.587802+00:00'
        """
        if v == '' or v is None:
            return None

        # Fix timezone format: +00 -> +00:00, +07 -> +07:00
        if isinstance(v, str):
            # Pattern: ends with +XX or -XX (without colon)
            import re
            # Match timezone like +00, +07, -05 at the end
            pattern = r'([+-]\\d{{2}})$'
            match = re.search(pattern, v)
            if match:
                v = v + ':00'

        return v


class User(UserInDB):
    pass
'''
    write_file(project_dir / "app" / "schemas" / "user.py", user_schema)
    files_created.append("app/schemas/user.py")

    # Common schemas
    common_schema = '''"""
Common Response Schemas
"""
from pydantic import BaseModel
from typing import Generic, TypeVar, Optional, List

T = TypeVar("T")


class ResponseBase(BaseModel):
    success: bool
    message: str


class DataResponse(ResponseBase, Generic[T]):
    data: Optional[T] = None


class PaginationResponse(ResponseBase, Generic[T]):
    data: List[T]
    total: int
    page: int
    size: int
    pages: int
'''
    write_file(project_dir / "app" / "schemas" / "common.py", common_schema)
    files_created.append("app/schemas/common.py")

    # Example Repository - User
    user_repo = '''"""
Example User Repository
Demonstrates ORM and Native SQL patterns
"""
from typing import Optional
from sqlalchemy.orm import Session

from atams.db import BaseRepository
from app.models.user import User


class UserRepository(BaseRepository[User]):
    def __init__(self):
        super().__init__(User)

    def get_by_name(self, db: Session, name: str) -> Optional[User]:
        """
        Get user by name using ORM

        Example of custom ORM query
        """
        return db.query(User).filter(User.u_name == name).first()

    def get_users_with_native_sql(self, db: Session, skip: int = 0, limit: int = 100):
        """
        Get users using Native SQL

        EXAMPLE: Shows how to use native SQL for complex queries
        Always use parameterized queries to prevent SQL injection
        """
        query = """
            SELECT u_id, u_name, u_created_at, u_updated_at
            FROM {db_schema}.user
            ORDER BY u_created_at DESC
            LIMIT :limit OFFSET :skip
        """
        return self.execute_raw_sql_dict(db, query, {{"skip": skip, "limit": limit}})

    def count_users_native_sql(self, db: Session) -> int:
        """
        Count users using Native SQL

        EXAMPLE: Shows how to use native SQL for scalar results
        """
        query = "SELECT COUNT(*) FROM {db_schema}.user"
        return self.execute_raw_sql_scalar(db, query)
'''
    write_file(project_dir / "app" / "repositories" / "user_repository.py", user_repo.format(db_schema=db_schema))
    files_created.append("app/repositories/user_repository.py")

    # Example Service - User
    user_service = '''"""
User Service
Business logic layer with role-based permission validation

SECOND LEVEL VALIDATION happens here:
- Route level checks: "Can access this endpoint?" (via require_role_level)
- Service level checks: "What can this role level do?" (implemented here)
"""
from typing import List
from sqlalchemy.orm import Session

from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserUpdate, User
from atams.exceptions import (
    NotFoundException,
    ForbiddenException,
    BadRequestException
)


class UserService:
    def __init__(self):
        self.repository = UserRepository()

    def get_user(
        self,
        db: Session,
        user_id: int,
        current_user_role_level: int,
        current_user_id: int
    ) -> User:
        """
        Get single user with role-based access control

        Permission logic (SECOND LEVEL VALIDATION):
        - Level 100 (Super Admin): Can view any user
        - Level 50 (Admin): Can view users in same organization
        - Level 10 (User): Can only view own profile

        Args:
            db: Database session
            user_id: User ID to retrieve
            current_user_role_level: Role level from Atlas SSO
            current_user_id: Current user's ID from Atlas SSO

        Returns:
            User data

        Raises:
            NotFoundException: User not found
            ForbiddenException: Insufficient permission
        """
        db_user = self.repository.get(db, user_id)

        if not db_user:
            raise NotFoundException(f"User with ID {{user_id}} not found")

        # SECOND LEVEL VALIDATION - What can each role level do?
        if current_user_role_level >= 100:
            # Super Admin can view any user
            pass
        elif current_user_role_level >= 50:
            # Admin can view users (add organization check here if needed)
            pass
        elif current_user_role_level >= 10:
            # Regular user can only view own profile
            if user_id != current_user_id:
                raise ForbiddenException("You can only view your own profile")
        else:
            raise ForbiddenException("Insufficient permission to view user")

        return User.model_validate(db_user)

    def get_users(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
        current_user_role_level: int = 0
    ) -> List[User]:
        """
        Get list of users with pagination

        Permission logic:
        - Level 100: Can view all users
        - Level 50: Can view users in organization
        - Level 10: Cannot list users

        Raises:
            ForbiddenException: Insufficient permission
        """
        # SECOND LEVEL VALIDATION
        if current_user_role_level < 50:
            raise ForbiddenException("Insufficient permission to list users")

        db_users = self.repository.get_multi(db, skip=skip, limit=limit)
        return [User.model_validate(user) for user in db_users]

    def create_user(self, db: Session, user: UserCreate, current_user_role_level: int) -> User:
        """
        Create new user

        Permission logic:
        - Level 100: Can create any user
        - Level 50: Can create users with level < 50
        - Level 10: Cannot create users

        Raises:
            ForbiddenException: Insufficient permission
            BadRequestException: Invalid data
        """
        # SECOND LEVEL VALIDATION
        if current_user_role_level < 50:
            raise ForbiddenException("Insufficient permission to create user")

        # Validate input
        if not user.u_name or len(user.u_name.strip()) == 0:
            raise BadRequestException("User name is required")

        db_user = self.repository.create(db, user.model_dump())
        return User.model_validate(db_user)

    def update_user(
        self,
        db: Session,
        user_id: int,
        user: UserUpdate,
        current_user_role_level: int,
        current_user_id: int
    ) -> User:
        """
        Update existing user

        Permission logic:
        - Level 100: Can update any user
        - Level 50: Can update users with level < 50
        - Level 10: Can only update own profile

        Raises:
            NotFoundException: User not found
            ForbiddenException: Insufficient permission
        """
        db_user = self.repository.get(db, user_id)

        if not db_user:
            raise NotFoundException(f"User with ID {{user_id}} not found")

        # SECOND LEVEL VALIDATION - User ownership check
        if current_user_role_level >= 100:
            # Super Admin can update any user
            pass
        elif current_user_role_level >= 50:
            # Admin can update users (add level check if needed)
            pass
        elif current_user_role_level >= 10:
            # Regular user can only update own profile
            if user_id != current_user_id:
                raise ForbiddenException("You can only update your own profile")
        else:
            raise ForbiddenException("Insufficient permission to update user")

        update_data = user.model_dump(exclude_unset=True)
        db_user = self.repository.update(db, db_user, update_data)
        return User.model_validate(db_user)

    def delete_user(self, db: Session, user_id: int, current_user_role_level: int) -> None:
        """
        Delete user

        Permission logic:
        - Level 100: Can delete any user
        - Level 50: Can delete users with level < 50
        - Level 10: Cannot delete users

        Raises:
            NotFoundException: User not found
            ForbiddenException: Insufficient permission
        """
        # SECOND LEVEL VALIDATION
        if current_user_role_level < 50:
            raise ForbiddenException("Insufficient permission to delete user")

        deleted = self.repository.delete(db, user_id)

        if not deleted:
            raise NotFoundException(f"User with ID {{user_id}} not found")

    def get_total_users(self, db: Session) -> int:
        """Get total count of users"""
        return self.repository.count(db)
'''
    write_file(project_dir / "app" / "services" / "user_service.py", user_service)
    files_created.append("app/services/user_service.py")

    # Example Endpoint - Users
    users_endpoint = '''"""
User Endpoints
Demonstrates complete AURA v2 patterns:
- Atlas SSO authentication
- Two-level authorization (route + service)
- Response encryption for GET
- Proper HTTP status codes
- Clean error handling
"""
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.user_service import UserService
from app.schemas.user import User, UserCreate, UserUpdate
from app.schemas.common import DataResponse, PaginationResponse
from app.api.deps import require_auth, require_min_role_level
from atams.encryption import encrypt_response_data
from app.core.config import settings

router = APIRouter()
user_service = UserService()


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_min_role_level(50))]  # FIRST LEVEL: Route validation
)
async def get_users(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum records to return"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_auth)
):
    """
    Get list of users with pagination

    **FIRST LEVEL Authorization (Route):**
    - Requires role level >= 50 (Admin or above)

    **SECOND LEVEL Authorization (Service):**
    - Level 100: Can view all users
    - Level 50: Can view users in organization

    **Response:**
    - Encrypted if ENCRYPTION_ENABLED=true
    - Status code 200
    """
    # SECOND LEVEL: Service validates what each level can do
    users = user_service.get_users(
        db,
        skip=skip,
        limit=limit,
        current_user_role_level=current_user["role_level"]
    )
    total = user_service.get_total_users(db)

    response = PaginationResponse(
        success=True,
        message="Users retrieved successfully",
        data=users,
        total=total,
        page=skip // limit + 1,
        size=limit,
        pages=(total + limit - 1) // limit
    )

    # Auto-encrypt GET responses
    return encrypt_response_data(response, settings)


@router.get(
    "/{user_id}",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_min_role_level(10))]  # FIRST LEVEL: Route validation
)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_auth)
):
    """
    Get single user by ID

    **FIRST LEVEL Authorization (Route):**
    - Requires role level >= 10 (any authenticated user)

    **SECOND LEVEL Authorization (Service):**
    - Level 100: Can view any user
    - Level 50: Can view users in organization
    - Level 10: Can only view own profile

    **Response:**
    - Encrypted if ENCRYPTION_ENABLED=true
    - Status code 200
    - Raises 404 if not found
    """
    # SECOND LEVEL: Service validates permissions with user ownership
    user = user_service.get_user(
        db,
        user_id,
        current_user_role_level=current_user["role_level"],
        current_user_id=current_user["user_id"]
    )

    response = DataResponse(
        success=True,
        message="User retrieved successfully",
        data=user
    )

    # Auto-encrypt GET responses
    return encrypt_response_data(response, settings)


@router.post(
    "/",
    response_model=DataResponse[User],
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_min_role_level(50))]  # FIRST LEVEL
)
async def create_user(
    user: UserCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_auth)
):
    """
    Create new user

    **FIRST LEVEL Authorization (Route):**
    - Requires role level >= 50 (Admin or above)

    **SECOND LEVEL Authorization (Service):**
    - Level 100: Can create any user
    - Level 50: Can create users with level < 50

    **Response:**
    - Status code 201 (Created)
    - Raises 400 if validation fails
    - Raises 409 if user exists
    """
    new_user = user_service.create_user(
        db,
        user,
        current_user_role_level=current_user["role_level"]
    )

    return DataResponse(
        success=True,
        message="User created successfully",
        data=new_user
    )


@router.put(
    "/{user_id}",
    response_model=DataResponse[User],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_min_role_level(10))]  # FIRST LEVEL
)
async def update_user(
    user_id: int,
    user: UserUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_auth)
):
    """
    Update existing user

    **FIRST LEVEL Authorization (Route):**
    - Requires role level >= 10

    **SECOND LEVEL Authorization (Service):**
    - Level 100: Can update any user
    - Level 50: Can update users with level < 50
    - Level 10: Can only update own profile

    **Response:**
    - Status code 200
    - Raises 404 if not found
    - Raises 403 if insufficient permission
    """
    updated_user = user_service.update_user(
        db,
        user_id,
        user,
        current_user_role_level=current_user["role_level"],
        current_user_id=current_user["user_id"]
    )

    return DataResponse(
        success=True,
        message="User updated successfully",
        data=updated_user
    )


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_min_role_level(50))]  # FIRST LEVEL
)
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_auth)
):
    """
    Delete user

    **FIRST LEVEL Authorization (Route):**
    - Requires role level >= 50 (Admin or above)

    **SECOND LEVEL Authorization (Service):**
    - Level 100: Can delete any user
    - Level 50: Can delete users with level < 50

    **Response:**
    - Status code 204 (No Content) on success
    - Raises 404 if not found
    - Raises 403 if insufficient permission
    """
    user_service.delete_user(
        db,
        user_id,
        current_user_role_level=current_user["role_level"]
    )

    # 204 returns no content
    return None
'''
    write_file(project_dir / "app" / "api" / "v1" / "endpoints" / "users.py", users_endpoint)
    files_created.append("app/api/v1/endpoints/users.py")

    # Update api.py to include users
    api_update = '''from fastapi import APIRouter
from app.api.v1.endpoints import users

api_router = APIRouter()

# Register routes
api_router.include_router(users.router, prefix="/users", tags=["Users"])
'''
    write_file(project_dir / "app" / "api" / "v1" / "api.py", api_update)

    # Success summary
    console.print()
    console.print("[bold green]Project created successfully![/bold green]")
    console.print()
    console.print("[bold]Files created:[/bold]")
    for file in files_created:
        console.print(f"  [green]+[/green] {file}")

    console.print()
    console.print("[bold]Next steps:[/bold]")
    console.print(f"  1. [cyan]cd {project_name}[/cyan]")
    console.print(f"  2. [cyan]cp .env.example .env[/cyan]")
    console.print(f"  3. Generate encryption keys:")
    console.print(f"     [cyan]openssl rand -hex 16[/cyan]  # Copy to ENCRYPTION_KEY")
    console.print(f"     [cyan]openssl rand -hex 8[/cyan]   # Copy to ENCRYPTION_IV")
    console.print(f"  4. Edit .env with your configuration (database, keys, etc.)")
    console.print(f"  5. [cyan]python -m venv venv[/cyan]")
    console.print(f"  6. [cyan]venv\\Scripts\\activate[/cyan]  # On Windows")
    console.print(f"  7. [cyan]pip install -r requirements.txt[/cyan]")
    console.print(f"  8. [cyan]uvicorn app.main:app --reload[/cyan]")
    console.print()
