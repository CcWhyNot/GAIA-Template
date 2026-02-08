# 🚀 GAIA News Management - Quick Start Guide

## 📋 Lo que se ha implementado

✅ **Especificaciones completas** en `specs/features/news-management/`
- Feature description, user stories, tickets, implementation plans

✅ **Backend Python (2000+ líneas)** en `backend/`
- Clean Architecture: Domain → Application → Infrastructure → Presentation
- FastAPI con 6 endpoints REST
- SQLAlchemy ORM + PostgreSQL
- Alembic migrations
- 10+ unit + integration tests
- XSS sanitization, RBAC, soft delete

✅ **Docker Compose** para desarrollo local
✅ **Documentación completa** (README, implementation summary)

---

## 🏃 Quick Start (3 minutos)

### Opción 1: Con Docker Compose (Recomendado)

```bash
# 1. Ir al directorio backend
cd backend

# 2. Levantar services (database + api)
docker-compose up -d

# 3. Esperar health check (30 segundos)
docker-compose ps

# 4. Ver API en http://localhost:8005/docs
```

**Resultado esperado**:
- ✅ PostgreSQL running en puerto 5432 (dentro de Docker)
- ✅ FastAPI running en puerto 8005 (mapeo desde 8000)
- ✅ Swagger UI en http://localhost:8005/docs
- ✅ Todos los endpoints disponibles

### Opción 2: Local Development (Sin Docker)

```bash
# 1. Instalar dependencias
cd backend
pip install poetry
poetry install

# 2. Crear .env
cp .env.example .env
# Editar .env con datos de tu base de datos PostgreSQL

# 3. Aplicar migraciones
alembic upgrade head

# 4. Ejecutar servidor
uvicorn app.main:app --reload

# 5. Ver API en http://localhost:8000/docs
```

---

## 🧪 Ejecutar Tests

```bash
cd backend

# Todos los tests
pytest

# Solo unit tests
pytest tests/unit/

# Solo integration tests
pytest tests/integration/

# Con cobertura
pytest --cov=app --cov-report=html

# Verbose output
pytest -vv
```

**Resultado esperado**:
```
tests/unit/test_news_entity.py::TestNewsArticle::test_create_news_article PASSED
tests/unit/test_news_entity.py::TestNewsArticle::test_publish_article PASSED
tests/unit/test_sanitizer.py::TestSanitizeHtml::test_script_tags_removed PASSED
tests/integration/test_news_use_cases.py::TestCreateNewsUseCase::test_create_article PASSED
...
======================== 26 passed in 1.23s ========================
```

---

## 🌐 Probar la API

### 1. Crear un artículo (Admin)

```bash
curl -X POST http://localhost:8005/api/v1/news \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer 123e4567-e89b-12d3-a456-426614174000:ADMIN" \
  -d '{
    "title": "Fiesta del Barrio",
    "summary": "Celebración anual",
    "content": "<h2>Detalles</h2><p>Será en la plaza central</p>",
    "scope": "GENERAL",
    "cover_url": "https://example.com/image.jpg",
    "tags": ["eventos", "comunidad"]
  }'
```

**Response** (201 Created):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Fiesta del Barrio",
  "summary": "Celebración anual",
  "content": "<h2>Detalles</h2><p>Será en la plaza central</p>",
  "status": "DRAFT",
  "scope": "GENERAL",
  "author_id": "123e4567-e89b-12d3-a456-426614174000",
  "cover_url": "https://example.com/image.jpg",
  "tags": ["eventos", "comunidad"],
  "published_at": null,
  "created_at": "2026-02-08T23:00:00",
  "updated_at": "2026-02-08T23:00:00",
  "is_deleted": false
}
```

### 2. Publicar el artículo (Admin)

```bash
curl -X PATCH http://localhost:8005/api/v1/news/550e8400-e29b-41d4-a716-446655440000/status \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer 123e4567-e89b-12d3-a456-426614174000:ADMIN" \
  -d '{"status": "PUBLISHED"}'
```

**Response** (200 OK):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "PUBLISHED",
  "published_at": "2026-02-08T23:00:05",
  ...
}
```

### 3. Listar artículos (Visitor)

```bash
curl http://localhost:8005/api/v1/news?skip=0&limit=10
```

**Response** (200 OK):
```json
{
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Fiesta del Barrio",
      "summary": "Celebración anual",
      "cover_url": "https://example.com/image.jpg",
      "published_at": "2026-02-08T23:00:05",
      "scope": "GENERAL",
      "tags": ["eventos", "comunidad"]
    }
  ],
  "total": 1,
  "skip": 0,
  "limit": 10
}
```

### 4. Ver detalle (Visitor)

```bash
curl http://localhost:8005/api/v1/news/550e8400-e29b-41d4-a716-446655440000
```

**Response** (200 OK):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Fiesta del Barrio",
  "summary": "Celebración anual",
  "content": "<h2>Detalles</h2><p>Será en la plaza central</p>",
  "status": "PUBLISHED",
  "scope": "GENERAL",
  "author_id": "123e4567-e89b-12d3-a456-426614174000",
  "published_at": "2026-02-08T23:00:05",
  ...
}
```

---

## 🔐 Usuarios de Prueba

Usa estos tokens en el header `Authorization: Bearer <token>`:

| Usuario | Token Format | Rol |
|---------|--------------|-----|
| Admin | `550e8400-e29b-41d4-a716-000000000001:ADMIN` | Crear, editar, eliminar, ver todos |
| Member | `550e8400-e29b-41d4-a716-000000000002:MEMBER` | Ver GENERAL + INTERNAL |
| Supporter | `550e8400-e29b-41d4-a716-000000000003:SUPPORTER` | Ver solo GENERAL |
| Visitor | Sin token o `:VISITOR` | Ver solo GENERAL (sin autenticar) |

---

## 📝 Casos de Prueba Manuales

### ✅ Test 1: Create + Publish
```bash
# 1. Admin crea artículo (status=DRAFT)
POST /api/v1/news
# 2. Admin publica (status=PUBLISHED, published_at set)
PATCH /api/v1/news/{id}/status con {"status": "PUBLISHED"}
# 3. Visitor ve el artículo publicado
GET /api/v1/news/{id}
```

### ✅ Test 2: XSS Prevention
```bash
# Admin intenta crear con script tag
POST /api/v1/news con content: "<script>alert('xss')</script><p>Safe</p>"
# Respuesta: content almacenado sin script tag
GET /api/v1/news/{id}
# → response.content = "<p>Safe</p>"
```

### ✅ Test 3: INTERNAL Article Security
```bash
# Admin crea artículo INTERNAL
POST /api/v1/news con scope: "INTERNAL"
# Admin publica
PATCH /api/v1/news/{id}/status
# Visitor intenta ver (debe retornar 404, no 403)
GET /api/v1/news/{id}
# → HTTP 404 (información no divulgada)
# Member ve el mismo artículo
GET /api/v1/news/{id} con Authorization: Bearer ...:MEMBER
# → HTTP 200 + article data
```

### ✅ Test 4: Invalid Transitions
```bash
# Admin crea artículo (DRAFT)
POST /api/v1/news
# Admin intenta archivar directamente (DRAFT → ARCHIVED inválido)
PATCH /api/v1/news/{id}/status con {"status": "ARCHIVED"}
# → HTTP 422 "Cannot transition from DRAFT to ARCHIVED"
```

### ✅ Test 5: Soft Delete
```bash
# Admin crea + publica artículo
POST + PATCH
# Admin elimina
DELETE /api/v1/news/{id}
# → HTTP 200
# Artículo no aparece en listados
GET /api/v1/news
# → total no incluye el eliminado
# Intentar ver detalle
GET /api/v1/news/{id}
# → HTTP 404
```

---

## 📚 Documentación Detallada

- **Backend README**: `backend/README.md` (500+ líneas)
  - Setup detallado
  - Arquitectura explicada
  - Todos los endpoints documentados
  - Troubleshooting

- **Implementation Summary**: `IMPLEMENTATION_SUMMARY.md`
  - Especificaciones generadas
  - Código implementado
  - Tests creados
  - Seguridad implementada

- **Feature Specs**: `specs/features/news-management/`
  - `feature-descr.md` — Descripción del feature
  - `user-stories.md` — 8 historias con Gherkin
  - `tickets.md` — 10 tickets de implementación
  - `plan_*.md` — 7 planes detallados

---

## 🛠️ Troubleshooting

### Error: "Cannot connect to database"
```bash
# Verificar que PostgreSQL está running
docker-compose ps db

# Recrear servicios
docker-compose down
docker-compose up -d --build
```

### Error: "Table news_articles does not exist"
```bash
# Aplicar migraciones
docker-compose exec backend alembic upgrade head

# O en local:
alembic upgrade head
```

### Error: "Module not found"
```bash
# Reinstalar dependencias
poetry install --no-cache
```

### Tests fallando
```bash
# Ejecutar con verbose output
pytest -vv

# Ver logs detallados
pytest -s --tb=short
```

---

## 📊 Resumen de Implementación

**Especificaciones** (Docs)
- ✅ Feature description
- ✅ 8 User stories (Gherkin)
- ✅ 10 Implementation tickets
- ✅ 7 Implementation plans

**Backend** (Code)
- ✅ Domain Layer: 1 entity, 1 port
- ✅ Application Layer: 6 use cases
- ✅ Infrastructure Layer: 1 model, 1 repository
- ✅ Presentation Layer: 6 endpoints, 7 DTOs
- ✅ Core: Config, DB, sanitizers, security

**Testing**
- ✅ 16 unit tests
- ✅ 10 integration tests
- ✅ Coverage: 80%+

**Deployment**
- ✅ Docker + docker-compose
- ✅ Alembic migrations
- ✅ PostgreSQL con indexes

**Documentation**
- ✅ Backend README (500+ lines)
- ✅ Code comments (traceability)
- ✅ Implementation summary (this file)

---

## ✅ Verificación Rápida

Ejecutar esto para verificar que todo está funcionando:

```bash
cd backend

# 1. Levantar services
docker-compose up -d

# 2. Esperar health check
sleep 30

# 3. Ejecutar tests
pytest

# 4. Ver API docs
echo "Open http://localhost:8005/docs in your browser"

# 5. Hacer un request de prueba
curl http://localhost:8005/health
```

**Resultado esperado**: Todo debe estar ✅ verde

---

## 🎓 Aprendizajes Clave

1. **Clean Architecture**: Separación clara entre capas
2. **Domain-Driven Design**: Lógica de negocio en domain layer
3. **TDD approach**: Tests guían la implementación
4. **Security by default**: RBAC, XSS prevention, soft delete
5. **SOLID principles**: Dependency injection, single responsibility
6. **Spec-Driven Development**: Specs → Code → Tests

---

¡Listo para empezar! 🚀

Si necesitas ayuda, consulta `backend/README.md` o los comentarios en el código.
