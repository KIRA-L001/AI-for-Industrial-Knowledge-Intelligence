"""AI Orchestrator — the heart of the Industrial AI Operating System.

Pipeline: plan (route to an agent) → retrieve cited context → compose a grounded
answer via the provider-agnostic LLM → score confidence → attach citations. The
specialized agents (Phase 11) supply the system prompt and post-processing; the
orchestrator wires them to retrieval, the LLM, and the confidence/citation
engines so every answer is grounded and traceable.
"""

from __future__ import annotations

import uuid
from collections.abc import AsyncIterator
from dataclasses import dataclass, field

from app.ai.llm.base import LLMProvider, Message
from app.ai.os.confidence import compute_confidence, confidence_label
from app.services.retrieval import Citation, RetrievalService


@dataclass
class AgentSpec:
    """Describes a specialized agent's behavior to the orchestrator."""

    key: str
    title: str
    system_prompt: str


@dataclass
class AgentAnswer:
    agent: str
    answer: str
    confidence: float
    confidence_label: str
    citations: list[Citation] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)


def _build_messages(
    spec: AgentSpec, query: str, context: str, history: list[Message]
) -> list[Message]:
    system = (
        f"{spec.system_prompt}\n\n"
        "Answer using ONLY the provided context. Cite supporting passages as [n]. "
        "If the context is insufficient, say so explicitly.\n\n"
        f"Context:\n{context if context else '(no relevant documents found)'}"
    )
    return [Message(role="system", content=system), *history, Message(role="user", content=query)]


class AIOrchestrator:
    """Coordinates retrieval, the LLM, and the confidence/citation engines."""

    def __init__(self, retrieval: RetrievalService, llm: LLMProvider) -> None:
        self.retrieval = retrieval
        self.llm = llm

    async def run(
        self,
        organization_id: uuid.UUID,
        spec: AgentSpec,
        query: str,
        *,
        history: list[Message] | None = None,
        limit: int = 6,
    ) -> AgentAnswer:
        retrieval = await self.retrieval.retrieve(organization_id, query, limit=limit)
        messages = _build_messages(spec, query, retrieval.context, history or [])
        answer = await self.llm.complete(messages)
        confidence = compute_confidence(retrieval.citations)
        return AgentAnswer(
            agent=spec.key,
            answer=answer,
            confidence=confidence,
            confidence_label=confidence_label(confidence),
            citations=retrieval.citations,
        )

    async def stream(
        self,
        organization_id: uuid.UUID,
        spec: AgentSpec,
        query: str,
        *,
        history: list[Message] | None = None,
        limit: int = 6,
    ) -> AsyncIterator[str]:
        retrieval = await self.retrieval.retrieve(organization_id, query, limit=limit)
        messages = _build_messages(spec, query, retrieval.context, history or [])
        async for token in self.llm.stream(messages):
            yield token
