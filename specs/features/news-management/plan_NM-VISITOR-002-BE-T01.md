# NM-VISITOR-002-BE-T01 — Implementation Plan

**Source ticket**: `specs/features/news-management/tickets.md` → **NM-VISITOR-002-BE-T01**  
**Related user story**: **NM-VISITOR-002** and **NM-MEMBER-002** (from `specs/features/news-management/user-stories.md`)  
**Plan version**: v1.0 — List News Articles Endpoint  
**Traceability**: All tasks reference `NM-VISITOR-002-BE-T01`, `NM-VISITOR-002`, and `NM-MEMBER-002`.

---

## 1) Context & Objective

**Ticket Summary:**
Implement the GET `/api/v1/news` endpoint to retrieve a paginated, date-sorted list of published news articles with role-based scope filtering. The endpoint:
- Supports **pagination** (skip/limit query parameters).
- Supports **sorting** by `published_at` descending (most recent first).
- Supports **title search** (case-insensitive ILIKE).
- Supports **scope filter** (optional `scope` query parameter for Members to filter by INTERNAL).
- **Role-based visibility**: Visitors/Supporters see only GENERAL; Members see GENERAL+INTERNAL; Admins see all statuses.
- Returns HTTP 200 with paginated response including total count, limit, offset, and article list.
- **Performance**: Must respond in < 500ms (P95) even with 1000 articles in the database.

**Impacted services/modules:**
- `backend/app/presentation/routers/news.py` — GET /api/v1/news endpoint.
- `backend/app/presentation/schemas/news.py` — Pydantic response DTOs (PaginatedNewsResponse, NewsCardResponse).
- `backend/app/application/use_cases/list_news.py` — ListNewsUseCase with filtering/pagination/search.
- `backend/app/infrastructure/repositories/news_repository.py` — Repository list method with advanced filtering.

**Impacted tests:**
- Happy path: Visitor list (GENERAL only), Member list (GENERAL+INTERNAL), Admin list (all statuses).
- Filtering: Title search, scope filter.
- Pagination: First page, middle page, last page, empty results.
- Performance: 1000 articles respond in < 500ms.
- Security: INTERNAL articles never leak to non-members.

---

## 2) Scope

### In scope
- FastAPI router with GET `/api/v1/news` endpoint.
- Query parameters: `skip` (default 0), `limit` (default 20), `q` (title search), `scope` (optional filter).
- Pydantic response DTOs: PaginatedNewsResponse (with total, limit, offset), NewsCardResponse (title, summary, cover_url, published_at, scope, tags).
- Role-based filtering: Visitors/Supporters see only GENERAL+PUBLISHED; Members see GENERAL+INTERNAL+PUBLISHED; Admins see all.
- Title search: Case-insensitive ILIKE query on title and summary.
- Sorting: By published_at DESC (most recent first).
- Database indexes for performance: Composite index on (scope, status, is_deleted, published_at).
- Unit and integration tests including performance verification.

### Out of scope
- Full-text search (ILIKE is sufficient for this iteration).
- Category or tag filtering (can be added later).
- Date range filtering.
- Infinite scroll (pagination is explicit).

### Assumptions
- Limit is capped at 100 to prevent DoS-like large payload requests.
- Search query is exact-matched on title/summary (ILIKE for case-insensitivity).
- Performance budget is validated with synthetic data (1000 articles).

---

## 3) Detailed Work Plan (TDD + BDD)

### 3.1 Test-first sequencing
1. Define unit tests for filtering/pagination logic.
2. Define integration tests for endpoint per role, pagination, search, performance.
3. Implement use case, repository list method, endpoint.
4. Run and verify all tests pass; measure performance with 1000 articles.

### 3.2 NFR hooks
- **Performance**: Composite index on (scope, status, is_deleted, published_at) enables efficient queries. Pagination prevents large result sets.
- **Security**: Scope-based visibility enforced at query level (not post-query filtering).
- **Observability**: Log list queries with filters, user_role, result_count, query_time_ms.

---

## 4) Atomic Task Breakdown

### Task 1: Create Repository List Method with Advanced Filtering
- **Purpose**: Build a database query that efficiently filters by scope, status, soft-delete, search, and pagination.
- **Artifacts impacted**: `backend/app/domain/ports/news_repository.py`, `backend/app/infrastructure/repositories/news_repository.py`.
- **Test types**: Integration tests (against test PostgreSQL).
- **BDD Acceptance (Given-When-Then)**:
  ```gherkin
  Given a repository with published GENERAL and INTERNAL articles
  When list(skip=0, limit=10, scope_filter=GENERAL, status_filter=PUBLISHED) is called
  Then 10 GENERAL articles are returned, sorted by published_at DESC

  When list(skip=10, limit=10, ...) is called
  Then the next 10 articles are returned (pagination works)

  When list(..., search_query="Fiesta") is called
  Then only articles with "Fiesta" in title or summary are returned

  When list(..., user_role=VISITOR) is called
  Then only GENERAL articles are returned

  When list(..., user_role=MEMBER) is called
  Then GENERAL and INTERNAL articles are returned

  When list(..., user_role=ADMIN) is called
  Then all statuses (DRAFT, PUBLISHED, ARCHIVED) are returned
  ```

---

### Task 2: Create ListNewsUseCase
- **Purpose**: Orchestrate list logic with role-based filtering and search.
- **Artifacts impacted**: `backend/app/application/use_cases/list_news.py`.
- **Test types**: Unit tests.
- **BDD Acceptance (Given-When-Then)**:
  ```gherkin
  Given a ListNewsUseCase with a mocked repository
  When execute(skip=0, limit=20, user_role=MEMBER, search_query="Aviso") is called
  Then the repository.list() is called with appropriate filters
  And the use case returns a paginated response with results and metadata

  When execute(..., limit=150) is called
  Then the limit is capped at 100 (DoS prevention)
  ```

---

### Task 3: Create Pydantic Response DTOs
- **Purpose**: Define the paginated response schema.
- **Artifacts impacted**: `backend/app/presentation/schemas/news.py`.
- **Test types**: Unit tests (Pydantic validation).
- **BDD Acceptance (Given-When-Then)**:
  ```gherkin
  Given a PaginatedNewsResponse DTO
  When created with total=50, limit=20, offset=0, results=[...]
  Then the response has pagination metadata (total, limit, offset)
  And each result item is a NewsCardResponse with title, summary, cover_url, published_at, scope, tags
  ```

---

### Task 4: Create FastAPI GET Endpoint
- **Purpose**: Expose the GET /api/v1/news endpoint with query parameter parsing.
- **Artifacts impacted**: `backend/app/presentation/routers/news.py`.
- **Test types**: Integration tests.
- **BDD Acceptance (Given-When-Then)**:
  ```gherkin
  Given a FastAPI router with GET /api/v1/news endpoint
  When a Visitor sends GET /api/v1/news?skip=0&limit=10
  Then the endpoint returns HTTP 200 with 10 GENERAL articles
  And pagination metadata shows total count, limit, offset

  When a Member sends GET /api/v1/news?q=Fiesta
  Then the endpoint returns articles matching "Fiesta" in title/summary (all scopes visible to Member)

  When a Member sends GET /api/v1/news?scope=INTERNAL
  Then the endpoint returns only INTERNAL articles

  When a Visitor sends GET /api/v1/news?scope=INTERNAL
  Then the endpoint returns empty list (or filters are ignored, Visitor sees only GENERAL)

  When a user sends GET /api/v1/news?limit=200
  Then the limit is capped at 100

  When there are no articles matching filters
  Then the endpoint returns HTTP 200 with empty list and total=0
  ```

---

### Task 5: Integration Test Suite (including Performance)
- **Purpose**: Test the entire flow and verify performance budget.
- **Artifacts impacted**: `backend/tests/integration/test_news_list.py`.
- **Test types**: Integration tests.
- **BDD Acceptance**:
  ```gherkin
  Feature: List News Articles

    Scenario: Visitor lists published news
      Given 15 published articles (10 GENERAL, 5 INTERNAL) in the database
      When a Visitor sends GET /api/v1/news?limit=10
      Then the endpoint returns HTTP 200
      And 10 GENERAL articles are returned
      And no INTERNAL articles are included
      And pagination shows total=10

    Scenario: Member lists published news
      Given the same 15 articles
      When a Member sends GET /api/v1/news?limit=10
      Then up to 10 articles (mix of GENERAL and INTERNAL) are returned
      And pagination shows correct total count

    Scenario: Search filters results
      Given articles with titles "Fiesta del Barrio", "Obras en la Calle", "Fiesta Privada"
      When a Visitor sends GET /api/v1/news?q=Fiesta
      Then articles with "Fiesta" in title are returned
      And "Obras en la Calle" is not included

    Scenario: Performance budget is met
      Given 1000 published articles in the database
      When a Visitor sends GET /api/v1/news?limit=20
      Then the endpoint responds in less than 500ms (P95)

    Scenario: Admin lists all statuses
      Given articles in DRAFT, PUBLISHED, ARCHIVED statuses
      When an Admin sends GET /api/v1/news
      Then articles in all statuses are returned

    Scenario: Scope filter works for Members
      Given published GENERAL and INTERNAL articles
      When a Member sends GET /api/v1/news?scope=INTERNAL
      Then only INTERNAL articles are returned
  ```

---

### Task 6: Performance Verification and Optimization
- **Purpose**: Ensure composite index is in place and queries are optimal.
- **Artifacts impacted**: Backend database configuration, Alembic migrations, repository queries.
- **Test types**: Performance tests with 1000 synthetic articles.
- **Verification steps**:
  - Verify composite index on (scope, status, is_deleted, published_at) is created in DB migration.
  - Run load test with 1000 articles, measure P95 latency.
  - If > 500ms, analyze query plan (EXPLAIN) and optimize (e.g., additional indexes, query restructuring).

---

## Summary of Deliverables

1. **Repository list method** with advanced filtering, pagination, search.
2. **ListNewsUseCase** with role-based filtering and pagination logic.
3. **Pydantic response DTOs** (PaginatedNewsResponse, NewsCardResponse).
4. **FastAPI GET endpoint** with query parameter parsing.
5. **Unit and integration tests** covering all scenarios, roles, pagination, search.
6. **Performance verification** confirming < 500ms P95 with 1000 articles.
