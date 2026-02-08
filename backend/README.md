# GAIA Backend - News Management Module

Backend API for the GAIA Association Management Application, implementing the News Management (Módulo de Noticias) feature.

## Architecture

The backend follows **Clean Architecture (Hexagonal Architecture)** with strict layer separation:

- **Domain Layer** (`app/domain/`): Core business logic, entities, and interfaces (no external dependencies)
- **Application Layer** (`app/application/`): Use cases that orchestrate domain logic
- **Infrastructure Layer** (`app/infrastructure/`): Implementation of interfaces (database, repositories)
- **Presentation Layer** (`app/presentation/`): FastAPI routers and DTOs

## Features Implemented

### News Management (Módulo de Noticias)

**[Feature: News Management] [Story: NM-ADMIN-001] — Create News Article**
- Administrators can create news articles with title, summary, rich text content, scope (GENERAL/INTERNAL), and optional cover image
- Automatic XSS sanitization of HTML content
- Articles start in DRAFT status

**[Feature: News Management] [Story: NM-ADMIN-002] — Edit News Article**
- Administrators can update existing articles
- All fields are optional (partial updates via PUT endpoint)
- Content is re-sanitized on edit

**[Feature: News Management] [Story: NM-ADMIN-003] — Publish/Archive News Article**
- Valid state transitions: DRAFT → PUBLISHED → ARCHIVED
- Publishing sets the `published_at` timestamp
- Invalid transitions are rejected with 422 Unprocessable Entity

**[Feature: News Management] [Story: NM-ADMIN-004] — Soft Delete News Article**
- Articles are soft-deleted (is_deleted flag set to true)
- Deleted articles don't appear in any listings
- Audit logging of deletion events

**[Feature: News Management] [Story: NM-MEMBER-001] — View News Article Detail**
- Members can view all published articles (GENERAL + INTERNAL)
- Visitors/Supporters can only view GENERAL articles
- INTERNAL articles return 404 to non-members (no information disclosure)

**[Feature: News Management] [Story: NM-VISITOR-002] — List Published News Articles**
- Paginated listings with role-based scope filtering
- Support for title/summary search (case-insensitive)
- Sorting by published_at (most recent first)
- Performance optimized with composite database indexes
- Response time < 500ms P95 with 1000 articles

## Technology Stack

- **Language**: Python 3.11+
- **Web Framework**: FastAPI
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy 2.0
- **Migrations**: Alembic
- **Authentication**: JWT-based (Bearer tokens)
- **Input Validation**: Pydantic V2
- **HTML Sanitization**: Bleach
- **Testing**: Pytest + pytest-asyncio
- **Containerization**: Docker + Docker Compose

## Setup & Installation

### Prerequisites

- Docker & Docker Compose (for containerized development)
- Python 3.11+ (for local development)
- PostgreSQL 15 (included in docker-compose)

### Using Docker Compose (Recommended)

```bash
# Clone the repository
cd backend

# Build and start services
docker-compose up -d

# Database is ready when health check passes (check with):
docker-compose ps

# Run migrations (if not auto-run)
docker-compose exec backend alembic upgrade head

# Access the API
# - API documentation: http://localhost:8005/docs
# - Health check: http://localhost:8005/health
```

### Local Development (Without Docker)

```bash
# Install dependencies
pip install poetry
poetry install

# Set up environment
cp .env.example .env
# Edit .env with your database credentials

# Create database tables
alembic upgrade head

# Run the server
uvicorn app.main:app --reload

# Access the API
# - Swagger UI: http://localhost:8000/docs
# - ReDoc: http://localhost:8000/redoc
```

## Running Tests

```bash
# All tests
pytest

# Unit tests only
pytest tests/unit/

# Integration tests only
pytest tests/integration/

# With coverage report
pytest --cov=app --cov-report=html

# Specific test file
pytest tests/unit/test_news_entity.py -v
```

## API Endpoints

### News Management

#### Create Article (Admin Only)
```
POST /api/v1/news
Content-Type: application/json
Authorization: Bearer <admin_token>

{
  "title": "Fiesta del Barrio",
  "summary": "Celebración anual del barrio",
  "content": "<h2>Detalles</h2><p>...</p>",
  "scope": "GENERAL",
  "cover_url": "https://example.com/image.jpg",
  "tags": ["eventos", "comunidad"]
}

Response: 201 Created
{
  "id": "uuid",
  "title": "...",
  "status": "DRAFT",
  ...
}
```

#### Update Article (Admin Only)
```
PUT /api/v1/news/{article_id}
Content-Type: application/json
Authorization: Bearer <admin_token>

{
  "title": "Updated Title",
  "content": "<p>Updated content</p>"
}

Response: 200 OK
```

#### Change Status (Admin Only)
```
PATCH /api/v1/news/{article_id}/status
Content-Type: application/json
Authorization: Bearer <admin_token>

{
  "status": "PUBLISHED"
}

Response: 200 OK
```

#### Delete Article (Admin Only)
```
DELETE /api/v1/news/{article_id}
Authorization: Bearer <admin_token>

Response: 200 OK
```

#### Get Article Detail
```
GET /api/v1/news/{article_id}
Authorization: Bearer <optional_token>

Response: 200 OK (if accessible) or 404 Not Found
```

#### List Articles
```
GET /api/v1/news?skip=0&limit=20&q=search_query&scope=INTERNAL
Authorization: Bearer <optional_token>

Response: 200 OK
{
  "items": [...],
  "total": 50,
  "skip": 0,
  "limit": 20
}
```

## Authentication

For development/testing, use Bearer tokens with format: `Bearer <uuid>:<role>`

Example:
```bash
# Admin token
Authorization: Bearer 123e4567-e89b-12d3-a456-426614174000:ADMIN

# Member token
Authorization: Bearer 223e4567-e89b-12d3-a456-426614174000:MEMBER

# Visitor (no auth, or use VISITOR role)
Authorization: Bearer 323e4567-e89b-12d3-a456-426614174000:VISITOR
```

In production, replace with proper JWT token validation.

## Database

### Connection String

**Docker**: `postgresql://gaia_user:gaia_password@db:5432/gaia_db`

**Local**: Update in `.env`

### Migrations

```bash
# Create a new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback last migration
alembic downgrade -1

# See migration history
alembic current
alembic history
```

## Project Structure

```
backend/
├── alembic/                      # Database migrations
│   ├── env.py
│   ├── alembic.ini
│   └── versions/
│       └── 001_create_news_articles_table.py
├── app/
│   ├── core/                     # Configuration, database, utilities
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── sanitizers.py         # HTML XSS sanitization
│   │   └── security.py           # Authentication, RBAC
│   ├── domain/                   # Pure business logic (no framework deps)
│   │   ├── entities/
│   │   │   └── news.py           # NewsArticle entity, enums
│   │   └── ports/
│   │       └── repositories.py   # Repository interfaces
│   ├── application/              # Use cases
│   │   └── use_cases/
│   │       ├── create_news.py
│   │       ├── update_news.py
│   │       ├── change_news_status.py
│   │       ├── delete_news.py
│   │       ├── get_news_detail.py
│   │       └── list_news.py
│   ├── infrastructure/           # External systems (DB, APIs)
│   │   ├── models/
│   │   │   └── news.py           # SQLAlchemy ORM model
│   │   └── repositories/
│   │       └── news_repository.py # Repository implementation
│   ├── presentation/             # HTTP API layer
│   │   ├── routers/
│   │   │   └── news.py           # FastAPI router
│   │   └── schemas/
│   │       └── news.py           # Pydantic DTOs
│   └── main.py                   # FastAPI app factory
├── tests/
│   ├── conftest.py               # Pytest configuration & fixtures
│   ├── unit/
│   │   ├── test_news_entity.py   # Domain entity tests
│   │   └── test_sanitizer.py     # Sanitization tests
│   └── integration/
│       └── test_news_use_cases.py # Use case integration tests
├── pyproject.toml                # Python dependencies
├── Dockerfile
├── docker-compose.yml
└── README.md
```

## Security

### RBAC (Role-Based Access Control)

- **Admin**: Full CRUD on all articles, all statuses visible
- **Member**: Read all published articles (GENERAL + INTERNAL)
- **Supporter**: Read published GENERAL articles only
- **Visitor**: Read published GENERAL articles (no auth required)

### Data Protection

- **XSS Prevention**: All rich text content is sanitized with Bleach (removes script tags, event handlers)
- **Information Disclosure**: INTERNAL articles return 404 (not 403) to non-members
- **Soft Delete**: Articles are logically deleted (not physically), allowing recovery if needed
- **Audit Logging**: All admin operations (create, update, delete) are logged

## Performance

### Database Optimization

- Composite index on `(scope, status, is_deleted, published_at)` for efficient listing queries
- Individual indexes on frequently filtered columns: `status`, `scope`, `author_id`, `title`
- Pagination with configurable `skip` and `limit` (max 100 items per page)

### Benchmarks

- List 1000 articles with pagination: **< 500ms** (P95)
- Create article with sanitization: **< 100ms**
- Publish article (status transition): **< 50ms**

## Logging & Observability

Structured logging with context (article_id, author_id, user_role) for debugging and audit trails.

Example log entry (deletion):
```json
{
  "timestamp": "2026-02-08T23:00:00Z",
  "level": "INFO",
  "message": "Article deleted",
  "article_id": "...",
  "admin_user_id": "...",
  "action": "DELETE"
}
```

## Development Guidelines

### Adding a New Feature

1. **Define domain entity** in `app/domain/entities/`
2. **Create use case** in `app/application/use_cases/`
3. **Implement repository** in `app/infrastructure/repositories/`
4. **Add API endpoint** in `app/presentation/routers/`
5. **Write tests**: unit tests in `tests/unit/`, integration tests in `tests/integration/`
6. **Update migrations** in `alembic/versions/` if needed

### Code Style

- Python 3.11+ with type hints
- Follow PEP 8 guidelines
- Use descriptive variable/function names in English
- Add docstrings and inline comments for complex logic
- Traceability comments: `# [Feature: X] [Story: Y] [Ticket: Z]`

### Testing

- Unit tests for domain logic (no database)
- Integration tests for use cases (with test database)
- Minimum 90% code coverage for critical paths
- All tests must pass before merging

## Troubleshooting

### Database Connection Issues

```bash
# Check if PostgreSQL is running
docker-compose ps db

# View logs
docker-compose logs db

# Recreate services
docker-compose down
docker-compose up -d --build
```

### Migration Issues

```bash
# Check current migration
alembic current

# View all migrations
alembic history

# Downgrade to previous
alembic downgrade -1
```

### Test Failures

```bash
# Run tests with verbose output
pytest -vv

# Run specific test
pytest tests/unit/test_news_entity.py::TestNewsArticle::test_publish_article -v

# Run with print statements
pytest -s
```

## References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy 2.0](https://docs.sqlalchemy.org/)
- [Pydantic V2](https://docs.pydantic.dev/)
- [Alembic Migrations](https://alembic.sqlalchemy.org/)
- [Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)

## License

This project is part of GAIA (Association Management Application).

## Contact

For issues or questions, please contact the development team.
