"""Graph view schemas (shaped for React Flow on the frontend)."""

from __future__ import annotations

from pydantic import BaseModel


class GraphNodeOut(BaseModel):
    id: str
    label: str
    name: str
    properties: dict[str, str] = {}


class GraphEdgeOut(BaseModel):
    source: str
    target: str
    rel_type: str


class GraphViewOut(BaseModel):
    nodes: list[GraphNodeOut]
    edges: list[GraphEdgeOut]


class GraphSyncResult(BaseModel):
    nodes: int
    edges: int
