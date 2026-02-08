# NM-ADMIN-003-BE-T01 — Implementation Plan

**Source ticket**: `specs/features/news-management/tickets.md` → **NM-ADMIN-003-BE-T01**  
**Related user story**: **NM-ADMIN-003** (from `specs/features/news-management/user-stories.md`)  
**Plan version**: v1.0 — State Transition Endpoint  
**Traceability**: All tasks reference `NM-ADMIN-003-BE-T01` and `NM-ADMIN-003`.

---

## 1) Context & Objective

**Ticket Summary:**
Implement the PATCH `/api/v1/news/{article_id}/status` endpoint for Administrators to transition article status. The endpoint:
- Enforces RBAC (Admin-only).
- Enforces valid state transitions: DRAFT → PUBLISHED, PUBLISHED → ARCHIVED only.
- Invalid transitions return HTTP 422 Unprocessable Entity.
- Sets `published_at` timestamp when transitioning to PUBLISHED.
- Returns HTTP 200 with the updated article on success.

**Impacted services/modules:**
- `backend/app/presentation/routers/news.py` — PATCH endpoint.
- `backend/app/presentation/schemas/news.py` — Pydantic DTO (ChangeStatusRequest).
- `backend/app/application/use_cases/change_news_status.py` — ChangeNewsStatusUseCase with state machine.
- `backend/app/domain/value_objects/news_status.py` — NewsStatus enum and state transition logic.

**Impacted tests:**
- Happy path: Publish draft, archive published.
- Edge cases: Invalid transitions (DRAFT → ARCHIVED, ARCHIVED → PUBLISHED) return 422.
- Security: Non-admin blocked (403).

---

## 2) Scope

### In scope
- State transition validation (DRAFT → PUBLISHED → ARCHIVED only).
- Setting `published_at` when transitioning to PUBLISHED (if not already set).
- PATCH endpoint with Admin-only RBAC.
- Pydantic DTO for status change request.
- Use case with state machine logic.
- Unit and integration tests.

### Out of scope
- Undo/revert to previous status.
- Batch status changes.
- Scheduled transitions (future enhancement).

### Assumptions
- Valid status transitions are exactly: DRAFT → PUBLISHED, PUBLISHED → ARCHIVED.
- DRAFT articles can only transition to PUBLISHED (not directly to ARCHIVED).
- Archived articles cannot transition back.

---

## 3) Detailed Work Plan (TDD + BDD)

### 3.1 Test-first sequencing
1. Define unit tests for state transition validation.
2. Define integration tests for endpoint (valid transitions, invalid transitions, 403, 404).
3. Implement state machine logic, use case, endpoint.
4. Run and verify all tests pass.

### 3.2 NFR hooks
- **Security**: RBAC (Admin-only). State invariants enforced at domain level.
- **Observability**: Log status transitions with article_id, old_status, new_status, author_id.

---

## 4) Atomic Task Breakdown

### Task 1: Define State Transition Logic in Domain
- **Purpose**: Encapsulate valid state transitions in a domain service or value object.
- **Artifacts impacted**: `backend/app/domain/value_objects/news_status.py` or `backend/app/domain/services/news_state_machine.py`.
- **Test types**: Unit tests.
- **BDD Acceptance (Given-When-Then)**:
  ```gherkin
  Given a NewsStatus value object with status DRAFT
  When can_transition_to(PUBLISHED) is called
  Then it returns True

  When can_transition_to(ARCHIVED) is called
  Then it returns False

  Given a NewsStatus with status PUBLISHED
  When can_transition_to(ARCHIVED) is called
  Then it returns True

  When can_transition_to(DRAFT) is called
  Then it returns False

  Given a NewsStatus with status ARCHIVED
  When can_transition_to(any status) is called
  Then it returns False
  ```

---

### Task 2: Create ChangeNewsStatusUseCase
- **Purpose**: Orchestrate status transition logic (validation, repository update).
- **Artifacts impacted**: `backend/app/application/use_cases/change_news_status.py`.
- **Test types**: Unit tests.
- **BDD Acceptance (Given-When-Then)**:
  ```gherkin
  Given a ChangeNewsStatusUseCase with a mocked repository
  When execute(article_id, new_status=PUBLISHED) is called
  Then the article is retrieved
  And its current status is validated for the transition
  And the article status is updated
  And if transitioning to PUBLISHED, published_at is set to current timestamp
  And the article is saved
  And the use case returns the updated article

  When execute() is called with an invalid transition
  Then the use case raises InvalidStateTransitionError
  ```

---

### Task 3: Create FastAPI PATCH Endpoint
- **Purpose**: Expose the PATCH /api/v1/news/{article_id}/status endpoint.
- **Artifacts impacted**: `backend/app/presentation/routers/news.py`.
- **Test types**: Integration tests.
- **BDD Acceptance (Given-When-Then)**:
  ```gherkin
  Given a FastAPI router with PATCH /api/v1/news/{article_id}/status endpoint
  When an Admin sends PATCH with new_status=PUBLISHED
  Then the endpoint returns HTTP 200 with the updated article
  And the response status field is PUBLISHED
  And published_at is set in the response

  When an Admin sends PATCH with invalid transition (DRAFT to ARCHIVED)
  Then the endpoint returns HTTP 422 Unprocessable Entity

  When a non-Admin sends PATCH
  Then the endpoint returns HTTP 403 Forbidden

  When an unauthenticated user sends PATCH
  Then the endpoint returns HTTP 401 Unauthorized

  When a user sends PATCH with non-existent article_id
  Then the endpoint returns HTTP 404 Not Found
  ```

---

### Task 4: Integration Test Suite
- **Purpose**: Test the entire flow (endpoint → use case → repository → database).
- **Artifacts impacted**: `backend/tests/integration/test_news_state_transitions.py`.
- **Test types**: Integration tests.
- **BDD Acceptance**:
  ```gherkin
  Feature: News Article State Transitions

    Scenario: Admin publishes a draft article
      Given a draft article exists in the database
      When an Admin sends PATCH /api/v1/news/{id}/status with new_status=PUBLISHED
      Then the article status is updated to PUBLISHED
      And published_at is set to current timestamp
      And the response contains the updated article

    Scenario: Admin archives a published article
      Given a published article exists
      When an Admin sends PATCH with new_status=ARCHIVED
      Then the article status is updated to ARCHIVED
      And the response contains the updated article

    Scenario: Invalid transition is rejected
      Given a draft article exists
      When an Admin sends PATCH with new_status=ARCHIVED
      Then the endpoint returns HTTP 422
  ```

---

## Summary of Deliverables

1. **State transition logic** in domain layer.
2. **ChangeNewsStatusUseCase** with validation.
3. **FastAPI PATCH endpoint** with RBAC.
4. **Unit and integration tests**.
