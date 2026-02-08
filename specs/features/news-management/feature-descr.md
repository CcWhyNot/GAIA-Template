# News Management (Módulo de Noticias) — Feature Description

## 0) Feature Name & Summary
**Feature Name:** News Management (Módulo de Noticias)

**Executive Summary:**
- **Problem:** The community currently relies on fragmented channels (posters, social media, word of mouth), leading to misinformation or members missing critical updates.
- **Opportunity:** To establish the Association App as the "single source of truth" for neighborhood information, offering targeted content based on membership status.
- **Expected Outcome:** Increased community engagement, transparency in association actions, and efficient dissemination of both public and internal operational news.

**Fit with Vision / Product Goal:**
This feature directly supports the core mission of "fostering better communication and transparency between the board and the neighbors" by providing a reliable, official, and accessible communication channel.

---

## 1) Description of the Feature
The News Management module allows the Association to publish relevant information for the neighborhood and the organization itself. It provides a simple publishing workflow for Administrators and an efficient reading experience for all other profiles (Members, Supporters, Visitors).

The core capability is to create, edit, publish, and delete news articles, with a strict distinction between "General Neighborhood" news (visible to arguably everyone) and "Internal Association" news (restricted to paid members). It enforces Role-Based Access Control (RBAC) to ensure information reaches the right audience without exposing sensitive internal matters to the public.

---

## 2) Users/Roles & Impacted Personas

| Role/Persona | Key Objectives | Tasks / Jobs-to-be-done | Current Pain | Stakeholders |
|---|---|---|---|---|
| **Administrator** | Effective communication | Create, edit, publish, archive, and delete news. Manage visibility (General vs Internal). | Communicating via multiple manual channels is time-consuming and error-prone. | Board of Directors |
| **Member (Socio)** | Stay informed on all matters | Read all news (both General and Internal). Access exclusive member updates. | Feels disconnected from internal decisions or pays fees without seeing value. | — |
| **Supporter (Simpatizante)** | Know what is happening in the neighborhood | Read General Neighborhood news. | Misses public events or general alerts. | — |
| **Visitor (Unregistered)** | Get general info | Read General Neighborhood news. | Has no easy way to know about the association's public activities. | — |

---

## 3) Problem / Opportunity Statement
**Context:** The neighborhood association generates two types of information: general interest (festivities, works, security) and internal interest (assemblies, accounts, internal voting).

**Problem Statement:** Our **community members** experience **confusion and lack of information** when **news is scattered across multiple unconnected channels**, which causes **low participation and trust** in the association.

**Why Now:** Launching the app without a communication channel would limit its utility to just "admin tasks" (payments/voting), missing the chance to drive daily engagement.

---

## 4) Objectives & Business Outcomes

| Objective / Outcome | KPI / Metric | Baseline | Target | Time Horizon | Measurement Method |
|---|---|---|---|---|---|
| **Increase Reach** | % of active users who view at least 1 news item/week | 0% (New) | > 40% | Q1 Post-Launch | Analytics events |
| **Timely Communication** | Avg. time from "Draft" to "Published" | N/A | < 10 min | Q1 | System logs |
| **Member Value** | Engagement with "Internal" news vs General | N/A | > 20% of Member sessions | Q2 | Analytics (Page views by scope) |

---

## 5) Scope (In/Out)

**In scope:**
- **CRUD Operations:** Create, Edit, Delete (Soft), View Details, List.
- **Workflow States:** Draft (Borrador), Published (Publicado), Archived (Archivado).
- **Visibility Scopes:** General Neighborhood (Public) vs. Internal Association (Members Only).
- **Content:** Title, Summary, Rich Text Content, Cover Image (URL), Attachments, Tags.
- **RBAC:** Strict enforcement of visibility based on user role (Visitor/Supporter vs Member vs Admin).
- **Listing:** Pagination, Sorting (Date DESC), Simple Title Search.

**Out of scope:**
- **Interactions:** Comments, Reactions (Likes), Share to Social Media (native integration).
- **Advanced Features:** Push Notifications, Email Newsletters, RSS Feeds.
- **Editorial Workflow:** Review buckets, multi-author approval.
- **Internationalization:** Multi-language support (for this version).

**Key Assumptions:**
- A Rich Text Editor component is available or can be easily integrated into the Frontend.
- "Supporters" (Simpatizantes) are treated effectively as "Public" for news visibility, pending any future "Supporter-only" content.

**Dependencies / Blockers:**
- **User Management:** Must be fully implemented to authenticate Admins and resolve Member vs Supporter roles.

---

## 6) Non-Functional Requirements (NFRs)

### 6.1 Security & Privacy
- **Personal Data (PII):** Author identity (user ID) is stored; no additional PII beyond what User Management already handles.
- **Encryption/Hashing:** All API traffic over TLS 1.2+. No passwords or sensitive hashes in this module.
- **Access Control (RBAC):** Content with scope `INTERNAL` must **never** be returned by the API to unauthenticated users or Supporters. Filtering must happen at the Database/query level, not in the Frontend.
- **Compliance:** GDPR-compliant — author IDs are pseudonymized references. No additional PII collection.
- **Audit & Sensitive Logs:** Logging of who created/edited/deleted news items (Author ID, Timestamp). No PII in logs.
- **Sanitization:** All Rich Text input must be sanitized on the backend to prevent stored XSS attacks.

### 6.2 Performance
- **Performance Budgets:** List endpoint must respond in < 500ms (P95).
- **Load/Throughput Limits:** Expected peak of ~50 concurrent reads. Write operations are admin-only and low-frequency.
- **Query/Index Efficiency:** Index on `status`, `scope`, `published_at`, `is_deleted` columns for efficient filtering and sorting.

### 6.3 Availability & Reliability
- **SLO/SLA/SLI:** Standard application SLO (99.5% uptime target for the news module).
- **Graceful Degradation:** If the news service is temporarily unavailable, the app should display a user-friendly error, not crash.

### 6.4 Accessibility (a11y) & Internationalization (i18n)
- **Accessibility:** WCAG 2.1 AA compliance. News detail and list views must be readable by screen readers (proper heading hierarchy `h1`-`h6`, alt text for cover images, keyboard navigable).
- **Languages/Locales:** UI strings in Spanish (Castilian). Code entities in English. No multi-language content support in this version.

### 6.5 Observability
- **Metrics:** Track views on Detail page to measure engagement. Track creation/publication rates.
- **Logs:** Structured JSON logs with correlation ID per request. Log level INFO for CRUD operations, WARN for authorization denials.
- **Traces:** Standard request tracing via middleware.
- **Alerts:** Alert on sustained error rate > 5% on news endpoints over 5-minute window.

---

## Annexes

### Data Model Proposal

| Field | Type | Description |
|---|---|---|
| `id` | UUID | Primary key |
| `title` | string (max 255) | News article title |
| `summary` | string (max 500) | Short summary / excerpt |
| `content` | text | Rich text content (sanitized HTML) |
| `status` | enum: `DRAFT`, `PUBLISHED`, `ARCHIVED` | Publication workflow state |
| `scope` | enum: `GENERAL`, `INTERNAL` | Visibility scope |
| `author_id` | UUID (FK to User) | Reference to the author |
| `cover_url` | string (nullable) | URL to cover image |
| `tags` | string[] | Categorization tags |
| `published_at` | datetime (nullable) | Timestamp when published |
| `created_at` | datetime | Creation timestamp |
| `updated_at` | datetime | Last update timestamp |
| `is_deleted` | boolean (default: false) | Soft delete flag |

### Open Questions
- Should Supporters eventually have a dedicated visibility scope, or remain treated as "Public" indefinitely?
- Should archived news be visible to any user, or only to Admins?
- Maximum attachment count/size per news article?
