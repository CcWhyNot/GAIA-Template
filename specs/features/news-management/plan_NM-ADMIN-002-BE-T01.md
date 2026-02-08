# NM-ADMIN-002-BE-T01 — Implementation Plan

**Source ticket**: `specs/features/news-management/tickets.md` → **NM-ADMIN-002-BE-T01**  
**Related user story**: **NM-ADMIN-002** (from `specs/features/news-management/user-stories.md`)  
**Plan version**: v1.0 — Edit News Article Endpoint  
**Traceability**: All tasks reference `NM-ADMIN-002-BE-T01` and `NM-ADMIN-002`.

---

## 1) Context & Objective

**Ticket Summary:**
Implement the PUT `/api/v1/news/{article_id}` endpoint for Administrators to edit existing news articles. The endpoint:
- Enforces RBAC (Admin-only access).
- Validates input via Pydantic DTOs.
- Sanitizes rich text content.
- Handles not-found (404) and soft-deleted articles (404).
- Updates the `updated_at` timestamp.
- Returns HTTP 200 with the updated article on success.

**Impacted services/modules:**
- `backend/app/presentation/routers/news.py` — PUT endpoint.
- `backend/app/presentation/schemas/news.py` — Pydantic DTOs (UpdateNewsRequest).
- `backend/app/application/use_cases/update_news.py` — UpdateNewsUseCase.
- `backend/app/infrastructure/repositories/news_repository.py` — Repository update method.

**Impacted tests:**
- Happy path: Admin edits draft, Admin edits published.
- Edge cases: Non-existent article (404), soft-deleted article (404).
- Security: Non-admin blocked (403).

---

## 2) Scope

### In scope
- FastAPI router with PUT `/api/v1/news/{article_id}` endpoint.
- Pydantic request DTO (UpdateNewsRequest) with optional fields.
- UpdateNewsUseCase with repository update method.
- HTML sanitization of updated content.
- RBAC enforcement.
- Unit and integration tests.

### Out of scope
- Partial updates (PATCH) — only full PUT updates.
- Conflict resolution (no optimistic locking).
- Version history / audit trail (audit logs only).

### Assumptions
- Article exists check is handled by repository (returns None if not found or soft-deleted).
- `updated_at` is auto-updated by the database trigger or application code.

---

## 3) Detailed Work Plan (TDD + BDD)

### 3.1 Test-first sequencing
1. Define unit tests for UpdateNewsUseCase.
2. Define integration tests for endpoint (edit draft, edit published, 404, 403).
3. Implement use case, repository method, endpoint.
4. Run and verify all tests pass.

### 3.2 NFR hooks
- **Security**: RBAC (Admin-only). Content sanitization. No unauthorized edits.
- **Observability**: Log updates with article_id, author_id, changes made.

---

## 4) Atomic Task Breakdown

### Task 1: Create UpdateNewsUseCase
- **Purpose**: Orchestrate the business logic for updating a news article.
- **Artifacts impacted**: `backend/app/application/use_cases/update_news.py`.
- **Test types**: Unit tests.
- **BDD Acceptance (Given-When-Then)**:
  ```gherkin
  Given an UpdateNewsUseCase with a mocked repository
  When execute() is called with article_id and updated fields (title, summary, content, scope, cover_url, tags)
  Then the repository is queried for the article
  And if the article exists, it is updated and saved
  And updated_at is refreshed
  And the use case returns the updated article

  When execute() is called with a non-existent article_id
  Then the use case raises ArticleNotFoundError
  ```

---

### Task 2: Add Repository Update Method
- **Purpose**: Add update method to NewsRepository.
- **Artifacts impacted**: `backend/app/domain/ports/news_repository.py`, `backend/app/infrastructure/repositories/news_repository.py`.
- **Test types**: Integration tests.
- **BDD Acceptance (Given-When-Then)**:
  ```gherkin
  Given a repository with an existing article
  When update(article_id, fields) is called with new values
  Then the article is updated in the database
  And updated_at is set to current timestamp
  And the updated article is returned

  When update(article_id, fields) is called with a non-existent id
  Then ArticleNotFoundError is raised
  ```

---

### Task 3: Create FastAPI Router PUT Endpoint
- **Purpose**: Expose the PUT /api/v1/news/{article_id} endpoint.
- **Artifacts impacted**: `backend/app/presentation/routers/news.py`.
- **Test types**: Integration tests.
- **BDD Acceptance (Given-When-Then)**:
  ```gherkin
  Given a FastAPI router with PUT /api/v1/news/{article_id} endpoint
  When an Admin sends PUT with updated data
  Then the endpoint returns HTTP 200 with the updated article

  When a non-Admin sends PUT
  Then the endpoint returns HTTP 403 Forbidden

  When an unauthenticated user sends PUT
  Then the endpoint returns HTTP 401 Unauthorized

  When a user sends PUT with non-existent article_id
  Then the endpoint returns HTTP 404 Not Found

  When a user sends PUT with invalid data
  Then the endpoint returns HTTP 422 Unprocessable Entity
  ```

---

### Task 4: Integration Test Suite
- **Purpose**: Test the entire flow (endpoint → use case → repository → database).
- **Artifacts impacted**: `backend/tests/integration/test_news_update.py`.
- **Test types**: Integration tests.
- **BDD Acceptance**:
  ```gherkin
  Scenario: Admin edits a draft article
    Given a draft article exists
    When an Admin sends PUT /api/v1/news/{id} with updated title
    Then the article is updated
    And the response contains the updated article

  Scenario: Admin edits a published article
    Given a published article exists
    When an Admin sends PUT with updated summary
    Then the article is updated
    And the status remains PUBLISHED
  ```

---

## Summary of Deliverables

1. **UpdateNewsUseCase** with business logic.
2. **Repository update method** in infrastructure.
3. **FastAPI PUT endpoint** with RBAC.
4. **Unit and integration tests**.
