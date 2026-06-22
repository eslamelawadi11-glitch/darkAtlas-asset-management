# DarkAtlas Asset Management System

A self-contained Asset Management module for the DarkAtlas Attack Surface Monitoring platform.

## Stack
- **Python 3.13** + **FastAPI**
- **PostgreSQL 16** (via Docker)
- **SQLAlchemy** ORM
- **Pydantic v2** for validation

---

## Quick Start

### 1. Clone the repo

    git clone https://github.com/YOUR_USERNAME/darkAtlas-asset-management.git
    cd darkAtlas-asset-management

### 2. Setup environment

    cp .env.example .env

### 3. Run with Docker

    docker-compose up --build

API will be live at: `http://localhost:8000`
Swagger UI: `http://localhost:8000/docs`

---

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://postgres:password@db:5432/darkatlas` |
| `API_KEY` | API key for write operations | `changeme-secret-api-key` |
| `DEBUG` | Debug mode | `false` |

---

## Authentication

Write operations (POST, PATCH, DELETE) require an API key in the request header:

    X-API-Key: your-api-key

Read operations (GET) are public.

---

## API Endpoints

### Assets
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/assets/` | ✅ | Create asset |
| `GET` | `/assets/` | ❌ | List assets (filter, sort, paginate) |
| `GET` | `/assets/{id}` | ❌ | Get asset by ID |
| `PATCH` | `/assets/{id}` | ✅ | Update asset |
| `DELETE` | `/assets/{id}` | ✅ | Delete asset |
| `PATCH` | `/assets/{id}/stale` | ✅ | Mark asset as stale |
| `POST` | `/assets/bulk-import` | ✅ | Bulk import with deduplication |

### Relationships
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/relationships/` | ✅ | Create relationship |
| `GET` | `/relationships/` | ❌ | List all relationships |
| `GET` | `/relationships/graph/{id}` | ❌ | Get asset with its graph |
| `DELETE` | `/relationships/{id}` | ✅ | Delete relationship |

---

## List Filters

    GET /assets/?type=domain&status=active&tag=prod&value_contains=example&sort_by=last_seen&sort_order=desc&page=1&page_size=20

---

## Bulk Import Example

    POST /assets/bulk-import
    X-API-Key: your-api-key

    {
      "assets": [
        {
          "type": "domain",
          "value": "example.com",
          "status": "active",
          "source": "scan",
          "tags": ["root"],
          "metadata": {}
        },
        {
          "type": "subdomain",
          "value": "api.example.com",
          "status": "active",
          "source": "scan",
          "tags": ["prod"],
          "metadata": {}
        }
      ]
    }

---

## Running Tests

    python -m pytest tests/ -v

---

## Design Decisions & Assumptions

- **Deduplication** is based on `type + value` combination — two assets with the same type and value are considered the same asset.
- **Tag merging** on re-import uses a union strategy (no duplicates, no deletions).
- **Metadata merging** uses an override strategy — incoming values overwrite existing keys on conflict.
- **Stale re-activation** — if a stale asset is seen again via bulk import, it automatically returns to `active`.
- **Malformed records** in bulk import are skipped gracefully and reported in the response.
- **PostgreSQL ARRAY** is used for tags in production; tests use SQLite with JSON for portability.
- **Authentication** is API-key based via `X-API-Key` header on all write operations.
- **first_seen** is set once on creation and never updated.
- **last_seen** is updated on every re-sighting or update.

---

## What I Would Add Next

- Alembic migrations for proper schema versioning
- Multi-tenant organization isolation
- Rate limiting and caching
- CI/CD pipeline with GitHub Actions
- LangChain-powered natural language asset queries (Track B bonus)