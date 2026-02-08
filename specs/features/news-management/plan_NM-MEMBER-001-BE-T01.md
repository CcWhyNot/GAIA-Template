# NM-MEMBER-001-BE-T01 — Implementation Plan

**Source ticket**: `specs/features/news-management/tickets.md` → **NM-MEMBER-001-BE-T01**  
**Related user story**: **NM-MEMBER-001** and **NM-VISITOR-001** (from `specs/features/news-management/user-stories.md`)  
**Plan version**: v1.0 — Get News Detail Endpoint  
**Traceability**: All tasks reference `NM-MEMBER-001-BE-T01`, `NM-MEMBER-001`, and `NM-VISITOR-001`.

---

## 1) Context & Objective

**Ticket Summary:**
Implement the GET `/api/v1/news/{article_id}` endpoint to retrieve the full detail of a published news article. The endpoint enforces role-based scope visibility:
- **Members** can view GENERAL + INTERNAL published articles.
- **Visitors/Supporters** can view only GENERAL published articles.
- **Draft, Archived, and soft-deleted** articles return HTTP 404 to all users (including Admins).
- **INTERNAL articles accessed by non-members** return HTTP 404 (not 403, to avoid information disclosure).
- Returns HTTP 200 with full article data on success.

**Impacted services/modules:**
- `backend/app/presentation/routers/news.py` — GET endpoint.
- `backend/app/presentation/schemas/news.py` — Pydantic response DTO (NewsDetailResponse).
- `backend/app/application/use_cases/get_news_detail.py` — GetNewsDetailUseCase with role-based filtering.
- `backend/app/infrastructure/repositories/news_repository.py` — Repository query method.

**Impacted tests:**
- Happy path: Member views GENERAL, Member views INTERNAL, Visitor views GENERAL.
- Edge cases: Non-existent (404), draft (404), soft-deleted (404).
- Security: Visitor/Supporter views INTERNAL returns 404 (not 403).

---

## 2) Scope

### In scope
- FastAPI router with GET `/api/v1/news/{article_id}` endpoint.
- Pydantic response DTO (NewsDetailResponse) with all article fields.
- GetNewsDetailUseCase with role-based scope filtering logic.
- Repository query method returning article only if PUBLISHED and not soft-deleted.
- RBAC-aware query: Members see GENERAL+INTERNAL; Visitors/Supporters see only GENERAL.
- Unit and integration tests per role.

### Out of scope
- View count tracking (future enhancement).
- Read receipts or bookmark tracking.
- Related articles recommendations.

### Assumptions
- Draft and Archived articles are never visible to any user via this endpoint.
- Soft-deleted articles return 404 (same as non-existent).
- Role information is available from the current user context (JWT claims or database lookup).

---

## 3) Detailed Work Plan (TDD + BDD)

### 3.1 Test-first sequencing
1. Define unit tests for role-based filtering logic.
2. Define integration tests for endpoint per role (Member, Visitor, Supporter).
3. Implement use case, repository query method, endpoint.
4. Run and verify all tests pass.

### 3.2 NFR hooks
- **Security**: Scope-based visibility at query level (database filtering, not post-query filtering).
- **Information Disclosure**: Non-member access to INTERNAL returns 404, not 403 (prevents leaking existence of INTERNAL articles).
- **Accessibility**: Response includes proper heading hierarchy and alt text for cover images.

---

## 4) Atomic Task Breakdown

### Task 1: Define Role-Based Filtering Logic in Domain
- **Purpose**: Encapsulate the visibility rules (which roles can see which scopes).
- **Artifacts impacted**: `backend/app/domain/services/news_visibility.py` or `backend/app/application/policies/`.
- **Test types**: Unit tests.
- **BDD Acceptance (Given-When-Then)**:
  ```gherkin
  Given a NewsVisibility policy service
  When can_view(user_role=MEMBER, article_scope=GENERAL) is called
  Then it returns True

  When can_view(user_role=MEMBER, article_scope=INTERNAL) is called
  Then it returns True

  When can_view(user_role=SUPPORTER, article_scope=GENERAL) is called
  Then it returns True

  When can_view(user_role=SUPPORTER, article_scope=INTERNAL) is called
  Then it returns False

  When can_view(user_role=VISITOR, article_scope=GENERAL) is called
  Then it returns True

  When can_view(user_role=VISITOR, article_scope=INTERNAL) is called
  Then it returns False
  ```

---

### Task 2: Create GetNewsDetailUseCase
- **Purpose**: Orchestrate the business logic for retrieving article detail with visibility checks.
- **Artifacts impacted**: `backend/app/application/use_cases/get_news_detail.py`.
- **Test types**: Unit tests.
- **BDD Acceptance (Given-When-Then)**:
  ```gherkin
  Given a GetNewsDetailUseCase with a mocked repository and visibility policy
  When execute(article_id, user_role=MEMBER) is called
  Then the repository is queried for the article with status=PUBLISHED, is_deleted=false
  And the visibility policy is checked
  And if the user can view the article's scope, it is returned
  And if not, ArticleNotFoundError is raised (or None is returned, treated as 404)

  When execute(article_id, user_role=VISITOR) is called for an INTERNAL article
  Then ArticleNotFoundError is raised (even though it exists)
  ```

---

### Task 3: Add Repository Query Method
- **Purpose**: Query the database for published articles with scope and soft-delete filtering.
- **Artifacts impacted**: `backend/app/infrastructure/repositories/news_repository.py`.
- **Test types**: Integration tests.
- **BDD Acceptance (Given-When-Then)**:
  ```gherkin
  Given a repository with published GENERAL and INTERNAL articles, and draft/archived articles
  When get_by_id(article_id) is called with a published GENERAL article
  Then the article is returned

  When get_by_id(article_id) is called with a draft article
  Then None is returned (not found)

  When get_by_id(article_id) is called with a soft-deleted article
  Then None is returned (not found)

  When get_by_id(article_id) is called with a non-existent id
  Then None is returned (not found)
  ```

---

### Task 4: Create FastAPI GET Endpoint
- **Purpose**: Expose the GET /api/v1/news/{article_id} endpoint.
- **Artifacts impacted**: `backend/app/presentation/routers/news.py`.
- **Test types**: Integration tests.
- **BDD Acceptance (Given-When-Then)**:
  ```gherkin
  Given a FastAPI router with GET /api/v1/news/{article_id} endpoint
  When a Member sends GET request for a published GENERAL article
  Then the endpoint returns HTTP 200 with the article data

  When a Member sends GET request for a published INTERNAL article
  Then the endpoint returns HTTP 200 with the article data

  When a Visitor sends GET request for a published GENERAL article
  Then the endpoint returns HTTP 200 with the article data

  When a Visitor sends GET request for a published INTERNAL article
  Then the endpoint returns HTTP 404 Not Found (not 403)

  When a Supporter sends GET request for an INTERNAL article
  Then the endpoint returns HTTP 404 Not Found

  When a user sends GET for a draft article
  Then the endpoint returns HTTP 404 Not Found

  When a user sends GET for a soft-deleted article
  Then the endpoint returns HTTP 404 Not Found

  When a user sends GET for non-existent article_id
  Then the endpoint returns HTTP 404 Not Found
  ```

---

### Task 5: Integration Test Suite
- **Purpose**: Test the entire flow (endpoint → use case → repository → database) per role.
- **Artifacts impacted**: `backend/tests/integration/test_news_get_detail.py`.
- **Test types**: Integration tests.
- **BDD Acceptance**:
  ```gherkin
  Feature: Get News Article Detail

    Scenario: Member views published GENERAL article
      Given a published GENERAL article exists in the database
      When a Member sends GET /api/v1/news/{id}
      Then the endpoint returns HTTP 200
      And the response contains the full article data

    Scenario: Member views published INTERNAL article
      Given a published INTERNAL article exists
      When a Member sends GET /api/v1/news/{id}
      Then the endpoint returns HTTP 200
      And the response contains the full article data

    Scenario: Visitor views published GENERAL article
      Given a published GENERAL article exists
      When a Visitor (unauthenticated) sends GET /api/v1/news/{id}
      Then the endpoint returns HTTP 200
      And the response contains the article data

    Scenario: Visitor cannot view INTERNAL article
      Given a published INTERNAL article exists
      When a Visitor sends GET /api/v1/news/{id}
      Then the endpoint returns HTTP 404 Not Found

    Scenario: Supporter cannot view INTERNAL article
      Given a published INTERNAL article exists
      When a Supporter sends GET /api/v1/news/{id}
      Then the endpoint returns HTTP 404 Not Found

    Scenario: No one can view draft article
      Given a draft article exists
      When any user sends GET /api/v1/news/{id}
      Then the endpoint returns HTTP 404 Not Found
  ```

---

## Summary of Deliverables

1. **Role-based visibility policy** service in domain layer.
2. **GetNewsDetailUseCase** with visibility checks.
3. **Repository query method** for published articles.
4. **FastAPI GET endpoint** with role-aware responses.
5. **Unit and integration tests** covering all roles and edge cases.
