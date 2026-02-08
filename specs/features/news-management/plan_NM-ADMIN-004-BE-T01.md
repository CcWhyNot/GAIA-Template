# NM-ADMIN-004-BE-T01 — Implementation Plan

**Source ticket**: `specs/features/news-management/tickets.md` → **NM-ADMIN-004-BE-T01**  
**Related user story**: **NM-ADMIN-004** (from `specs/features/news-management/user-stories.md`)  
**Plan version**: v1.0 — Soft Delete Endpoint  
**Traceability**: All tasks reference `NM-ADMIN-004-BE-T01` and `NM-ADMIN-004`.

---

## 1) Context & Objective

**Ticket Summary:**
Implement the DELETE `/api/v1/news/{article_id}` endpoint for Administrators to soft-delete news articles. The endpoint:

- Enforces RBAC (Admin-only).
- Sets `is_deleted = true` and updates `updated_at`.
- Already-deleted articles return HTTP 404.
- Logs the deletion event (author_id, article_id, timestamp) for audit purposes.
- Returns HTTP 200 with a confirmation message on success.

**Impacted services/modules:**

- `backend/app/presentation/routers/news.py` — DELETE endpoint.
- `backend/app/application/use_cases/delete_news.py` — SoftDeleteNewsUseCase.
- `backend/app/infrastructure/repositories/news_repository.py` — Soft-delete repository method.
- `backend/app/core/audit_logger.py` — Audit logging utility.

**Impacted tests:**

- Happy path: Admin soft-deletes an article.
- Edge cases: Already deleted (404).
- Security: Non-admin blocked (403), unauthenticated blocked (401).
- Observability: Deletion is audit-logged.

---

## 2) Scope

### In scope

- FastAPI router with DELETE `/api/v1/news/{article_id}` endpoint.
- SoftDeleteNewsUseCase with repository soft-delete method.
- Repository method to set `is_deleted = true` and refresh `updated_at`.
- Audit logging of deletion events (author_id, article_id, timestamp, action).
- RBAC enforcement (Admin-only).
- Unit and integration tests.

### Out of scope

- Hard delete (permanent removal).
- Bulk delete operations.
- Undo/restore UI or functionality.

### Assumptions

- Soft-deleted articles are excluded from all queries by default (handled in repository layer).
- Audit logging is structured JSON; destination is a centralized logger or log aggregation service.

---

## 3) Detailed Work Plan (TDD + BDD)

### 3.1 Test-first sequencing

1. Define unit tests for SoftDeleteNewsUseCase.
2. Define integration tests for endpoint and audit logging.
3. Implement use case, repository method, audit logging, endpoint.
4. Run and verify all tests pass.

### 3.2 NFR hooks

- **Security**: RBAC (Admin-only). Soft-delete prevents accidental permanent loss.
- **Observability**: Audit log captures: author_id (who deleted), article_id, timestamp, action="DELETE", status_code.

---

## 4) Atomic Task Breakdown

### Task 1: Create SoftDeleteNewsUseCase

- **Purpose**: Orchestrate soft-deletion logic (validation, repository update, audit logging).
- **Artifacts impacted**: `backend/app/application/use_cases/delete_news.py`.
- **Test types**: Unit tests.
- **BDD Acceptance (Given-When-Then)**:

    ```gherkin
    Given a SoftDeleteNewsUseCase with a mocked repository and audit logger
    When execute(article_id, admin_user_id) is called
    Then the repository is queried for the article
    And if the article exists and is_deleted=false, the repository soft-deletes it
    And the audit logger is called with deletion event (author_id, article_id, timestamp)
    And the use case returns a success response

    When execute() is called with a non-existent article_id
    Then ArticleNotFoundError is raised
    ```

---

### Task 2: Add Repository Soft-Delete Method

- **Purpose**: Update repository to support soft-delete.
- **Artifacts impacted**: `backend/app/domain/ports/news_repository.py`, `backend/app/infrastructure/repositories/news_repository.py`.
- **Test types**: Integration tests.
- **BDD Acceptance (Given-When-Then)**:

    ```gherkin
    Given a repository with an existing article where is_deleted=false
    When soft_delete(article_id) is called
    Then the article is_deleted field is set to true
    And updated_at is set to current timestamp
    And the article is no longer returned by get_by_id() or list() queries

    When soft_delete(article_id) is called with a non-existent id
    Then ArticleNotFoundError is raised

    When soft_delete(article_id) is called with an already-deleted article
    Then ArticleNotFoundError is raised (not found)
    ```

---

### Task 3: Create Audit Logging Utility

- **Purpose**: Log deletion events for compliance and debugging.
- **Artifacts impacted**: `backend/app/core/audit_logger.py` (or extend existing logging).
- **Test types**: Unit tests.
- **BDD Acceptance (Given-When-Then)**:
    ```gherkin
    Given an audit logger
    When log_deletion(article_id, author_id, timestamp) is called
    Then the logger outputs structured JSON with: {"action": "DELETE", "article_id": "...", "author_id": "...", "timestamp": "...", "module": "news"}
    And the log level is INFO
    ```

---

### Task 4: Create FastAPI DELETE Endpoint

- **Purpose**: Expose the DELETE /api/v1/news/{article_id} endpoint.
- **Artifacts impacted**: `backend/app/presentation/routers/news.py`.
- **Test types**: Integration tests.
- **BDD Acceptance (Given-When-Then)**:

    ```gherkin
    Given a FastAPI router with DELETE /api/v1/news/{article_id} endpoint
    When an Admin sends DELETE request
    Then the endpoint returns HTTP 200 with a deletion confirmation message
    And the response contains the deleted article_id

    When a non-Admin sends DELETE
    Then the endpoint returns HTTP 403 Forbidden

    When an unauthenticated user sends DELETE
    Then the endpoint returns HTTP 401 Unauthorized

    When a user sends DELETE with non-existent article_id
    Then the endpoint returns HTTP 404 Not Found

    When a user sends DELETE with already-deleted article_id
    Then the endpoint returns HTTP 404 Not Found
    ```

---

### Task 5: Integration Test Suite

- **Purpose**: Test the entire flow (endpoint → use case → repository → database → audit log).
- **Artifacts impacted**: `backend/tests/integration/test_news_delete.py`.
- **Test types**: Integration tests.
- **BDD Acceptance**:

    ```gherkin
    Feature: Soft Delete News Article

      Scenario: Admin soft-deletes an article
        Given an article exists with is_deleted=false
        When an Admin sends DELETE /api/v1/news/{id}
        Then the endpoint returns HTTP 200
        And the article is_deleted is now true
        And the article no longer appears in list() queries
        And an audit log entry is created

      Scenario: Deletion of already-deleted article returns 404
        Given an article exists with is_deleted=true
        When an Admin sends DELETE /api/v1/news/{id}
        Then the endpoint returns HTTP 404 Not Found

      Scenario: Deletion is audit-logged
        Given an article exists
        When an Admin deletes it
        Then the audit log contains: action="DELETE", article_id="...", author_id="...", timestamp
    ```

---

## Summary of Deliverables

1. **SoftDeleteNewsUseCase** with business logic.
2. **Repository soft-delete method**.
3. **Audit logging utility**.
4. **FastAPI DELETE endpoint** with RBAC.
5. **Unit and integration tests**.
