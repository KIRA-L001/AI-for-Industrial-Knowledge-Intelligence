"""Knowledge-graph backend abstraction.

`GraphBackend` is the surface the graph service depends on. `Neo4jGraph` is the
production implementation (async Cypher); `InMemoryGraph` is a dependency-free
backend for tests. All operations are scoped by `organization_id` so tenants
never see each other's graph.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol


@dataclass
class GraphNode:
    id: str
    label: str  # node type, e.g. "equipment" | "standard"
    name: str
    properties: dict[str, str] = field(default_factory=dict)


@dataclass
class GraphEdge:
    source: str
    target: str
    rel_type: str


@dataclass
class GraphView:
    """Nodes + edges shaped for React Flow on the frontend."""

    nodes: list[GraphNode] = field(default_factory=list)
    edges: list[GraphEdge] = field(default_factory=list)


class GraphBackend(Protocol):
    async def upsert_node(self, org_id: str, node: GraphNode) -> None: ...

    async def upsert_edge(self, org_id: str, edge: GraphEdge) -> None: ...

    async def neighbors(self, org_id: str, node_id: str, depth: int = 1) -> GraphView: ...

    async def overview(self, org_id: str, limit: int = 100) -> GraphView: ...

    async def clear_org(self, org_id: str) -> None: ...


class InMemoryGraph:
    """Process-local adjacency store implementing `GraphBackend` for tests."""

    def __init__(self) -> None:
        self._nodes: dict[str, dict[str, GraphNode]] = {}
        self._edges: dict[str, list[GraphEdge]] = {}

    async def upsert_node(self, org_id: str, node: GraphNode) -> None:
        self._nodes.setdefault(org_id, {})[node.id] = node

    async def upsert_edge(self, org_id: str, edge: GraphEdge) -> None:
        edges = self._edges.setdefault(org_id, [])
        if not any(
            e.source == edge.source and e.target == edge.target and e.rel_type == edge.rel_type
            for e in edges
        ):
            edges.append(edge)

    async def neighbors(self, org_id: str, node_id: str, depth: int = 1) -> GraphView:
        nodes = self._nodes.get(org_id, {})
        edges = self._edges.get(org_id, [])
        seen: set[str] = {node_id}
        frontier = {node_id}
        collected_edges: list[GraphEdge] = []
        for _ in range(depth):
            next_frontier: set[str] = set()
            for edge in edges:
                if edge.source in frontier or edge.target in frontier:
                    collected_edges.append(edge)
                    next_frontier.update({edge.source, edge.target})
            frontier = next_frontier - seen
            seen.update(next_frontier)
            if not frontier:
                break
        view_nodes = [nodes[n] for n in seen if n in nodes]
        # Deduplicate edges
        unique = {(e.source, e.target, e.rel_type): e for e in collected_edges}
        return GraphView(nodes=view_nodes, edges=list(unique.values()))

    async def overview(self, org_id: str, limit: int = 100) -> GraphView:
        nodes = list(self._nodes.get(org_id, {}).values())[:limit]
        node_ids = {n.id for n in nodes}
        edges = [
            e
            for e in self._edges.get(org_id, [])
            if e.source in node_ids and e.target in node_ids
        ]
        return GraphView(nodes=nodes, edges=edges)

    async def clear_org(self, org_id: str) -> None:
        self._nodes.pop(org_id, None)
        self._edges.pop(org_id, None)


class Neo4jGraph:
    """Async Neo4j-backed `GraphBackend` using Cypher MERGE statements."""

    def __init__(self) -> None:
        from app.infra.clients import get_neo4j_driver

        self._driver = get_neo4j_driver()

    async def upsert_node(self, org_id: str, node: GraphNode) -> None:
        query = (
            "MERGE (n:Entity {id: $id, org: $org}) "
            "SET n.label = $label, n.name = $name, n += $props"
        )
        async with self._driver.session() as session:
            await session.run(
                query,
                id=node.id,
                org=org_id,
                label=node.label,
                name=node.name,
                props=node.properties,
            )

    async def upsert_edge(self, org_id: str, edge: GraphEdge) -> None:
        query = (
            "MATCH (a:Entity {id: $src, org: $org}), (b:Entity {id: $tgt, org: $org}) "
            "MERGE (a)-[r:REL {type: $rt}]->(b)"
        )
        async with self._driver.session() as session:
            await session.run(query, src=edge.source, tgt=edge.target, org=org_id, rt=edge.rel_type)

    async def neighbors(self, org_id: str, node_id: str, depth: int = 1) -> GraphView:
        query = (
            "MATCH (n:Entity {id: $id, org: $org}) "
            f"OPTIONAL MATCH path = (n)-[*1..{max(1, min(depth, 4))}]-(m:Entity) "
            "WITH collect(distinct n) + collect(distinct m) AS ns, "
            "     [rel in apoc.coll.flatten(collect(relationships(path))) | rel] AS rs "
            "RETURN ns, rs"
        )
        return await self._run_view(query, id=node_id, org=org_id)

    async def overview(self, org_id: str, limit: int = 100) -> GraphView:
        query = (
            "MATCH (n:Entity {org: $org}) WITH n LIMIT $limit "
            "OPTIONAL MATCH (n)-[r:REL]->(m:Entity {org: $org}) "
            "RETURN collect(distinct n) + collect(distinct m) AS ns, collect(distinct r) AS rs"
        )
        return await self._run_view(query, org=org_id, limit=limit)

    async def clear_org(self, org_id: str) -> None:
        async with self._driver.session() as session:
            await session.run("MATCH (n:Entity {org: $org}) DETACH DELETE n", org=org_id)

    async def _run_view(self, query: str, **params: object) -> GraphView:
        nodes: dict[str, GraphNode] = {}
        edges: list[GraphEdge] = []
        async with self._driver.session() as session:
            result = await session.run(query, **params)
            async for record in result:
                for n in record.get("ns") or []:
                    if n is None:
                        continue
                    nodes[n["id"]] = GraphNode(
                        id=n["id"], label=n.get("label", "entity"), name=n.get("name", "")
                    )
                for r in record.get("rs") or []:
                    if r is None:
                        continue
                    edges.append(
                        GraphEdge(
                            source=r.start_node["id"],
                            target=r.end_node["id"],
                            rel_type=r.get("type", "rel"),
                        )
                    )
        return GraphView(nodes=list(nodes.values()), edges=edges)


def get_graph_backend() -> GraphBackend:
    """Default graph backend (Neo4j)."""
    return Neo4jGraph()
