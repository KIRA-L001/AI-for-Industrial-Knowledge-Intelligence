"""Specialized AI agents and the planner that routes queries to them.

Each agent is an `AgentSpec` (a reusable system prompt + identity) consumed by
the orchestrator. The `Planner` performs lightweight intent classification to
pick the best agent; the LLM-backed router can replace it later without changing
callers. All six AI_AGENTS.md agents are represented.
"""

from __future__ import annotations

from app.ai.os.orchestrator import AgentSpec

KNOWLEDGE = AgentSpec(
    key="knowledge",
    title="Knowledge Copilot",
    system_prompt=(
        "You are the KIRA Knowledge Copilot, an industrial engineering assistant. "
        "Provide precise, citation-backed answers about plant documents and equipment."
    ),
)

DOCUMENT = AgentSpec(
    key="document",
    title="Document Intelligence Agent",
    system_prompt=(
        "You are the Document Intelligence Agent. Summarize, classify, and explain "
        "the content and structure of industrial documents from the context."
    ),
)

MAINTENANCE = AgentSpec(
    key="maintenance",
    title="Maintenance Agent",
    system_prompt=(
        "You are the Maintenance Agent. Analyze maintenance history, identify failure "
        "patterns, and recommend preventive and corrective actions for equipment."
    ),
)

COMPLIANCE = AgentSpec(
    key="compliance",
    title="Compliance Agent",
    system_prompt=(
        "You are the Compliance Agent. Map operations to Factory Act / OISD / PESO "
        "requirements, identify compliance gaps, and cite the governing standards."
    ),
)

RCA = AgentSpec(
    key="rca",
    title="Root Cause Analysis Agent",
    system_prompt=(
        "You are the RCA Agent. Analyze incidents, determine the most probable root "
        "cause from the evidence, and recommend preventive actions."
    ),
)

LESSONS = AgentSpec(
    key="lessons",
    title="Lessons Learned Agent",
    system_prompt=(
        "You are the Lessons Learned Agent. Detect recurring patterns across incidents "
        "and recommend operational improvements."
    ),
)

AGENTS: dict[str, AgentSpec] = {
    a.key: a for a in (KNOWLEDGE, DOCUMENT, MAINTENANCE, COMPLIANCE, RCA, LESSONS)
}

# Intent keywords → agent key (first match wins; order matters).
_ROUTING: list[tuple[str, tuple[str, ...]]] = [
    ("rca", ("root cause", "why did", "failure analysis", "incident", "rca")),
    ("maintenance", ("maintenance", "repair", "predict", "failure", "breakdown", "spare")),
    (
        "compliance",
        ("compliance", "oisd", "peso", "factory act", "audit", "regulation", "standard"),
    ),
    ("lessons", ("lessons", "recurring", "pattern", "improve", "best practice")),
    ("document", ("summarize", "summary", "classify", "what does this document", "metadata")),
]


class Planner:
    """Routes a query to the most appropriate agent via keyword intent matching."""

    def plan(self, query: str) -> AgentSpec:
        q = query.lower()
        for agent_key, keywords in _ROUTING:
            if any(kw in q for kw in keywords):
                return AGENTS[agent_key]
        return KNOWLEDGE


def get_agent(key: str) -> AgentSpec | None:
    return AGENTS.get(key)
