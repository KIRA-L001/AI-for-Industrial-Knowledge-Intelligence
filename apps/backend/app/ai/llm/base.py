"""Provider-agnostic LLM interface and message types.

Agents and the response composer depend only on `LLMProvider`. Concrete
providers (stub, Anthropic, OpenAI, Ollama) live alongside and are selected by
configuration, so the platform is never coupled to a single vendor.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import Literal, Protocol

Role = Literal["system", "user", "assistant"]


@dataclass
class Message:
    role: Role
    content: str


class LLMProvider(Protocol):
    """Minimal chat-completion surface used across the AI layer."""

    name: str

    async def complete(self, messages: list[Message], *, max_tokens: int = 1024) -> str: ...

    def stream(
        self, messages: list[Message], *, max_tokens: int = 1024
    ) -> AsyncIterator[str]: ...
