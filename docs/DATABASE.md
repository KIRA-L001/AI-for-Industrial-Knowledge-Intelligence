# DATABASE.md

## Core Tables
- users
- organizations
- projects
- documents
- document_versions
- chunks
- embeddings
- equipment
- entities
- relationships
- incidents
- maintenance_records
- inspections
- compliance_rules
- compliance_results
- chats
- audit_logs

## Relationships
Project -> Documents
Document -> Chunks
Chunk -> Embedding
Document -> Entities
Equipment -> Maintenance
Equipment -> Incidents
Equipment -> Compliance

## Databases
PostgreSQL: metadata
Neo4j: graph
Qdrant: vectors
Redis: cache
MinIO: files
