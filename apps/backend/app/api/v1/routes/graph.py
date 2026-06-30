"""Knowledge graph endpoints: sync, overview, and node neighborhood."""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.ai.graph.backend import GraphView
from app.api.deps import CurrentUser, get_graph_service, require_role
from app.core.security import Role
from app.schemas.graph import GraphEdgeOut, GraphNodeOut, GraphSyncResult, GraphViewOut
from app.services.graph import GraphService

router = APIRouter(prefix="/graph", tags=["graph"])

Graph = Annotated[GraphService, Depends(get_graph_service)]
Engineer = Depends(require_role(Role.ENGINEER))


def _to_view(view: GraphView) -> GraphViewOut:
    return GraphViewOut(
        nodes=[
            GraphNodeOut(id=n.id, label=n.label, name=n.name, properties=n.properties)
            for n in view.nodes
        ],
        edges=[
            GraphEdgeOut(source=e.source, target=e.target, rel_type=e.rel_type)
            for e in view.edges
        ],
    )


@router.post("/sync", response_model=GraphSyncResult, dependencies=[Engineer])
async def sync_graph(user: CurrentUser, service: Graph) -> GraphSyncResult:
    """Project the org's entities/relationships into the knowledge graph."""
    result = await service.sync_org(user.organization_id)
    return GraphSyncResult(**result)


@router.get("", response_model=GraphViewOut)
async def graph_overview(
    user: CurrentUser,
    service: Graph,
    limit: Annotated[int, Query(ge=1, le=500)] = 100,
) -> GraphViewOut:
    return _to_view(await service.overview(user.organization_id, limit=limit))


@router.get("/node/{entity_id}", response_model=GraphViewOut)
async def graph_neighbors(
    entity_id: uuid.UUID,
    user: CurrentUser,
    service: Graph,
    depth: Annotated[int, Query(ge=1, le=4)] = 1,
) -> GraphViewOut:
    return _to_view(await service.neighbors(user.organization_id, entity_id, depth=depth))
