"""Knowledge graph service.

Projects the relational entity/relationship store (Phase 6) into the graph
backend (Neo4j) and exposes traversal/visualization views. Sync is idempotent
(MERGE semantics) — re-running reconciles the graph with the source of truth in
PostgreSQL, following the outbox-style projection in the architecture plan.
"""

from __future__ import annotations

import uuid

from app.ai.graph.backend import GraphBackend, GraphEdge, GraphNode, GraphView
from app.core.logging import get_logger
from app.repositories.knowledge import EntityRepository, RelationshipRepository

logger = get_logger("kira.graph")


class GraphService:
    """Builds and queries the per-organization knowledge graph."""

    def __init__(
        self,
        entities: EntityRepository,
        relationships: RelationshipRepository,
        backend: GraphBackend,
    ) -> None:
        self.entities = entities
        self.relationships = relationships
        self.backend = backend

    async def sync_org(self, organization_id: uuid.UUID) -> dict[str, int]:
        """Project all entities/relationships for the org into the graph."""
        org = str(organization_id)
        entities = await self.entities.list_for_org(organization_id, limit=10_000, offset=0)
        for ent in entities:
            await self.backend.upsert_node(
                org,
                GraphNode(
                    id=str(ent.id),
                    label=ent.entity_type,
                    name=ent.name,
                    properties={"normalized": ent.normalized},
                ),
            )

        relationships = await self.relationships.list_for_org(
            organization_id, limit=50_000, offset=0
        )
        for rel in relationships:
            await self.backend.upsert_edge(
                org,
                GraphEdge(
                    source=str(rel.source_entity_id),
                    target=str(rel.target_entity_id),
                    rel_type=rel.rel_type,
                ),
            )

        logger.info(
            "graph_synced",
            org=org,
            nodes=len(entities),
            edges=len(relationships),
        )
        return {"nodes": len(entities), "edges": len(relationships)}

    async def overview(self, organization_id: uuid.UUID, limit: int = 100) -> GraphView:
        return await self.backend.overview(str(organization_id), limit=limit)

    async def neighbors(
        self, organization_id: uuid.UUID, entity_id: uuid.UUID, depth: int = 1
    ) -> GraphView:
        return await self.backend.neighbors(str(organization_id), str(entity_id), depth=depth)
