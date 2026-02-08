# NM-ADMIN-001-BE-T02 — Implementation Plan

**Source ticket**: `specs/features/news-management/tickets.md` → **NM-ADMIN-001-BE-T02**  
**Related user story**: **NM-ADMIN-001** (from `specs/features/news-management/user-stories.md`)  
**Plan version**: v1.0 — Create News Article Endpoint  
**Traceability**: All tasks reference `NM-ADMIN-001-BE-T02` and `NM-ADMIN-001`.

---

## 1) Context & Objective

**Ticket Summary:**
Implement the POST `/api/v1/news` endpoint for Administrators to create news articles. The endpoint:
- Enforces RBAC (Admin-only access).
- Validates input via Pydantic DTOs.
- Sanitizes rich text content to prevent stored XSS attacks.
- Persists the article via the repository (created in NM-ADMIN-001-DB-T01).
- Returns HTTP 201 with the created article on success.
- Returns appropriate HTTP error codes (401 Unauthorized, 403 Forbidden, 422 Unprocessable Entity).

**Impacted services/modules:**
- `backend/app/presentation/routers/news.py` — FastAPI router with POST endpoint.
- `backend/app/presentation/schemas/news.py` — Pydantic request/response DTOs.
- `backend/app/application/use_cases/create_news.py` — CreateNewsUseCase business logic.
- `backend/app/infrastructure/repositories/news_repository.py` — Repository implementation (from DB ticket).
- `backend/app/core/security.py` — RBAC dependency/middleware.
- `backend/app/core/sanitizers.py` — HTML sanitization utility.

**Impacted tests or business flows:**
- Happy path: Admin creates article with all fields, minimal fields.
- Edge cases: Missing required fields (422), non-admin attempts creation (403), unauthenticated user (401).
- Security: XSS content sanitization.
- Observable: Created article appears in database with correct author_id and timestamps.

---

## 2) Scope

### In scope
- FastAPI router with POST `/api/v1/news` endpoint.
- Pydantic request DTO (CreateNewsRequest) with validation (required: title, summary, content, scope; optional: cover_url, tags).
- Pydantic response DTO (NewsResponse) with all article fields.
- RBAC dependency ensuring only Admin role can call the endpoint.
- CreateNewsUseCase orchestrating domain logic (entity creation, repository save).
- HTML sanitization utility (using `bleach` or `markupsafe`) to strip XSS vectors from content.
- Unit tests: use case logic, input validation, sanitization.
- Integration tests: endpoint call with Admin role (201), non-admin role (403), missing fields (422), XSS payload sanitized.

### Out of scope
- File upload for cover images (cover_url is a string URL).
- Rich text editor component (frontend concern).
- Async job processing (immediate synchronous persistence).
- Auto-tagging or ML-based categorization.
- Email notifications on article creation.

### Assumptions
- User authentication is in place (JWT tokens are validated upstream via middleware).
- User roles (Admin, Member, Supporter, Visitor) are available in the JWT claims or database lookup.
- Repository implementation is complete (save method exists and returns the saved article with id).
- Bleach library is already available in backend dependencies (or markupsafe is sufficient).

### Open questions
- Should we validate title uniqueness, or allow duplicate titles?
  - **Assumption**: No uniqueness constraint; different articles can have the same title.
- Should cover_url be validated (e.g., is it a valid URL format)?
  - **Assumption**: Basic URL format validation in Pydantic (URL type); domain validation is out of scope.

---

## 3) Detailed Work Plan (TDD + BDD)

### 3.1 Test-first sequencing

1. **Define expectations** (unit tests):
   - Pydantic DTO validates required fields and rejects extra fields.
   - CreateNewsUseCase accepts valid input and calls repository.save().
   - Sanitizer removes script tags and other XSS vectors.
2. **Define endpoint expectations** (integration tests):
   - POST /api/v1/news with valid Admin token returns 201 with article.
   - POST /api/v1/news with non-admin token returns 403.
   - POST /api/v1/news without token returns 401.
   - POST /api/v1/news with missing title returns 422.
   - POST /api/v1/news with XSS payload in content stores sanitized content.
3. **Minimal implementation**:
   - Create DTOs, use case, router, sanitizer.
4. **Refactor**:
   - Ensure error handling is consistent; logging is structured.

### 3.2 NFR hooks

- **Security/Privacy**: RBAC at endpoint level (Admin-only). Content sanitization removes script/iframe/etc. No PII leakage in error messages. Author is inferred from JWT, not from request body.
- **Performance**: Synchronous write; no async needed (low write volume). Sanitization is O(content_length).
- **Observability**: Structured logging: `logger.info("Article created", extra={"article_id": article.id, "author_id": current_user.id})`.
- **Data Validation**: Pydantic with `extra="forbid"` to reject unexpected fields. Title, summary, content are required; cover_url and tags are optional.

---

## 4) Atomic Task Breakdown

### Task 1: Create Pydantic DTOs

- **Purpose**: Define the request and response schemas for the endpoint. Enforce validation at the boundary.
- **Artifacts impacted**: `backend/app/presentation/schemas/news.py`.
- **Test types**: Unit tests (Pydantic validation).
- **BDD Acceptance (Given-When-Then)**:
  ```gherkin
  Given a CreateNewsRequest DTO
  When created with title="Test", summary="Summary", content="<p>Content</p>", scope="GENERAL"
  Then the DTO is valid and all fields are accessible

  When created without a title
  Then Pydantic raises a ValidationError

  When created with extra field unknown_field="value"
  Then Pydantic raises a ValidationError (extra="forbid")

  Given a NewsResponse DTO
  When created from a NewsArticle domain entity
  Then all fields (id, title, summary, content, scope, status, cover_url, tags, author_id, published_at, created_at, updated_at, is_deleted) are serialized correctly
  ```

---

### Task 2: Create CreateNewsUseCase

- **Purpose**: Orchestrate the business logic for creating a news article (entity creation, repository persistence).
- **Artifacts impacted**: `backend/app/application/use_cases/create_news.py`.
- **Test types**: Unit tests (pure logic, no database).
- **BDD Acceptance (Given-When-Then)**:
  ```gherkin
  Given a CreateNewsUseCase with a mocked repository
  When execute() is called with valid title, summary, content, scope, author_id
  Then a NewsArticle domain entity is created
  And the repository.save() method is called with the entity
  And the use case returns the saved article with id set

  When execute() is called with content containing "<script>alert('xss')</script>"
  Then the content is sanitized before saving
  And the saved article has clean HTML
  ```

---

### Task 3: Create HTML Sanitization Utility

- **Purpose**: Strip XSS vectors from rich text content before storage.
- **Artifacts impacted**: `backend/app/core/sanitizers.py`.
- **Test types**: Unit tests (sanitization logic).
- **BDD Acceptance (Given-When-Then)**:
  ```gherkin
  Given an HTML sanitizer utility
  When sanitize() is called with "<p>Safe text</p>"
  Then it returns "<p>Safe text</p>" unchanged

  When sanitize() is called with "<script>alert('xss')</script><p>Text</p>"
  Then it returns "<p>Text</p>" (script tag removed)

  When sanitize() is called with "<iframe src='evil'></iframe><p>Text</p>"
  Then it returns "<p>Text</p>" (iframe removed)

  When sanitize() is called with "<p onclick='alert()'>Text</p>"
  Then it returns "<p>Text</p>" (onclick attribute removed)
  ```

---

### Task 4: Create FastAPI Router and Endpoint

- **Purpose**: Expose the POST /api/v1/news endpoint with RBAC protection.
- **Artifacts impacted**: `backend/app/presentation/routers/news.py`.
- **Test types**: Integration tests (endpoint with mocked dependencies and real Pydantic validation).
- **BDD Acceptance (Given-When-Then)**:
  ```gherkin
  Given a FastAPI router with POST /api/v1/news endpoint
  When an Admin user sends POST /api/v1/news with valid CreateNewsRequest
  Then the endpoint returns HTTP 201 Created
  And the response body is NewsResponse with the created article

  When a non-Admin user (Member) sends POST /api/v1/news
  Then the endpoint returns HTTP 403 Forbidden

  When an unauthenticated user sends POST /api/v1/news
  Then the endpoint returns HTTP 401 Unauthorized

  When a user sends POST /api/v1/news with missing title
  Then the endpoint returns HTTP 422 Unprocessable Entity
  And the response includes a validation error message

  When a user sends POST /api/v1/news with XSS content
  Then the endpoint returns HTTP 201
  And the stored content is sanitized
  ```

---

### Task 5: Integration Test Suite

- **Purpose**: Test the entire flow (endpoint → use case → repository → database) with a test database.
- **Artifacts impacted**: `backend/tests/integration/test_news_create.py`.
- **Test types**: Integration tests (against test PostgreSQL instance via docker-compose).
- **BDD Acceptance (Given-When-Then)**:
  ```gherkin
  Feature: Create News Article Integration

    Scenario: Admin creates article successfully
      Given the test database is clean
      And a user with Admin role exists
      When the Admin calls POST /api/v1/news with valid data
      Then the article is created in the database
      And the response contains the article id
      And the article has status DRAFT

    Scenario: Article is created with correct timestamps
      Given the test database is clean
      When an article is created
      Then created_at and updated_at are set to current timestamp
      And published_at is null (not yet published)

    Scenario: XSS content is sanitized on creation
      Given the test database is clean
      When an article is created with content containing script tags
      Then the content is stored without script tags
  ```

---

## Summary of Deliverables

1. **Pydantic DTOs** (CreateNewsRequest, NewsResponse) with validation.
2. **CreateNewsUseCase** orchestrating entity creation and persistence.
3. **HTML Sanitization Utility** (using bleach/markupsafe).
4. **FastAPI Router** with POST /api/v1/news endpoint and RBAC.
5. **Unit tests** for DTOs, use case, and sanitizer.
6. **Integration tests** covering happy path, edge cases, security.
7. **Documentation** in code comments linking to feature/story/ticket.

## Key Traceability
```python
# [Feature: News Management] [Story: NM-ADMIN-001] [Ticket: NM-ADMIN-001-BE-T02]
def create_news(...):
    """Create a new news article (POST /api/v1/news)."""
    ...
```
