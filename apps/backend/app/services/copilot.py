"""AI Copilot service: routes a question to an agent and runs the orchestrator."""

from __future__ import annotations

import uuid
from collections.abc import AsyncIterator

from app.ai.agents.registry import AGENTS, Planner, get_agent
from app.ai.llm.base import Message
from app.ai.os.orchestrator import AgentAnswer, AgentSpec, AIOrchestrator


class CopilotService:
    """Public entrypoint for the AI Copilot used by the chat API."""

    def __init__(self, orchestrator: AIOrchestrator, planner: Planner | None = None) -> None:
        self.orchestrator = orchestrator
        self.planner = planner or Planner()

    def _resolve(self, query: str, agent_key: str | None) -> AgentSpec:
        if agent_key:
            spec = get_agent(agent_key)
            if spec is not None:
                return spec
        return self.planner.plan(query)

    async def ask(
        self,
        organization_id: uuid.UUID,
        query: str,
        *,
        agent_key: str | None = None,
        history: list[tuple[str, str]] | None = None,
    ) -> AgentAnswer:
        spec = self._resolve(query, agent_key)
        msgs = [Message(role=r, content=c) for r, c in (history or [])]  # type: ignore[arg-type]
        return await self.orchestrator.run(organization_id, spec, query, history=msgs)

    async def stream(
        self,
        organization_id: uuid.UUID,
        query: str,
        *,
        agent_key: str | None = None,
        history: list[tuple[str, str]] | None = None,
    ) -> AsyncIterator[str]:
        spec = self._resolve(query, agent_key)
        msgs = [Message(role=r, content=c) for r, c in (history or [])]  # type: ignore[arg-type]
        async for token in self.orchestrator.stream(organization_id, spec, query, history=msgs):
            yield token

    @staticmethod
    def list_agents() -> list[dict[str, str]]:
        return [{"key": a.key, "title": a.title} for a in AGENTS.values()]
