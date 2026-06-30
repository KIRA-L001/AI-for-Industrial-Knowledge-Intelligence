# API_SPEC.md

## Authentication
POST /auth/register
POST /auth/login
GET /auth/me

## Documents
POST /documents/upload
GET /documents
GET /documents/{id}
DELETE /documents/{id}

## Search
POST /search

## Chat
POST /chat

## Equipment
GET /equipment
GET /equipment/{id}

## Graph
GET /graph/{equipment_id}

## Maintenance
POST /maintenance/analyze

## Compliance
POST /compliance/check

## Reports
POST /reports/generate
