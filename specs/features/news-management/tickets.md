# News Management — Implementation Tickets

## Feature Recap
The News Management module enables the association to publish and manage news articles with role-based visibility control (General vs Internal). Administrators perform CRUD operations; Members see all published content; Visitors/Supporters see only General content.

## Global Dependencies
- **User Management**: Must be implemented (authentication, roles: ADMIN, MEMBER, SUPPORTER).
- **Database**: PostgreSQL with Alembic migrations.
- **Backend**: FastAPI with Clean/Hexagonal Architecture.
- **Frontend**: React SPA (out of scope for backend-only tickets).

---

### Story: NM-ADMIN-001 — Create News Article
**Source**: `user-stories.md`
**Key Scenarios**: `@happy-path` (full fields, minimal fields), `@edge-case` (missing required fields), `@security` (non-admin blocked, XSS sanitization)

#### Tickets for NM-ADMIN-001

1. - [ ] **NM-ADMIN-001-DB-T01 — Create News Article Table and Migration**
   - **Type**: DB
   - **Description**: Create the `news_articles` table with all required columns (id, title, summary, content, status, scope, author_id, cover_url, tags, published_at, created_at, updated_at, is_deleted). Add indexes on status, scope, published_at, and is_deleted for efficient querying.
   - **Scope**:
     - Included: Alembic migration, SQLAlchemy model, enum types (NewsStatus, NewsScope), foreign key to users table, indexes.
     - Excluded: Seed data, test data factories.
   - **Dependencies**: User Management DB schema (users table must exist for FK).
   - **Deliverables**:
     - Alembic migration file for `news_articles` table.
     - SQLAlchemy model in `infrastructure/`.
     - Domain entity and enum definitions in `domain/`.
     - Repository interface (port) in `domain/`.

2. - [ ] **NM-ADMIN-001-BE-T02 — Create News Article Endpoint**
   - **Type**: BE
   - **Description**: Implement POST `/api/v1/news` endpoint that allows Admins to create news articles. Enforces RBAC (Admin only), validates input via Pydantic DTOs, sanitizes rich text content (XSS prevention), and persists via the repository.
   - **Scope**:
     - Included: Router, Pydantic request/response DTOs, use case, repository implementation, RBAC dependency, HTML sanitization utility, unit and integration tests.
     - Excluded: Frontend form, file upload for cover image.
   - **Dependencies**: NM-ADMIN-001-DB-T01 (table and model must exist).
   - **Deliverables**:
     - FastAPI router with POST endpoint.
     - Pydantic DTOs (CreateNewsRequest, NewsResponse).
     - CreateNewsUseCase in `application/`.
     - NewsRepository implementation in `infrastructure/`.
     - HTML sanitizer utility.
     - Tests: unit (use case logic, sanitization), integration (endpoint with DB).

3. - [ ] **NM-ADMIN-001-FE-T03 — Create News Article Form (Frontend)**
   - **Type**: FE
   - **Description**: Build the admin form for creating news articles with title, summary, rich text editor for content, scope selector (GENERAL/INTERNAL), cover URL input, and tags input. Integrates with the POST endpoint.
   - **Scope**:
     - Included: Form component, validation (Zod), API integration (React Query), routing, success/error feedback.
     - Excluded: Rich text editor library selection (assumed available).
   - **Dependencies**: NM-ADMIN-001-BE-T02 (endpoint must exist).
   - **Deliverables**:
     - Create News form component.
     - Zod validation schema.
     - React Query mutation hook.
     - Route registration and navigation link.
     - Component tests.

---

### Story: NM-ADMIN-002 — Edit News Article
**Source**: `user-stories.md`
**Key Scenarios**: `@happy-path` (edit draft, edit published), `@edge-case` (non-existent, soft-deleted), `@security` (non-admin blocked)

#### Tickets for NM-ADMIN-002

1. - [ ] **NM-ADMIN-002-BE-T01 — Edit News Article Endpoint**
   - **Type**: BE
   - **Description**: Implement PUT `/api/v1/news/{article_id}` endpoint that allows Admins to update news article fields. Enforces RBAC, validates input, sanitizes content, handles not-found and soft-deleted cases.
   - **Scope**:
     - Included: Router, Pydantic DTOs (UpdateNewsRequest), use case, repository update method, unit and integration tests.
     - Excluded: Partial updates (PATCH), frontend.
   - **Dependencies**: NM-ADMIN-001-DB-T01, NM-ADMIN-001-BE-T02 (table, model, and repository must exist).
   - **Deliverables**:
     - FastAPI router with PUT endpoint.
     - Pydantic DTO (UpdateNewsRequest).
     - UpdateNewsUseCase in `application/`.
     - Repository update method.
     - Tests: unit (use case, edge cases), integration (endpoint).

2. - [ ] **NM-ADMIN-002-FE-T02 — Edit News Article Form (Frontend)**
   - **Type**: FE
   - **Description**: Build the admin form for editing existing news articles, pre-populated with current data. Integrates with the PUT endpoint.
   - **Scope**:
     - Included: Edit form component (reusing Create form), API integration, routing with article_id param, success/error feedback.
     - Excluded: Inline editing, version conflict resolution.
   - **Dependencies**: NM-ADMIN-002-BE-T01.
   - **Deliverables**:
     - Edit News form component.
     - React Query mutation hook for update.
     - Route registration.
     - Component tests.

---

### Story: NM-ADMIN-003 — Publish / Archive News Article
**Source**: `user-stories.md`
**Key Scenarios**: `@happy-path` (publish draft, archive published), `@edge-case` (invalid transitions), `@security` (non-admin blocked)

#### Tickets for NM-ADMIN-003

1. - [ ] **NM-ADMIN-003-BE-T01 — State Transition Endpoint**
   - **Type**: BE
   - **Description**: Implement PATCH `/api/v1/news/{article_id}/status` endpoint that allows Admins to transition article status. Enforces valid transitions (DRAFT->PUBLISHED, PUBLISHED->ARCHIVED only). Sets published_at on publish.
   - **Scope**:
     - Included: Router, Pydantic DTO (ChangeStatusRequest), use case with state machine validation, repository method, unit and integration tests.
     - Excluded: Batch status changes, undo/revert.
   - **Dependencies**: NM-ADMIN-001-DB-T01, NM-ADMIN-001-BE-T02.
   - **Deliverables**:
     - FastAPI router with PATCH endpoint.
     - Pydantic DTO (ChangeStatusRequest).
     - ChangeNewsStatusUseCase with state transition validation.
     - Tests: unit (valid/invalid transitions), integration (endpoint).

2. - [ ] **NM-ADMIN-003-FE-T02 — Status Action Buttons (Frontend)**
   - **Type**: FE
   - **Description**: Add Publish and Archive action buttons to the admin news detail/list view. Includes confirmation dialogs and API integration.
   - **Scope**:
     - Included: Action buttons component, confirmation dialog, API integration (React Query), visual state indicators.
     - Excluded: Bulk status changes.
   - **Dependencies**: NM-ADMIN-003-BE-T01.
   - **Deliverables**:
     - Status action buttons component.
     - React Query mutation hook for status change.
     - Component tests.

---

### Story: NM-ADMIN-004 — Soft Delete News Article
**Source**: `user-stories.md`
**Key Scenarios**: `@happy-path` (soft delete), `@edge-case` (already deleted), `@security` (non-admin blocked), `@observability` (audit log)

#### Tickets for NM-ADMIN-004

1. - [ ] **NM-ADMIN-004-BE-T01 — Soft Delete Endpoint**
   - **Type**: BE
   - **Description**: Implement DELETE `/api/v1/news/{article_id}` endpoint that soft-deletes a news article (sets is_deleted=true). Enforces RBAC, handles already-deleted, logs deletion event.
   - **Scope**:
     - Included: Router, use case, repository soft-delete method, audit logging, unit and integration tests.
     - Excluded: Hard delete, bulk delete, undo.
   - **Dependencies**: NM-ADMIN-001-DB-T01, NM-ADMIN-001-BE-T02.
   - **Deliverables**:
     - FastAPI router with DELETE endpoint.
     - SoftDeleteNewsUseCase.
     - Repository soft-delete method.
     - Audit log entry on deletion.
     - Tests: unit, integration.

2. - [ ] **NM-ADMIN-004-FE-T02 — Delete Button with Confirmation (Frontend)**
   - **Type**: FE
   - **Description**: Add a delete button to the admin news list/detail view with confirmation dialog. Integrates with the DELETE endpoint.
   - **Scope**:
     - Included: Delete button, confirmation modal, API integration, list refresh on success.
     - Excluded: Undo/restore UI.
   - **Dependencies**: NM-ADMIN-004-BE-T01.
   - **Deliverables**:
     - Delete button with confirmation component.
     - React Query mutation hook.
     - Component tests.

---

### Story: NM-MEMBER-001 — View News Detail (All Scopes)
**Source**: `user-stories.md`
**Key Scenarios**: `@happy-path` (view GENERAL, view INTERNAL), `@edge-case` (non-existent, draft, soft-deleted)

#### Tickets for NM-MEMBER-001

1. - [ ] **NM-MEMBER-001-BE-T01 — Get News Detail Endpoint**
   - **Type**: BE
   - **Description**: Implement GET `/api/v1/news/{article_id}` endpoint that returns the full detail of a published news article. Enforces scope-based visibility: Members see GENERAL + INTERNAL; Visitors/Supporters see only GENERAL. Draft, archived, and soft-deleted articles return 404.
   - **Scope**:
     - Included: Router, use case, repository query with scope filtering, role-based visibility logic, unit and integration tests.
     - Excluded: View count tracking (future enhancement).
   - **Dependencies**: NM-ADMIN-001-DB-T01, NM-ADMIN-001-BE-T02.
   - **Deliverables**:
     - FastAPI router with GET endpoint.
     - Pydantic response DTO (NewsDetailResponse).
     - GetNewsDetailUseCase with role-based scope filtering.
     - Repository method.
     - Tests: unit (role filtering logic), integration (endpoint per role).

2. - [ ] **NM-MEMBER-001-FE-T02 — News Detail Page (Frontend)**
   - **Type**: FE
   - **Description**: Build the news detail page displaying full article content with cover image, title, summary, content, tags, published date, and author. Accessible (WCAG 2.1 AA).
   - **Scope**:
     - Included: Detail page component, API integration (React Query), routing, a11y (heading hierarchy, alt text, keyboard nav).
     - Excluded: Comments, reactions, share buttons.
   - **Dependencies**: NM-MEMBER-001-BE-T01.
   - **Deliverables**:
     - News detail page component.
     - React Query query hook.
     - Route registration.
     - A11y compliance (heading hierarchy, alt text).
     - Component tests.

---

### Story: NM-VISITOR-001 — View News Detail (General Only)
**Source**: `user-stories.md`
**Key Scenarios**: `@happy-path` (Visitor/Supporter view GENERAL), `@security` (INTERNAL blocked for both)

> **Note**: This story is covered by the same endpoint as NM-MEMBER-001 (GET `/api/v1/news/{article_id}`), with role-based filtering. No additional tickets are needed — the BE-T01 from NM-MEMBER-001 handles both Member and Visitor/Supporter access.

---

### Story: NM-VISITOR-002 — List Published News Articles
**Source**: `user-stories.md`
**Key Scenarios**: `@happy-path` (Visitor list, Member list, title search, Admin list all), `@edge-case` (empty results), `@performance` (< 500ms P95), `@security` (no INTERNAL leak)

#### Tickets for NM-VISITOR-002

1. - [ ] **NM-VISITOR-002-BE-T01 — List News Articles Endpoint**
   - **Type**: BE
   - **Description**: Implement GET `/api/v1/news` endpoint that returns a paginated, sorted list of published news articles. Filters by scope based on user role. Supports title search, pagination (skip/limit), and sorting (published_at DESC). Admin sees all statuses.
   - **Scope**:
     - Included: Router, use case, repository list method with filtering/pagination/search, Pydantic response DTOs (paginated), role-based scope filtering at query level, performance optimization (indexes), unit and integration tests.
     - Excluded: Full-text search, category filtering, date range filtering.
   - **Dependencies**: NM-ADMIN-001-DB-T01, NM-ADMIN-001-BE-T02.
   - **Deliverables**:
     - FastAPI router with GET endpoint.
     - Pydantic DTOs (NewsListResponse, PaginatedNewsResponse).
     - ListNewsUseCase with role-based filtering.
     - Repository list method with pagination, sorting, search, scope filtering.
     - Tests: unit, integration (per role, pagination, search, performance).

2. - [ ] **NM-VISITOR-002-FE-T02 — News List Page (Frontend)**
   - **Type**: FE
   - **Description**: Build the news list page with paginated cards showing title, summary, cover image, published date, and scope badge. Includes search bar. Responsive and accessible (WCAG 2.1 AA).
   - **Scope**:
     - Included: List page component, news card component, search input, pagination controls, API integration (React Query), routing, a11y.
     - Excluded: Infinite scroll, advanced filters.
   - **Dependencies**: NM-VISITOR-002-BE-T01.
   - **Deliverables**:
     - News list page component.
     - News card component.
     - Search input component.
     - Pagination component.
     - React Query query hook.
     - Route registration.
     - Component tests.

---

### Story: NM-MEMBER-002 — List Internal News Articles
**Source**: `user-stories.md`
**Key Scenarios**: `@happy-path` (Member filters INTERNAL), `@security` (Supporter/Visitor get empty)

> **Note**: This story is covered by the same endpoint as NM-VISITOR-002 (GET `/api/v1/news`) with a `scope` query parameter filter. The role-based filtering in BE-T01 ensures Supporters/Visitors cannot access INTERNAL articles. No additional tickets are needed.
