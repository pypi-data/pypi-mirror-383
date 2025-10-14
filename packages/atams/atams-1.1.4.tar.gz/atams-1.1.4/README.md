# ATAMS - Advanced Toolkit for Application Management System

![Version](https://img.shields.io/badge/version-1.1.4-blue)
![Python](https://img.shields.io/badge/python-3.9+-green)
![License](https://img.shields.io/badge/license-MIT-blue)

Universal toolkit untuk semua **AURA (Atams Universal Runtime Architecture)** projects.

## Features

- 🚀 **Instant CRUD Generation** - Generate full boilerplate in seconds
- 🏗️ **Clean Architecture** - Enforced separation of concerns  
- 🔒 **Security by Default** - Atlas SSO, encryption, RBAC
- 📦 **Reusable Components** - Database, middleware, logging, etc.
- 🎨 **CLI Tool** - Project initialization & code generation
- 🌐 **CORS Protection** - Default to `*.atamsindonesia.com`

## Installation

```bash
pip install atams
```

## Quick Start

### 1. Initialize New Project

```bash
atams init my-app
cd my-app
cp .env.example .env
# Edit .env with your configuration
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### 2. Generate CRUD

```bash
atams generate department
```

Generates:
- ✅ Model (SQLAlchemy)
- ✅ Schema (Pydantic)
- ✅ Repository (data access)
- ✅ Service (business logic)
- ✅ Endpoint (API routes)
- ✅ Auto-registered to `api.py`

### 3. Customize & Run

Edit generated files to add custom logic, then test:

```bash
# Access API docs
http://localhost:8000/docs

# Test endpoints
GET  /api/v1/departments
GET  /api/v1/departments/{id}
POST /api/v1/departments
PUT  /api/v1/departments/{id}
DELETE /api/v1/departments/{id}
```

## Components

### Core Components

1. **Database Layer** - BaseRepository with ORM & Native SQL, configurable connection pooling
2. **Atlas SSO** - Authentication & authorization
3. **Response Encryption** - AES-256 for GET endpoints
4. **Exception Handling** - Standardized error responses
5. **Middleware** - Request ID tracking, rate limiting
6. **Logging** - Structured logging with JSON format
7. **Transaction Management** - Context managers for complex operations
8. **Common Schemas** - Response & pagination schemas
9. **Health Check Endpoints** - Built-in monitoring endpoints with pool statistics

### Configuration

ATAMS provides `AtamsBaseSettings` with sensible defaults:

```python
from atams import AtamsBaseSettings

class Settings(AtamsBaseSettings):
    APP_NAME: str = "MyApp"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # App-specific encryption
    ENCRYPTION_KEY: str = "your-key-32-chars"
    ENCRYPTION_IV: str = "your-iv-16-char"

settings = Settings()
```

**CORS Default:** Hanya `*.atamsindonesia.com` + localhost (development)

Override via `.env`:

```env
CORS_ORIGINS=["https://myapp.atamsindonesia.com"]
```

### Database Connection Pool Configuration

**IMPORTANT:** ATAMS now has configurable connection pool settings to prevent "remaining connection slots" errors!

**Default Settings (Conservative):**
- `DB_POOL_SIZE=3` - Persistent connections
- `DB_MAX_OVERFLOW=5` - Additional overflow connections
- `DB_POOL_RECYCLE=3600` - Recycle connections after 1 hour
- `DB_POOL_TIMEOUT=30` - Timeout waiting for connection
- `DB_POOL_PRE_PING=True` - Health check before using

**For Aiven Free Tier (20 connection limit):**

Add to your `.env`:
```env
# Database connection pool settings
DB_POOL_SIZE=3
DB_MAX_OVERFLOW=5
```

This allows max 8 connections per app instance (3 + 5).

**For Production (Higher limits):**

If your database has `max_connections=100`, you can increase:
```env
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20
```

**Calculate Your Pool Settings:**

Use this formula:
```
Total Connections = (DB_POOL_SIZE + DB_MAX_OVERFLOW) × Number of App Instances
```

Ensure: `Total Connections < Database Connection Limit - 5` (reserve for admin/monitoring)

**Example:**
- Database limit: 20
- Number of apps: 2
- Pool size: `(3 + 5) × 2 = 16 connections` ✅ (safe, under 20)

**Initialize Database with Custom Pool:**

```python
from atams.db import init_database
from app.core.config import settings

# Option 1: Use settings object (reads from .env)
init_database(
    settings.DATABASE_URL,
    settings.DEBUG,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_recycle=settings.DB_POOL_RECYCLE,
    pool_timeout=settings.DB_POOL_TIMEOUT,
    pool_pre_ping=settings.DB_POOL_PRE_PING
)

# Option 2: Explicit values
init_database(
    settings.DATABASE_URL,
    settings.DEBUG,
    pool_size=3,
    max_overflow=5
)
```

**Monitor Connection Pool:**

```python
from atams.db import get_pool_status, check_connection_health

# Check pool status
status = get_pool_status()
print(f"Active: {status['checked_out']}/{status['pool_size']}")
print(f"Total connections: {status['total_connections']}")

# Health check
if not check_connection_health():
    print("Database connection issue!")
```

**Built-in Health Check Endpoints:**

ATAMS now provides **automatic health check endpoints** that you can mount in your app!

```python
from fastapi import FastAPI
from atams.api import health_router

app = FastAPI()

# Mount built-in health endpoints
app.include_router(health_router, prefix="/health", tags=["Health"])
```

This provides **3 endpoints** automatically:

1. **GET /health** - Basic application health
   ```json
   {
     "status": "ok",
     "timestamp": "2025-01-13T10:00:00"
   }
   ```

2. **GET /health/db** - Database health with connection pool stats
   ```json
   {
     "status": "ok",
     "database": {
       "connected": true,
       "pool": {
         "pool_size": 3,
         "checked_in": 2,
         "checked_out": 1,
         "overflow": 0,
         "total_connections": 3
       }
     },
     "timestamp": "2025-01-13T10:00:00"
   }
   ```

3. **GET /health/full** - Full system health check
   ```json
   {
     "status": "ok",
     "application": {
       "status": "running",
       "timestamp": "2025-01-13T10:00:00"
     },
     "database": {
       "connected": true,
       "pool": {...}
     }
   }
   ```

**Manual Usage (if needed):**

```python
from atams.db import get_pool_status, check_connection_health

# Check pool status
status = get_pool_status()
print(f"Active: {status['checked_out']}/{status['pool_size']}")

# Health check
if not check_connection_health():
    print("Database connection issue!")
```

## CLI Commands

### `atams init <project_name>`

Initialize new AURA project with complete structure.

**Options:**
- `--app-name, -a` - Application name (default: project_name)
- `--version, -v` - Application version (default: 1.0.0)
- `--schema, -s` - Database schema (default: aura)

**Example:**

```bash
atams init my-new-app
```

### `atams generate <resource>`

Generate full CRUD boilerplate for a resource.

**Options:**
- `--schema, -s` - Database schema (default: aura)
- `--skip-api` - Skip auto-registration to api.py

**Example:**

```bash
atams generate department
atams generate user --schema=public
```

### `atams --version`

Show toolkit version.

## Project Structure

```
my-app/
├── app/
│   ├── core/              # Configuration
│   │   └── config.py
│   ├── db/                # Database
│   ├── models/            # SQLAlchemy models
│   ├── schemas/           # Pydantic schemas
│   ├── repositories/      # Data access layer
│   ├── services/          # Business logic layer
│   └── api/               # API endpoints
│       └── v1/
│           ├── api.py
│           └── endpoints/
├── tests/                 # Test files
├── .env.example           # Environment template
├── requirements.txt       # Dependencies
└── README.md
```

## Usage Examples

### Using BaseRepository

BaseRepository menyediakan 20+ methods untuk operasi database yang lengkap:

#### Basic CRUD Operations
| Method | Description |
|--------|-------------|
| `get(db, id)` | Get single record by ID |
| `get_multi(db, skip, limit)` | Get multiple records with pagination |
| `create(db, obj_in)` | Create new record |
| `update(db, db_obj, obj_in)` | Update existing record |
| `delete(db, id)` | Delete record by ID |

#### Advanced Query Methods
| Method | Description |
|--------|-------------|
| `exists(db, id)` | Fast existence check (returns bool) |
| `filter(db, filters, skip, limit, order_by)` | Dynamic filtering with pagination & ordering |
| `first(db, filters, order_by)` | Get first matching record |
| `count_filtered(db, filters)` | Count records with conditions |
| `get_or_create(db, defaults, **filters)` | Get existing or create new (atomic) |
| `update_or_create(db, filters, defaults)` | Update existing or create (upsert) |

#### Bulk Operations (High Performance)
| Method | Description |
|--------|-------------|
| `bulk_create(db, objects)` | Batch insert (100x faster than loop) |
| `bulk_update(db, objects)` | Batch update multiple records |
| `delete_many(db, ids)` | Batch delete by IDs |
| `partial_update(db, id, data)` | Update without fetching first |

#### Soft Delete Pattern
| Method | Description |
|--------|-------------|
| `soft_delete(db, id, deleted_at_field)` | Logical deletion with timestamp |
| `restore(db, id, deleted_at_field)` | Restore soft-deleted record |

#### Native SQL Execution
| Method | Description |
|--------|-------------|
| `execute_raw_sql(db, query, params)` | Execute raw SQL, returns result |
| `execute_raw_sql_dict(db, query, params)` | Execute SQL, returns list of dicts |
| `execute_raw_sql_commit(db, query, params)` | Execute SQL with auto-commit |

**Example Usage:**

```python
from atams import BaseRepository
from app.models.user import User

class UserRepository(BaseRepository[User]):
    def __init__(self):
        super().__init__(User)

    def example_usage(self, db):
        # Basic CRUD
        user = self.get(db, id=1)
        users = self.get_multi(db, skip=0, limit=10)
        new_user = self.create(db, {"name": "John", "email": "john@example.com"})

        # Advanced queries
        if self.exists(db, id=1):
            print("User exists!")

        active_users = self.filter(db,
            filters={"status": "active"},
            skip=0, limit=50,
            order_by="-created_at"  # descending
        )

        first_admin = self.first(db,
            filters={"role": "admin"},
            order_by="created_at"
        )

        total = self.count_filtered(db, {"status": "active"})

        # Get or create pattern
        user, created = self.get_or_create(db,
            defaults={"status": "pending"},
            email="new@example.com"
        )

        # Bulk operations (very fast!)
        users_data = [
            {"name": "User1", "email": "user1@example.com"},
            {"name": "User2", "email": "user2@example.com"},
        ]
        self.bulk_create(db, users_data)

        # Soft delete
        self.soft_delete(db, id=1, deleted_at_field="deleted_at")
        self.restore(db, id=1, deleted_at_field="deleted_at")

        # Native SQL
        query = "SELECT * FROM users WHERE status = :status"
        active_users = self.execute_raw_sql_dict(db, query, {"status": "active"})
```

### Using Atlas SSO

Configure Atlas SSO in `.env`:
```env
ATLAS_SSO_URL=https://api.atlas-microapi.atamsindonesia.com/api/v1
ATLAS_APP_CODE=your_app_code
ATLAS_ENCRYPTION_KEY=your_encryption_key
ATLAS_ENCRYPTION_IV=your_encryption_iv
```

Then use in endpoints:
```python
from atams.sso import require_auth, require_min_role_level

@router.get("/admin", dependencies=[Depends(require_min_role_level(50))])
async def admin_dashboard(current_user: dict = Depends(require_auth)):
    # Only users with role level >= 50 can access
    return {"user": current_user}
```

### Using Response Encryption

```python
from atams.encryption import encrypt_response_data
from atams.schemas import DataResponse

@router.get("/users/{user_id}")
async def get_user(user_id: int):
    user = get_user_from_db(user_id)
    response = DataResponse(
        success=True,
        message="User retrieved",
        data=user
    )
    # Auto-encrypt if ENCRYPTION_ENABLED=true
    return encrypt_response_data(response)
```

## Development

### Setup

```bash
git clone https://github.com/GratiaManullang03/atams.git
cd atams
pip install -e ".[dev]"
```

### Run Tests

```bash
pytest tests/ -v
pytest tests/ --cov=atams --cov-report=html
```

### Build Package

```bash
python -m build
```

## Versioning

ATAMS follows [Semantic Versioning](https://semver.org/):

- **MAJOR** version for incompatible API changes
- **MINOR** version for new functionality (backwards compatible)
- **PATCH** version for bug fixes

Current version: **1.1.4**

## License

MIT License - see LICENSE file for details.

## Links

- GitHub: [https://github.com/GratiaManullang03/atams](https://github.com/GratiaManullang03/atams)
- PyPI: [https://pypi.org/project/atams](https://pypi.org/project/atams)
- Issues: [https://github.com/GratiaManullang03/atams/issues](https://github.com/GratiaManullang03/atams/issues)

## Support

For support, email [gratiamanullang03@gmail.com](mailto:gratiamanullang03@gmail.com) or open an issue on GitHub.
