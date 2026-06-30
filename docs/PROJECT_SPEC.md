# PROJECT_SPEC.md

# KIRA (Knowledge Intelligence for Rapid Analysis) – Unified Industrial Knowledge Intelligence Platform

> Canonical product name: **KIRA**. (Formerly referred to as "IntelliPlant AI" in early drafts.)

## Vision
Build an enterprise AI platform that ingests industrial documents, extracts knowledge, builds a knowledge graph, indexes semantic embeddings, and provides citation-backed answers, maintenance intelligence, compliance analysis, and root cause analysis.

## Objectives
- Unified document repository
- AI Copilot
- Knowledge Graph
- Hybrid RAG
- Compliance intelligence
- Maintenance intelligence
- RCA engine

## Tech Stack
Frontend:
- Next.js 15
- TypeScript
- Tailwind CSS
- shadcn/ui
- React Flow
- Recharts

Backend:
- FastAPI
- PostgreSQL
- Redis
- Celery
- Qdrant
- Neo4j
- MinIO

AI:
- OCR
- Entity Extraction
- Hybrid RAG
- GraphRAG
- Multi-agent orchestration

## Core Workflow
Upload -> Storage -> OCR -> Layout Parsing -> Entity Extraction -> Knowledge Graph -> Chunking -> Embedding -> Qdrant -> Search -> AI Agents -> Citation-backed Response

## AI Agents
1. Document Intelligence
2. Knowledge Copilot
3. Maintenance Agent
4. Compliance Agent
5. RCA Agent
6. Lessons Learned Agent

## Functional Requirements
- Authentication
- Organization & Project management
- Upload PDF/DOCX/XLSX/Images
- OCR
- Metadata extraction
- Entity extraction
- Knowledge graph
- Hybrid search
- AI chat
- Reports
- Dashboard
- Audit logs

## Non-functional Requirements
- Modular
- Responsive
- Secure
- Typed
- Testable
- Dockerized

## Folder Structure
apps/
  web/
  backend/
packages/
docs/
docker/

## Development Order
1. Monorepo
2. Auth
3. Upload
4. OCR
5. Entity Extraction
6. Knowledge Graph
7. Embeddings
8. Hybrid Search
9. AI Agents
10. Dashboard
11. Reports
12. Deployment

## Coding Standards
- Clean Architecture
- SOLID
- Repository Pattern
- Strict TypeScript
- Python type hints
- REST APIs
- OpenAPI
