# Day 1 Summary — Project Scaffold & Docker Infrastructure

## What We Built

A fully scaffolded FastAPI project with Dockerized PostgreSQL and Redis, ready for development.

---

## Steps Completed

### 1. Project Initialization

```powershell
mkdir fastapi-reels && cd fastapi-reels
python -m venv venv
venv\Scripts\activate        # Windows activation
```

### 2. Dependencies (`requirements.txt`)

Created with these key packages:

- **fastapi** — web framework
- **uvicorn[standard]** — ASGI server with hot reload
- **sqlalchemy[asyncio]** — async ORM
- **psycopg[binary]** — PostgreSQL driver for async (used instead of asyncpg for Windows compatibility)
- **alembic** — database migrations
- **python-jose[cryptography]** — JWT tokens
- **passlib[bcrypt]** — password hashing
- **pydantic-settings** — environment variable management
- **redis** — caching layer

Installed with:

```bash
pip install -r requirements.txt
```

### 3. Docker Services (`docker-compose.yml`)

- PostgreSQL 15 on port **5432**
  - user: `postgres`
  - password: `postgres`
  - db: `fastapi_reels`

- Redis 7 on port **6379**

Started with:

```bash
docker-compose up -d
```

### 4. Environment Configuration (`.env`)

```env
SECRET_KEY="dev-8d7f9g0h1j2k3l4m5n6o7p8q9r0s1t2u"
DATABASE_URL="postgresql+psycopg://postgres:postgres@localhost:5432/fastapi_reels"
REDIS_URL="redis://localhost:6379/0"
```

Also created:

- `.env.example` → template for repository sharing

### 5. Project Structure

```
fastapi-reels/
├── app/
│   ├── api/v1/         # Route handlers (auth, users, reels)
│   ├── core/           # Config and security utilities
│   ├── db/             # Database base, session
│   ├── models/        # SQLAlchemy models
│   ├── schemas/       # Pydantic schemas
│   ├── services/      # External services (ImageKit, Redis)
│   └── main.py        # FastAPI app entry point
├── .env                # Environment variables (gitignored)
├── .env.example        # Template for team
├── docker-compose.yml  # Infrastructure
└── requirements.txt    # Python dependencies
```

### 6. FastAPI App

- `app/core/config.py` → settings class using `pydantic-settings`
- `app/main.py` → FastAPI instance with health-check endpoint:

```json
{
  "status": "alive",
  "project": "FastAPI Reels Backend"
}
```

### 7. Verification

- Server running at: `http://127.0.0.1:8000`
- Swagger docs: `http://127.0.0.1:8000/docs`
- PostgreSQL container healthy
- Redis container healthy

---

## Errors Encountered & Solutions

| Error                                              | Cause                                     | Solution                             |
| -------------------------------------------------- | ----------------------------------------- | ------------------------------------ |
| `'source' is not recognized`                       | Windows doesn't use Unix `source` command | Used `venv\Scripts\activate`         |
| Failed building wheel for asyncpg                  | Missing MSVC Build Tools on Windows       | Switched to `psycopg[binary]==3.3.4` |
| No matching distribution for psycopg-binary==3.2.4 | Python 3.14 compatibility issue           | Upgraded to `psycopg[binary]==3.3.4` |
| `SECRET_KEY / DATABASE_URL / REDIS_URL required`   | Missing `.env` file                       | Created `.env`                       |
| Docker API connection failed                       | Docker Desktop not running                | Started Docker Desktop               |
| `version is obsolete` warning                      | Old docker-compose version field          | Removed `version: '3.8'`             |

---

## Key Decisions

- **psycopg over asyncpg**
  Chosen for zero-compilation installation on Windows while maintaining async support.

- **Python 3.14**
  Latest version; verified dependency compatibility.

- **Docker usage strategy**
  Only PostgreSQL + Redis in containers, FastAPI runs locally for faster development.

---

# Day 2 Summary — Async Database Engine, Models, and Alembic

## What We Built

- Async PostgreSQL connection via SQLAlchemy and psycopg
- First database model (**User**)
- Alembic configured for async migrations
- First migration created and applied
- Verified tables in PostgreSQL

---

## Steps Completed

### 1. Declarative Base (`app/db/base.py`)

- Created SQLAlchemy `DeclarativeBase`
- Used as the base class for all ORM models

### 2. Async Session (`app/db/session.py`)

- Configured `create_async_engine` using `psycopg`
- Set up `async_sessionmaker`
- Created `get_db` dependency for FastAPI routes

### 3. User Model (`app/models/user.py`)

Created `users` table with:

- UUID primary key
- Unique `username` and `email` indexes
- `password_hash` field
- `followers_count` / `following_count`
- `created_at` / `updated_at` timestamps

### 4. Alembic Initialization

```bash
alembic init alembic
```

### 5. Alembic Async Configuration

- Updated `alembic/env.py`
- Connected to database using `settings.DATABASE_URL`
- Enabled async engine support via `async_engine_from_config`

### 6. First Migration

```bash
alembic revision --autogenerate -m "init user table"
```

Generated:

```
51ba7137547e_init_user_table.py
```

### 7. Migration Applied

```bash
alembic upgrade head
```

Result:

- `users` table created successfully

### 8. Verification

- `alembic_version` table exists
- `users` table exists
- Confirmed in PostgreSQL

### 9. DB Dependency (`app/api/dependencies.py`)

- Created `get_db` async generator
- Ready for injection into API routes

### 10. Server Status

- Uvicorn running without errors
- Swagger docs accessible

---

## Errors Encountered & Solutions

| Error                                  | Cause                                                      | Solution                                                                                                           |
| -------------------------------------- | ---------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| Psycopg cannot use `ProactorEventLoop` | Windows default event loop incompatible with psycopg async | Added `asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())` in `alembic/env.py` (Windows only) |

---

## Key Decisions

### 1. Windows Selector Event Loop

Required for psycopg async compatibility on Windows.

- Safe for Windows only
- No impact on Linux/Mac production

### 2. `expire_on_commit=False`

- Prevents SQLAlchemy from expiring ORM objects after commit
- Simplifies returning database objects directly in API responses
- Avoids extra SELECT queries

---

# Day 3 Summary — JWT Authentication (Register/Login)

## What We Built

A complete authentication system with:

- Password hashing
- JWT token creation and validation
- User registration and login
- Protected profile endpoint
- Account deletion

---

## Steps Completed

### 1. Security Utilities (`app/core/security.py`)

- `CryptContext` with bcrypt for password hashing
- `verify_password()` → compares plain text with hash
- `get_password_hash()` → hashes password before storage
- `create_access_token()` → generates JWT token (HS256 + expiry)

### 2. Pydantic Schemas

- **UserCreate**
  - username
  - email (`EmailStr`)
  - password

- **UserOut**
  - UUID (string)
  - username/email
  - timestamps (ISO format)

- **Token**
  - `access_token`
  - `token_type`

- **TokenData**
  - decoded JWT payload

### 3. Auth Endpoints (`app/api/v1/auth.py`)

| Method | Endpoint                | Status | Description                           |
| ------ | ----------------------- | ------ | ------------------------------------- |
| POST   | `/api/v1/auth/register` | 201    | Creates user with duplicate check     |
| POST   | `/api/v1/auth/login`    | 200    | Validates credentials and returns JWT |

### 4. Current User Dependency (`app/api/dependencies.py`)

- `oauth2_scheme` → extracts Bearer token
- `get_current_user()` → decodes JWT, fetches user, raises 401 if invalid
- `get_db()` → async DB session generator

### 5. User Endpoints (`app/api/v1/users.py`)

| Method | Endpoint           | Auth     | Description                  |
| ------ | ------------------ | -------- | ---------------------------- |
| GET    | `/api/v1/users/me` | Required | Returns current user profile |
| DELETE | `/api/v1/users/me` | Required | Deletes user account         |

### 6. Router Registration (`app/main.py`)

- Auth router mounted at `/api/v1`
- Users router mounted at `/api/v1`

---

## Testing Completed

- User registration with duplicate detection
- Login returns valid JWT
- `/users/me` works with valid token
- Protected routes return **401 Unauthorized** without token
- Account deletion works and invalidates access

---

## Authentication Flow

```text
1. POST /register   → Create user + hash password
2. POST /login      → Verify credentials + return JWT
3. Authorize header → Bearer <token>
4. GET /users/me    → Fetch profile
5. DELETE /users/me → Delete account
```

---

## Errors Encountered & Solutions

| Error                 | Cause                 | Solution          |
| --------------------- | --------------------- | ----------------- |
| No errors encountered | Stable implementation | No fixes required |

---

## Key Decisions

- **bcrypt for hashing**
  - Industry standard
  - Automatic salt generation

- **HS256 JWT**
  - Symmetric signing
  - Suitable for monolith backend (RS256 reserved for distributed systems)

- **Email-based login**
  - Email used as primary login identifier
  - Username kept for display uniqueness

- **7-day token expiry**
  - `ACCESS_TOKEN_EXPIRE_MINUTES=10080`
  - Balance between usability and security

- **`from_attributes = True`**
  - Enables direct ORM → Pydantic conversion
  - Removes manual mapping overhead

---

## Current Project Structure

```text
fastapi-reels/
├── app/
│   ├── api/v1/
│   │   ├── auth.py          ✅ Register & Login endpoints
│   │   ├── users.py         ✅ Profile & Delete endpoints
│   │   └── reels.py         ⬜ Empty (Day 4)
│   ├── core/
│   │   ├── config.py        ✅ Settings from .env
│   │   └── security.py      ✅ Password hashing & JWT
│   ├── db/
│   │   ├── base.py          ✅ DeclarativeBase
│   │   └── session.py       ✅ Async engine & session
│   ├── models/
│   │   └── user.py          ✅ User model (migrated)
│   ├── schemas/
│   │   ├── user.py          ✅ UserCreate, UserOut
│   │   └── token.py         ✅ Token, TokenData
│   └── main.py              ✅ App with routers
├── alembic/                 ✅ One migration applied
├── .env                     ✅ All variables set
└── docker-compose.yml       ✅ PostgreSQL + Redis running
```

---

## Day 3 Outcome

Complete authentication system is live:

- User registration
- Login with JWT
- Protected routes
- Profile access
- Account deletion

All secured endpoints correctly enforce **401 Unauthorized** when no valid token is provided.

```

```
