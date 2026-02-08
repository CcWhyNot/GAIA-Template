# NM-ADMIN-001-DB-T01 — Implementation Plan

**Source ticket**: `specs/features/news-management/tickets.md` → **NM-ADMIN-001-DB-T01**  
**Related user story**: **NM-ADMIN-001** (from `specs/features/news-management/user-stories.md`)  
**Plan version**: v1.0 — Database schema and ORM model for News Management  
**Traceability**: All tasks reference `NM-ADMIN-001-DB-T01` and `NM-ADMIN-001`.

---

## 1) Context & Objective

**Ticket Summary:**
Create the foundational database schema for the News Management feature. This includes:

- PostgreSQL `news_articles` table with all required columns (title, summary, content, status, scope, author_id, cover_url, tags, timestamps, soft-delete flag).
- Enums for status (DRAFT, PUBLISHED, ARCHIVED) and scope (GENERAL, INTERNAL).
- Foreign key reference to the `users` table (author_id).
- Indexes for efficient querying on status, scope, published_at, and is_deleted.
- SQLAlchemy ORM model mapping the table.
- Domain entity and value objects in the `domain/` layer.
- Repository interface (port) defining the contract for data access.

**Impacted entities/tables:**

- `news_articles` (new table).
- Relationship to `users` (FK on author_id).

**Impacted services/modules:**

- `backend/app/domain/entities/news.py` — Domain entity, value objects, enums.
- `backend/app/domain/ports/news_repository.py` — Repository interface.
- `backend/app/infrastructure/models/news.py` — SQLAlchemy model.
- `backend/alembic/versions/` — Migration script.

**Impacted tests or business flows:**

- Unit tests for domain entity validation.
- Integration tests for repository (CRUD operations with the new table).

---

## 2) Scope

### In scope

- Alembic migration creating `news_articles` table with all columns.
- PostgreSQL enum types for `news_status` (DRAFT, PUBLISHED, ARCHIVED) and `news_scope` (GENERAL, INTERNAL).
- Indexes: on `status`, `scope`, `published_at`, `is_deleted`, and composite index on `(scope, status, is_deleted, published_at)` for efficient listing.
- Foreign key constraint on `author_id` → `users.id` with ON DELETE SET NULL (author deletion does not cascade).
- SQLAlchemy model in `infrastructure/` mapping the table.
- Domain entity and value objects in `domain/` (NewsArticle, NewsStatus, NewsScope, NewsSummary).
- Repository interface (NewsRepository port) in `domain/ports/`.
- Soft-delete support: `is_deleted` boolean column, defaulting to false.

### Out of scope

- Test data factories (those will be in testing infrastructure).
- Trigger-based audit logging (audit logging will be via application layer).
- Full-text search indexes (can be added later).
- Archival/purge policies (retention is open-ended for now).

### Assumptions

- User Management DB schema is already in place (`users` table exists).
- PostgreSQL 12+ is in use (supports arrays, proper enum support).
- Alembic is configured and migrations directory is accessible.
- No need for column-level encryption; standard TLS in transit is sufficient.

### Open questions

- Should cover_url be indexed for faster image retrieval, or is the composite index sufficient?
    - **Assumption**: Composite index is sufficient; cover_url is optional and rarely used for filtering.

---

## 3) Detailed Work Plan (TDD + BDD)

### 3.1 Test-first sequencing

For a database ticket, the test-first approach means:

1. **Define** SQL expectations (schema, constraints, indexes) in a migration test suite.
2. **Define** ORM model expectations (properties, relationships, validation).
3. **Define** domain entity expectations (value objects, business invariants).
4. **Minimal implementation**: Create the migration, ORM model, and domain entity.
5. **Refactor** for clarity and consistency.

**Key scenarios to cover:**

- Migration creates table with correct column types, constraints, and indexes.
- ORM model maps all columns and relationships correctly.
- Domain entity enforces business rules (e.g., published_at can only be set when status=PUBLISHED).
- Soft-delete query filters (`is_deleted=false` is the default).

### 3.2 NFR hooks

- **Security/Privacy**: PII minimization (only author_id stored, not author email/name). Content sanitization deferred to application layer. No encryption at rest (beyond DB-level backups).
- **Performance**: Composite index `(scope, status, is_deleted, published_at)` enables efficient listing queries (List endpoint must < 500ms P95).
- **Observability**: Timestamps (created_at, updated_at) for audit trails. is_deleted flag allows soft-delete querying.
- **Compliance**: GDPR — author_id is a UUID reference, not PII itself. Pseudonymized access.

---

## 4) Atomic Task Breakdown

### Task 1: Create Alembic Migration

- **Purpose**: Generate and write the SQL migration that creates the `news_articles` table, enums, indexes, and constraints. This is the contract between the backend and the database.
- **Artifacts impacted**: `backend/alembic/versions/<timestamp>_create_news_articles_table.py`.
- **Test types**: Migration unit test (verify migration script can be applied and rolled back cleanly).
- **BDD Acceptance (Given-When-Then)**:
    ```gherkin
    Given an empty PostgreSQL database with user_management schema
    When the migration is applied (`alembic upgrade head`)
    Then the news_articles table exists with columns: id (UUID PK), title (varchar 255), summary (varchar 500), content (text), status (enum), scope (enum), author_id (UUID FK), cover_url (varchar nullable), tags (text array), published_at (timestamp nullable), created_at (timestamp), updated_at (timestamp), is_deleted (boolean default false)
    And indexes exist on status, scope, published_at, is_deleted
    And the composite index on (scope, status, is_deleted, published_at) exists
    And foreign key on author_id references users(id) with ON DELETE SET NULL
    And when the migration is rolled back, the table is dropped
    ```

---

### Task 2: Define Domain Entity and Value Objects

- **Purpose**: Create the domain layer abstractions (NewsArticle entity, value objects for status/scope, Gherkin expectations). This ensures business logic is testable without the database.
- **Artifacts impacted**: `backend/app/domain/entities/news.py`, `backend/app/domain/value_objects/news_scope.py`, `backend/app/domain/value_objects/news_status.py`.
- **Test types**: Unit tests (pure Python domain logic, no database).
- **BDD Acceptance (Given-When-Then)**:

    ```gherkin
    Given a NewsArticle domain entity
    When instantiated with valid title, summary, content, scope, author_id
    Then the entity has all properties accessible
    And created_at is auto-set to current timestamp
    And status defaults to DRAFT
    And is_deleted defaults to false

    Given a NewsStatus value object
    When created with "DRAFT"
    Then it is a valid NewsStatus
    When created with "INVALID"
    Then it raises a domain exception

    Given a NewsScope value object
    When created with "GENERAL" or "INTERNAL"
    Then it is valid
    When created with "RESTRICTED"
    Then it raises a domain exception
    ```

---

### Task 3: Create SQLAlchemy Model

- **Purpose**: Map the PostgreSQL table to a Python ORM model in the infrastructure layer. This bridges domain entities and database access.
- **Artifacts impacted**: `backend/app/infrastructure/models/news.py`, `backend/app/core/database.py` (if Base is not already centralized).
- **Test types**: Unit tests (ORM column mapping, relationships).
- **BDD Acceptance (Given-When-Then)**:
    ```gherkin
    Given a NewsArticle SQLAlchemy model
    When columns are defined (id, title, summary, content, status, scope, author_id, cover_url, tags, published_at, created_at, updated_at, is_deleted)
    Then the model can be instantiated with all attributes
    And the model reflects table constraints (FK on author_id, NOT NULL on title/summary/content/status/scope)
    And the model relationship to User entity is properly configured (lazy loading, back_populates)
    And the model responds to query methods (filter, order_by, etc.)
    ```

---

### Task 4: Create Repository Interface (Port)

- **Purpose**: Define the contract for data access in the domain layer. This enables loose coupling between domain and infrastructure.
- **Artifacts impacted**: `backend/app/domain/ports/news_repository.py` (or `repositories.py`).
- **Test types**: No tests for the interface itself (interfaces are abstract), but contract tests in integration tests.
- **BDD Acceptance (Given-When-Then)**:
    ```gherkin
    Given a NewsRepository port (interface)
    When the interface is defined
    Then it has methods: save(article: NewsArticle) -> NewsArticle, get_by_id(id: UUID) -> NewsArticle | None, list(...filters...) -> List[NewsArticle], delete(id: UUID) -> None
    And each method has a clear docstring describing parameters, return types, and exceptions
    ```

---

### Task 5: Create Repository Implementation (Adapter)

- **Purpose**: Implement the repository interface using SQLAlchemy, handling queries with soft-delete and filtering logic.
- **Artifacts impacted**: `backend/app/infrastructure/repositories/news_repository.py`.
- **Test types**: Integration tests (against test PostgreSQL instance), unit tests with mocked session.
- **BDD Acceptance (Given-When-Then)**:

    ```gherkin
    Given a NewsRepository implementation backed by SQLAlchemy
    When save() is called with a new NewsArticle
    Then the article is inserted into news_articles table and returned with id set

    When get_by_id() is called with a valid article id
    Then the article is retrieved (only if is_deleted=false)
    When get_by_id() is called with a soft-deleted article id
    Then None is returned

    When list() is called with filters (scope=GENERAL, status=PUBLISHED, skip=0, limit=10)
    Then articles matching filters are returned, sorted by published_at DESC
    And is_deleted=false is always applied (implicit soft-delete filter)

    When delete() is called with an article id
    Then is_deleted is set to true and updated_at is refreshed
    And the article no longer appears in list() or get_by_id() queries
    ```

---

## Summary of Deliverables

1. **Alembic migration file** creating the table, enums, indexes, and constraints.
2. **Domain entity** (NewsArticle) and value objects (NewsStatus, NewsScope) with business logic.
3. **SQLAlchemy model** mapping the table to ORM.
4. **Repository interface** (NewsRepository port) defining the contract.
5. **Repository implementation** using SQLAlchemy with soft-delete and filtering support.
6. **Unit + integration tests** covering schema, ORM, domain, and repository logic.
