# Product Requirements Document (PRD)

## Product Vision
A community association application that fosters better communication and transparency between the board and the neighbors, providing tools for management, payments, voting, and communication.

---

## News Management (Módulo de Noticias)

### 1. Feature Name
**News Management (Módulo de Noticias)**

The News Management module provides an official communication channel for the neighborhood association. It covers the creation, editing, publication, and archival of news articles, with strict visibility control based on membership status. It protects internal association information from unauthorized access while ensuring general neighborhood news reaches all audiences.

### 2. Core Entities / Roles / Actors

#### 2.1 Actors
- **Administrator (`ADMIN`)**: Can create, edit, publish, archive, and soft-delete news articles. Manages visibility scope (General vs Internal).
- **Member (`MEMBER`)**: Can read all news articles (both General and Internal scope). Authenticated paid member of the association.
- **Supporter (`SUPPORTER`)**: Can read General Neighborhood news only. Authenticated but non-paying participant.
- **Visitor (`VISITOR`)**: Can read General Neighborhood news only. Unauthenticated user.

### 3. High-Level Rules and Permissions

#### 3.1 Access Levels
- **Public (Visitor, Supporter)**: Can view news with scope `GENERAL` and status `PUBLISHED`.
- **Member+**: Can view news with scope `GENERAL` or `INTERNAL` and status `PUBLISHED`.
- **Admin**: Full CRUD operations on all news articles regardless of scope or status. Can manage workflow transitions (Draft -> Published -> Archived).

### 4. Requirements and Constraints

#### 4.1 Security / Compliance / Quality Requirements
- Content with scope `INTERNAL` must never be returned by the API to unauthenticated users or Supporters. Filtering must be enforced at the database/query level.
- All Rich Text input must be sanitized on the backend to prevent stored XSS attacks.
- RBAC must be verified server-side; frontend controls are cosmetic only.
- Audit logging of all create/edit/delete operations (Author ID, Timestamp).
- GDPR-compliant: author IDs are pseudonymized references.
- List endpoint must respond in < 500ms (P95).
- WCAG 2.1 AA compliance for news views.

**Detailed spec:** `specs/features/news-management/feature-descr.md`
