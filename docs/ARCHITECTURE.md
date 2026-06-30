# ARCHITECTURE.md

# High-Level Architecture

Users
-> Next.js 15 Frontend
-> FastAPI API Gateway
-> Authentication Service
-> Document Service
-> Redis Queue
-> Celery Workers
-> OCR Pipeline
-> Entity Extraction
-> Knowledge Graph (Neo4j)
-> Embedding Service
-> Qdrant Vector DB
-> AI Orchestrator
-> Specialized AI Agents
-> Response Composer

## Core Services
- Auth Service
- Project Service
- Document Service
- Search Service
- Graph Service
- AI Service
- Analytics Service
- Notification Service

## Data Flow
Upload → Store in MinIO → OCR → Parse → Chunk → Extract Entities → Build Graph → Generate Embeddings → Index → Query.

## Infrastructure
- Next.js
- FastAPI
- PostgreSQL
- Redis
- Celery
- Neo4j
- Qdrant
- MinIO
- Docker Compose
