# User Stories — Global Aggregation

## News Management (Módulo de Noticias)

| ID | Title | Role | Summary |
|---|---|---|---|
| NM-ADMIN-001 | Create News Article | Administrator | Create a new news article with title, summary, content, cover image, tags, and visibility scope. |
| NM-ADMIN-002 | Edit News Article | Administrator | Edit an existing news article (title, summary, content, scope, cover image, tags). |
| NM-ADMIN-003 | Publish / Archive News Article | Administrator | Change the status of a news article (Draft -> Published, Published -> Archived). |
| NM-ADMIN-004 | Soft Delete News Article | Administrator | Soft-delete a news article so it is removed from listings but recoverable. |
| NM-MEMBER-001 | View News Detail (All Scopes) | Member | View the full detail of any published news article (General or Internal). |
| NM-VISITOR-001 | View News Detail (General Only) | Visitor / Supporter | View the full detail of published General Neighborhood news. |
| NM-VISITOR-002 | List Published News Articles | Visitor / Any | See a paginated, date-sorted list of published news articles visible to the user. |
| NM-MEMBER-002 | List Internal News Articles | Member | Filter the news list to show only Internal association news. |

**Detailed stories:** `specs/features/news-management/user-stories.md`
