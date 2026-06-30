# KIRA — Knowledge Intelligence for Rapid Analysis

> An enterprise **Industrial AI Operating System** that turns fragmented plant
> documents (PDF, DOCX, XLSX, CSV, images, P&IDs) into a unified, queryable
> knowledge hub with **citation-backed answers**, an **industrial knowledge
> graph**, **predictive maintenance**, and **compliance intelligence**.

KIRA is not a chatbot. It ingests documents, extracts structured knowledge,
builds a knowledge graph, indexes semantic embeddings, performs hybrid
retrieval, and orchestrates multiple specialized AI agents — every answer is
grounded in your documents and traceable to the exact source passage.

---

## Table of contents

1. [Quickstart](#quickstart)
2. [Architecture at a glance](#architecture-at-a-glance)
3. [How it all works](#how-it-all-works)
   - [The document → knowledge pipeline](#1-the-document--knowledge-pipeline)
   - [Hybrid retrieval](#2-hybrid-retrieval)
   - [The AI Operating System](#3-the-ai-operating-system)
   - [A request, end to end](#4-a-request-end-to-end)
4. [Multi-tenancy & security](#multi-tenancy--security)
5. [The offline-first AI layer](#the-offline-first-ai-layer)
6. [Project layout](#project-layout)
7. [Data model](#data-model)
8. [API surface](#api-surface)
9. [Local development](#local-development)
10. [Testing](#testing)
11. [Configuration](#configuration)

---

## Quickstart

Prerequisites: **Docker Desktop** (with WSL2 on Windows) and **Node 20+**.

```bash
cp .env.example .env          # adjust secrets for anything non-local
npm run infra:up              # builds & starts all 8 services
```

| Service        | URL                                   |
|----------------|---------------------------------------|
| Web app        | http://localhost:3000                 |
| API + OpenAPI  | http://localhost:8000/docs            |
| Liveness       | http://localhost:8000/api/v1/health   |
| Readiness      | http://localhost:8000/api/v1/ready    |
| Neo4j browser  | http://localhost:7474                 |
| MinIO console  | http://localhost:9001                 |

Open the web app, **create a workspace** (this registers an organization +
owner user), then upload a document and ask the Copilot a question.

`npm run infra:down` stops everything; `npm run infra:logs` tails logs.

> **Note:** the default backend image is **lean** — it does not bundle PyTorch.
> KIRA runs fully with deterministic offline AI fallbacks (see
> [The offline-first AI layer](#the-offline-first-ai-layer)). To enable real
> transformer embeddings + cross-encoder reranking, install the optional ML
> stack (`apps/backend/requirements-ml.txt`).

---

## Architecture at a glance

```
                              ┌──────────────────────────┐
   Browser ───────────────▶   │  Next.js 15 web (App Router)│
                              └─────────────┬────────────┘
                                 REST / SSE │  (TanStack Query + Zustand auth)
                              ┌─────────────▼────────────┐
                              │   FastAPI API (thin)     │  routes → services → repos
                              │   JWT auth · RBAC · CORS │
                              └─────────────┬────────────┘
        ┌──────────────┬────────────────────┼───────────────────┬─────────────────┐
        ▼              ▼                     ▼                   ▼                 ▼
   Auth/Catalog   Document svc          Retrieval svc       AI Orchestrator   Analytics/
   (org-scoped    (upload→MinIO,        (hybrid: vector +   (plan → retrieve  Reports
    CRUD)          status machine)      keyword + rerank)    → compose → cite)
        │              │                     │                   │
        │         ┌────▼──── Celery worker ──┼───────────────────┘
        │         │  OCR · chunking · entity/relationship extraction · embedding
        ▼         ▼                          ▼
   ┌────────────────────────────────────────────────────────────────────────┐
   │ PostgreSQL  │  Redis  │  MinIO  │  Neo4j (graph)  │  Qdrant (vectors)  │
   │ (metadata)   (cache+   (files)   (entities +       (chunk embeddings)  │
   │              queue)               relationships)                       │
   └────────────────────────────────────────────────────────────────────────┘
```

**Design principles:** Clean Architecture, SOLID, Repository pattern, and
Dependency Injection throughout. Routes are thin; business logic lives in
services; data access lives in repositories. The dependency graph is acyclic:
`routes → services → repositories → stores`. External systems (LLM, vector
store, graph, object storage) sit behind interfaces so they're swappable and
testable.

---

## How it works

### 1. The document → knowledge pipeline

Every uploaded document advances through an explicit **status state machine**,
so processing is observable and idempotent:

```
uploaded → ocr → extracted → embedded → ready          (failed on any error)
```

| Stage | What happens | Where |
|-------|--------------|-------|
| **Upload** | File is validated against an allow-list, checksummed (SHA-256), stored in **MinIO**, and a `documents` row is created in `uploaded` state. | `services/document.py` |
| **OCR / extract** | Per-format extractors pull text + layout: `pypdf` (PDF), `python-docx` (DOCX), `openpyxl` (XLSX), CSV/plain, and **Tesseract OCR** for images (with word-level bounding boxes for citation provenance). Each page → a `document_pages` row. | `ai/ocr/extractor.py`, `services/processing.py` |
| **Chunking** | Page text is split into overlapping, word-bounded chunks (`chunks` table) carrying page + char offsets. | `ai/chunking.py` |
| **Entity & relationship extraction** | A pluggable extractor finds industrial **equipment tags** (e.g. `P-101`), **compliance standards** (OISD / PESO / Factory Act / API / ASME / IS), and links them (`governed_by`), upserting `entities` + `relationships` per organization. | `ai/extraction.py`, `services/intelligence.py` |
| **Knowledge graph** | Entities/relationships are projected into **Neo4j** (idempotent `MERGE`), giving a traversable, per-tenant industrial graph for visualization and graph-aware retrieval. | `services/graph.py`, `ai/graph/backend.py` |
| **Embedding** | Each chunk is embedded and upserted into **Qdrant** with tenant + source metadata; the chunk is marked `embedded`. | `services/embedding.py`, `ai/embeddings.py` |

Heavy stages run as **Celery tasks** (Redis broker) so uploads return instantly
and processing happens in the background worker; the same logic can also run
inline for small inputs and tests.

### 2. Hybrid retrieval

When a question is asked, KIRA retrieves evidence using **multiple signals**,
not just vector similarity:

1. **Semantic search** — embed the query, search Qdrant (tenant-filtered).
2. **Keyword search** — case-insensitive `LIKE` over chunk text (catches exact
   tags/codes that embeddings can blur).
3. **Reciprocal Rank Fusion (RRF)** — merge both candidate lists into one
   ranking that rewards passages found by either method.
4. **Cross-encoder reranking** — re-score the fused candidates against the query
   for final precision.
5. **Context builder** — assemble the top passages into a numbered context
   block, each carrying its **chunk / document / page provenance** so the answer
   can cite `[1]`, `[2]`, ….

See `services/retrieval.py`.

### 3. The AI Operating System

The AI layer (`ai/os/`, `ai/agents/`, `ai/llm/`) is the orchestration brain:

- **Planner** — lightweight intent classification routes a question to the right
  specialized agent.
- **Six specialized agents** (`ai/agents/registry.py`), each a reusable
  system-prompt + identity:
  **Knowledge Copilot**, **Document Intelligence**, **Maintenance**,
  **Compliance** (Factory Act / OISD / PESO), **RCA** (root-cause analysis), and
  **Lessons Learned**.
- **Orchestrator** (`ai/os/orchestrator.py`) — runs the pipeline:
  `plan → retrieve cited context → compose answer via the LLM → score confidence`.
- **Confidence engine** (`ai/os/confidence.py`) — derives a 0–1 score from the
  count and strength of supporting citations, so weakly-evidenced answers are
  flagged `low`.
- **Citation engine** — every answer ships with the exact source passages.
- **Provider-agnostic LLM** (`ai/llm/`) — agents depend on an `LLMProvider`
  interface, never a vendor (see below).

### 4. A request, end to end

> *"What is the root cause of the pump seal failure?"*

```
Browser → POST /api/v1/chat
  → Planner classifies intent → routes to the RCA agent
  → RetrievalService: semantic + keyword → RRF → cross-encoder rerank
       → top passages with {chunk, document, page} provenance
  → Orchestrator builds messages (RCA system prompt + cited context + question)
  → LLMProvider.complete(...) generates a grounded answer referencing [1],[2]
  → ConfidenceEngine scores the evidence
  ← { agent: "rca", answer, confidence, confidence_label, citations[] }
```

The frontend renders the answer with inline citations, a confidence badge, and
links back to the source documents. `POST /api/v1/chat/stream` does the same
over **Server-Sent Events** for token-by-token streaming.

---

## Multi-tenancy & security

- **Tenant isolation** is enforced at the **repository layer**: every
  tenant-owned entity carries `organization_id`, and the org-scoped repository
  filters every read/write by it — a user can never see another org's data.
  This is exercised by an explicit tenant-isolation test.
- **Auth**: registration creates an organization + owner; login issues a JWT
  **access + refresh** token pair (bcrypt-hashed passwords).
- **RBAC**: hierarchical roles `viewer < engineer < admin < owner`; write
  endpoints are guarded by a `require_role` dependency.
- **Hardening**: standard error envelope, request-id propagation, structured
  access logs, and baseline security headers (`X-Content-Type-Options`,
  `X-Frame-Options`, `Referrer-Policy`).

---

## The offline-first AI layer

Every AI dependency has a **deterministic, dependency-free fallback**, selected
automatically when the heavy library or API key is absent. This means the whole
pipeline runs — and is fully testable — with **no model downloads and no
network**, while production swaps in real models via configuration:

| Capability   | Offline default (built-in)     | Production adapter (opt-in)                          |
|--------------|--------------------------------|-----------------------------------------------------|
| LLM          | `StubLLM` (grounded templating)| **Anthropic Claude / OpenAI / Ollama** (`LLM_PROVIDER`) |
| Embeddings   | `HashingEmbedder` (hashed BoW) | **Sentence-Transformers** (`EMBEDDING_MODEL`)        |
| Reranking    | `LexicalReranker` (token overlap) | **Cross-encoder** (`RERANKER_MODEL`)              |
| Vector store | in-memory cosine (tests)       | **Qdrant**                                          |
| Graph        | in-memory adjacency (tests)    | **Neo4j**                                           |
| Object store | in-memory (tests)              | **MinIO**                                          |

Enable the real ML models:

```bash
cd apps/backend
pip install --index-url https://download.pytorch.org/whl/cpu torch==2.5.1
pip install -r requirements-ml.txt
# then set LLM_PROVIDER / LLM_API_KEY in .env to use a real LLM
```

---

## Project layout

```
apps/
  backend/                 FastAPI service (clean architecture)
    app/
      api/v1/routes/        thin HTTP routes (auth, documents, chat, graph, …)
      api/deps.py           dependency injection wiring
      services/             business logic (auth, document, intelligence, retrieval, copilot, …)
      repositories/         data access (org-scoped repository pattern)
      models/               SQLAlchemy ORM models + enums
      schemas/              Pydantic request/response DTOs
      ai/                   ocr · chunking · extraction · embeddings · vectorstore
                            · rerank · graph · llm (providers) · os (orchestrator,
                            confidence) · agents (registry + planner)
      core/                 config, security (JWT/bcrypt/RBAC), errors, logging, middleware
      db/                   async engine/session, base mixins, portable GUID type
      tasks/                Celery tasks (document processing)
      worker.py             Celery app
    alembic/                database migrations (0001…0005)
    requirements.txt        lean runtime deps
    requirements-ml.txt     optional heavy ML stack
  web/                     Next.js 15 app (App Router, TS strict)
    app/(app)/              authenticated pages: dashboard, copilot, documents,
                            graph, equipment, projects, maintenance, compliance,
                            rca, analytics, reports, settings
    components/             app shell, UI kit, charts, agent console
    lib/                    typed API client, auth store (Zustand), TanStack hooks
docker/                    Dockerfiles + docker-compose.yml (8 services)
docs/                     source-of-truth specifications
```

---

## Data model

PostgreSQL holds relational metadata (managed by Alembic migrations):

- **organizations**, **users** — tenants and accounts (RBAC roles)
- **plants**, **departments**, **projects**, **equipment** — the asset catalog
- **documents**, **document_pages** — source files + extracted page text/bboxes
- **chunks** — retrievable text chunks (with page/char offsets, `embedded` flag)
- **entities**, **relationships** — the knowledge graph source of truth
  (projected into Neo4j)

Specialist stores: **Neo4j** (graph), **Qdrant** (vectors), **MinIO** (files),
**Redis** (cache + Celery queue).

---

## API surface

All under `/api/v1` (full schema at `/docs`):

| Area | Endpoints |
|------|-----------|
| Auth | `POST /auth/register` · `/auth/login` · `/auth/refresh` · `GET /auth/me` · `POST /auth/password-reset/{request,confirm}` |
| Catalog | CRUD for `/plants` · `/departments` · `/projects` · `/equipment` |
| Documents | `POST /documents/upload` · `GET /documents` · `/{id}` · `/{id}/download` · `/{id}/process` · `/{id}/pages` · `DELETE /{id}` |
| Intelligence | `POST /documents/{id}/analyze` · `GET /documents/{id}/chunks` · `GET /entities` |
| Graph | `POST /graph/sync` · `GET /graph` · `GET /graph/node/{id}` |
| Search / RAG | `POST /documents/{id}/embed` · `POST /search` · `POST /retrieve` |
| AI Copilot | `GET /agents` · `POST /chat` · `POST /chat/stream` |
| Health | `GET /health` (liveness) · `GET /ready` (all stores) |

---

## Local development

**Backend** (Postgres required, or use SQLite for a quick auth/catalog run):

```bash
cd apps/backend
python -m venv .venv && source .venv/Scripts/activate   # Windows Git Bash
pip install -r requirements.txt
alembic upgrade head            # against Postgres
uvicorn app.main:app --reload   # http://localhost:8000
```

For a no-Postgres run, set `DATABASE_URL=sqlite+aiosqlite:///./dev.db` and
`AUTO_CREATE_DB=true` (creates tables on boot — dev only).

**Frontend:**

```bash
cd apps/web
npm install
npm run dev          # http://localhost:3000
npm run typecheck && npm run lint
```

---

## Testing

```bash
cd apps/backend && pytest && ruff check .      # API + unit tests, lint
cd apps/web && npm run typecheck && npm test   # tsc + Vitest
```

The backend suite runs entirely on **SQLite + in-memory fakes** (no external
services needed), exercising auth, RBAC, tenant isolation, the document
pipeline, intelligence, graph sync, embedding/search, hybrid retrieval, and the
Copilot — thanks to the offline-first design above.

---

## Configuration

Configuration is environment-driven (`apps/backend/app/core/config.py`); see
`.env.example` for the full list. Key variables:

| Variable | Purpose |
|----------|---------|
| `DATABASE_URL` | Async PostgreSQL DSN (or SQLite for local dev) |
| `JWT_SECRET_KEY`, `ACCESS_TOKEN_EXPIRE_MINUTES` | Auth signing & lifetimes |
| `LLM_PROVIDER`, `LLM_MODEL`, `LLM_API_KEY` | Select Anthropic/OpenAI/Ollama (else stub) |
| `EMBEDDING_MODEL`, `RERANKER_MODEL` | Real model checkpoints (else fallbacks) |
| `NEO4J_*`, `QDRANT_URL`, `MINIO_*`, `REDIS_URL` | Backing-store connections |

---

KIRA is built as a production-quality Industrial AI Operating System — modular,
typed, multi-tenant, observable, and grounded: **no answer without a citation.**
