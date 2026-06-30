"""Chat / AI Copilot schemas."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ChatTurn(BaseModel):
    role: str  # "user" | "assistant"
    content: str


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    agent: str | None = None  # force a specific agent; otherwise auto-routed
    history: list[ChatTurn] = []


class ChatCitation(BaseModel):
    index: int
    chunk_id: str
    document_id: str
    page_number: int | None
    text: str
    score: float


class ChatResponse(BaseModel):
    agent: str
    answer: str
    confidence: float
    confidence_label: str
    citations: list[ChatCitation]


class AgentInfo(BaseModel):
    key: str
    title: str
