# News Management — User Stories

## Introduction
These user stories cover the News Management feature, which enables the association to publish and manage news articles with role-based visibility control. They are derived from the feature description in `feature-descr.md` and are aligned with the following objectives:

- **Increase Reach**: > 40% of active users viewing at least 1 news item/week (Q1).
- **Timely Communication**: Avg. draft-to-published time < 10 min (Q1).
- **Member Value**: > 20% of Member sessions engaging with Internal news (Q2).

Acronym: **NM** (News Management)

---

## User Stories

### NM-ADMIN-001 — Create News Article

**As an** Administrator,
**I want to** create a new news article with title, summary, content, cover image, tags, and visibility scope,
**So that** I can draft communications for the neighborhood or the association.

#### Acceptance Criteria

```gherkin
Feature: Create News Article

  @happy-path
  Scenario: Admin creates a news article with all fields
    Given the user is authenticated as an Administrator
    When they submit a new news article with title "Fiesta del Barrio", summary "Celebracion anual", content "<p>Detalles del evento</p>", scope "GENERAL", cover_url "https://example.com/image.jpg", and tags ["eventos", "comunidad"]
    Then the system creates the article with status "DRAFT"
    And the article is assigned the author_id of the current Administrator
    And created_at and updated_at timestamps are recorded
    And the system returns HTTP 201 with the article data

  @happy-path
  Scenario: Admin creates a minimal news article
    Given the user is authenticated as an Administrator
    When they submit a new news article with only title "Aviso importante", summary "Informacion urgente", content "<p>Contenido</p>", and scope "INTERNAL"
    Then the system creates the article with status "DRAFT"
    And cover_url is null and tags is an empty list

  @edge-case
  Scenario: Admin submits article with missing required fields
    Given the user is authenticated as an Administrator
    When they submit a new news article without a title
    Then the system returns HTTP 422 with a validation error

  @security
  Scenario: Non-admin user attempts to create an article
    Given the user is authenticated as a Member
    When they attempt to create a new news article
    Then the system returns HTTP 403 Forbidden

  @security
  Scenario: Unauthenticated user attempts to create an article
    Given the user is not authenticated
    When they attempt to create a new news article
    Then the system returns HTTP 401 Unauthorized

  @security
  Scenario: XSS content is sanitized on creation
    Given the user is authenticated as an Administrator
    When they submit a news article with content "<script>alert('xss')</script><p>Safe</p>"
    Then the system stores the content with the script tag removed
    And the safe HTML content is preserved
```

---

### NM-ADMIN-002 — Edit News Article

**As an** Administrator,
**I want to** edit an existing news article (title, summary, content, scope, cover image, tags),
**So that** I can correct or update information before or after publication.

#### Acceptance Criteria

```gherkin
Feature: Edit News Article

  @happy-path
  Scenario: Admin edits a draft article
    Given the user is authenticated as an Administrator
    And a news article with id "article-uuid" exists with status "DRAFT"
    When they update the title to "Nuevo Titulo" and scope to "INTERNAL"
    Then the system updates the article fields
    And updated_at is refreshed
    And the system returns HTTP 200 with the updated article

  @happy-path
  Scenario: Admin edits a published article
    Given the user is authenticated as an Administrator
    And a news article with id "article-uuid" exists with status "PUBLISHED"
    When they update the summary to "Resumen actualizado"
    Then the system updates the article
    And the status remains "PUBLISHED"
    And updated_at is refreshed

  @edge-case
  Scenario: Admin edits a non-existent article
    Given the user is authenticated as an Administrator
    When they attempt to edit an article with id "non-existent-uuid"
    Then the system returns HTTP 404 Not Found

  @edge-case
  Scenario: Admin edits a soft-deleted article
    Given the user is authenticated as an Administrator
    And a news article with id "deleted-uuid" has is_deleted set to true
    When they attempt to edit the article
    Then the system returns HTTP 404 Not Found

  @security
  Scenario: Non-admin attempts to edit an article
    Given the user is authenticated as a Member
    When they attempt to edit a news article
    Then the system returns HTTP 403 Forbidden
```

---

### NM-ADMIN-003 — Publish / Archive News Article (State Transitions)

**As an** Administrator,
**I want to** change the status of a news article (Draft -> Published, Published -> Archived),
**So that** I can control when content becomes visible and when it is retired.

#### Acceptance Criteria

```gherkin
Feature: News Article State Transitions

  @happy-path
  Scenario: Admin publishes a draft article
    Given the user is authenticated as an Administrator
    And a news article exists with status "DRAFT"
    When they change the status to "PUBLISHED"
    Then the system updates the status to "PUBLISHED"
    And published_at is set to the current timestamp
    And the article becomes visible to the appropriate audience based on its scope

  @happy-path
  Scenario: Admin archives a published article
    Given the user is authenticated as an Administrator
    And a news article exists with status "PUBLISHED"
    When they change the status to "ARCHIVED"
    Then the system updates the status to "ARCHIVED"
    And the article is no longer visible in public listings

  @edge-case
  Scenario: Admin attempts invalid state transition (DRAFT -> ARCHIVED)
    Given the user is authenticated as an Administrator
    And a news article exists with status "DRAFT"
    When they attempt to change the status to "ARCHIVED"
    Then the system returns HTTP 422 with an error indicating invalid state transition

  @edge-case
  Scenario: Admin attempts invalid state transition (ARCHIVED -> PUBLISHED)
    Given the user is authenticated as an Administrator
    And a news article exists with status "ARCHIVED"
    When they attempt to change the status to "PUBLISHED"
    Then the system returns HTTP 422 with an error indicating invalid state transition

  @security
  Scenario: Non-admin attempts to change article status
    Given the user is authenticated as a Member
    When they attempt to change the status of a news article
    Then the system returns HTTP 403 Forbidden
```

---

### NM-ADMIN-004 — Soft Delete News Article

**As an** Administrator,
**I want to** soft-delete a news article,
**So that** it is removed from all listings but can be recovered if needed.

#### Acceptance Criteria

```gherkin
Feature: Soft Delete News Article

  @happy-path
  Scenario: Admin soft-deletes an article
    Given the user is authenticated as an Administrator
    And a news article with id "article-uuid" exists with is_deleted false
    When they delete the article
    Then the system sets is_deleted to true
    And updated_at is refreshed
    And the system returns HTTP 200 with a confirmation
    And the article no longer appears in any listing

  @edge-case
  Scenario: Admin deletes an already deleted article
    Given the user is authenticated as an Administrator
    And a news article with id "article-uuid" has is_deleted set to true
    When they attempt to delete the article
    Then the system returns HTTP 404 Not Found

  @security
  Scenario: Non-admin attempts to delete an article
    Given the user is authenticated as a Member
    When they attempt to delete a news article
    Then the system returns HTTP 403 Forbidden

  @security
  Scenario: Unauthenticated user attempts to delete an article
    Given the user is not authenticated
    When they attempt to delete a news article
    Then the system returns HTTP 401 Unauthorized

  @observability
  Scenario: Deletion is audit-logged
    Given the user is authenticated as an Administrator
    When they soft-delete a news article
    Then the system logs the deletion event with author_id, article_id, and timestamp
```

---

### NM-MEMBER-001 — View News Detail (All Scopes)

**As a** Member,
**I want to** view the full detail of any published news article (General or Internal),
**So that** I can stay informed on all association matters and feel the value of my membership.

#### Acceptance Criteria

```gherkin
Feature: View News Article Detail — Member

  @happy-path
  Scenario: Member views a GENERAL published article
    Given the user is authenticated as a Member
    And a news article exists with status "PUBLISHED" and scope "GENERAL"
    When they request the article detail
    Then the system returns HTTP 200 with the full article data including title, summary, content, cover_url, tags, author_id, and published_at

  @happy-path
  Scenario: Member views an INTERNAL published article
    Given the user is authenticated as a Member
    And a news article exists with status "PUBLISHED" and scope "INTERNAL"
    When they request the article detail
    Then the system returns HTTP 200 with the full article data

  @edge-case
  Scenario: Member views a non-existent article
    Given the user is authenticated as a Member
    When they request the detail of article id "non-existent-uuid"
    Then the system returns HTTP 404 Not Found

  @edge-case
  Scenario: Member views a DRAFT article
    Given the user is authenticated as a Member
    And a news article exists with status "DRAFT"
    When they request the article detail
    Then the system returns HTTP 404 Not Found

  @edge-case
  Scenario: Member views a soft-deleted article
    Given the user is authenticated as a Member
    And a news article has is_deleted set to true
    When they request the article detail
    Then the system returns HTTP 404 Not Found
```

---

### NM-VISITOR-001 — View News Detail (General Only)

**As a** Visitor (or Supporter),
**I want to** view the full detail of published General Neighborhood news,
**So that** I can learn about public events and neighborhood announcements.

#### Acceptance Criteria

```gherkin
Feature: View News Article Detail — Visitor / Supporter

  @happy-path
  Scenario: Visitor views a GENERAL published article
    Given the user is not authenticated
    And a news article exists with status "PUBLISHED" and scope "GENERAL"
    When they request the article detail
    Then the system returns HTTP 200 with the full article data

  @happy-path
  Scenario: Supporter views a GENERAL published article
    Given the user is authenticated as a Supporter
    And a news article exists with status "PUBLISHED" and scope "GENERAL"
    When they request the article detail
    Then the system returns HTTP 200 with the full article data

  @security
  Scenario: Visitor attempts to view an INTERNAL article
    Given the user is not authenticated
    And a news article exists with status "PUBLISHED" and scope "INTERNAL"
    When they request the article detail
    Then the system returns HTTP 404 Not Found

  @security
  Scenario: Supporter attempts to view an INTERNAL article
    Given the user is authenticated as a Supporter
    And a news article exists with status "PUBLISHED" and scope "INTERNAL"
    When they request the article detail
    Then the system returns HTTP 404 Not Found

  @edge-case
  Scenario: Visitor views a non-existent article
    Given the user is not authenticated
    When they request the detail of article id "non-existent-uuid"
    Then the system returns HTTP 404 Not Found
```

---

### NM-VISITOR-002 — List Published News Articles

**As a** Visitor (or any user),
**I want to** see a paginated, date-sorted list of published news articles visible to me,
**So that** I can browse recent news efficiently.

#### Acceptance Criteria

```gherkin
Feature: List Published News Articles

  @happy-path
  Scenario: Visitor lists published news
    Given the user is not authenticated
    And there are 15 published articles: 10 GENERAL and 5 INTERNAL
    When they request the news list with limit 10 and offset 0
    Then the system returns HTTP 200 with 10 GENERAL articles
    And results are sorted by published_at descending
    And no INTERNAL articles are included
    And pagination metadata is included (total count, limit, offset)

  @happy-path
  Scenario: Member lists published news
    Given the user is authenticated as a Member
    And there are 15 published articles: 10 GENERAL and 5 INTERNAL
    When they request the news list with limit 10 and offset 0
    Then the system returns HTTP 200 with 10 articles (mix of GENERAL and INTERNAL)
    And results are sorted by published_at descending

  @happy-path
  Scenario: User searches news by title
    Given the user is not authenticated
    And there are published GENERAL articles with titles "Fiesta del Barrio" and "Obras en la Calle Mayor"
    When they request the news list with search query "Fiesta"
    Then the system returns HTTP 200 with articles matching the title search
    And only GENERAL articles are included

  @happy-path
  Scenario: Admin lists all articles including drafts
    Given the user is authenticated as an Administrator
    When they request the news list with no status filter
    Then the system returns articles in all statuses (DRAFT, PUBLISHED, ARCHIVED)
    And results are sorted by updated_at descending

  @edge-case
  Scenario: Empty results
    Given there are no published GENERAL articles
    When a Visitor requests the news list
    Then the system returns HTTP 200 with an empty list and total count 0

  @performance
  Scenario: List endpoint responds within performance budget
    Given there are 1000 published articles in the database
    When any user requests the news list with limit 20
    Then the system responds in less than 500ms (P95)

  @security
  Scenario: INTERNAL articles never leak to unauthenticated users
    Given there are published INTERNAL articles
    When an unauthenticated user requests the news list
    Then no INTERNAL articles appear in the response
    And the total count excludes INTERNAL articles
```

---

### NM-MEMBER-002 — List Internal News Articles

**As a** Member,
**I want to** filter the news list to show only Internal association news,
**So that** I can quickly access exclusive member content.

#### Acceptance Criteria

```gherkin
Feature: List Internal News Articles — Member

  @happy-path
  Scenario: Member filters news by INTERNAL scope
    Given the user is authenticated as a Member
    And there are 5 published INTERNAL articles and 10 published GENERAL articles
    When they request the news list with scope filter "INTERNAL"
    Then the system returns HTTP 200 with only the 5 INTERNAL articles
    And results are sorted by published_at descending

  @security
  Scenario: Supporter attempts to filter by INTERNAL scope
    Given the user is authenticated as a Supporter
    When they request the news list with scope filter "INTERNAL"
    Then the system returns HTTP 200 with an empty list
    And no INTERNAL articles are exposed

  @security
  Scenario: Visitor attempts to filter by INTERNAL scope
    Given the user is not authenticated
    When they request the news list with scope filter "INTERNAL"
    Then the system returns HTTP 200 with an empty list
```
