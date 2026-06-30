"""AI Copilot endpoints: list agents, ask (JSON), and stream (SSE)."""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.api.deps import CurrentUser, get_copilot_service
from app.schemas.chat import (
    AgentInfo,
    ChatCitation,
    ChatRequest,
    ChatResponse,
)
from app.services.copilot import CopilotService

router = APIRouter(tags=["chat"])

Copilot = Annotated[CopilotService, Depends(get_copilot_service)]


@router.get("/agents", response_model=list[AgentInfo])
async def list_agents(_: CurrentUser, service: Copilot) -> list[AgentInfo]:
    return [AgentInfo(**a) for a in service.list_agents()]


@router.post("/chat", response_model=ChatResponse)
async def chat(payload: ChatRequest, user: CurrentUser, service: Copilot) -> ChatResponse:
    """Ask the AI Copilot a question; returns a cited, confidence-scored answer."""
    result = await service.ask(
        user.organization_id,
        payload.message,
        agent_key=payload.agent,
        history=[(t.role, t.content) for t in payload.history],
    )
    return ChatResponse(
        agent=result.agent,
        answer=result.answer,
        confidence=result.confidence,
        confidence_label=result.confidence_label,
        citations=[
            ChatCitation(
                index=i + 1,
                chunk_id=c.chunk_id,
                document_id=c.document_id,
                page_number=c.page_number,
                text=c.text,
                score=c.score,
            )
            for i, c in enumerate(result.citations)
        ],
    )


@router.post("/chat/stream")
async def chat_stream(
    payload: ChatRequest, user: CurrentUser, service: Copilot
) -> StreamingResponse:
    """Stream the Copilot answer as Server-Sent Events."""

    async def event_source() -> AsyncIterator[str]:
        async for token in service.stream(
            user.organization_id,
            payload.message,
            agent_key=payload.agent,
            history=[(t.role, t.content) for t in payload.history],
        ):
            yield f"data: {token}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_source(), media_type="text/event-stream")
