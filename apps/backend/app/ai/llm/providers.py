"""Concrete LLM providers and the configuration-driven factory."""

from __future__ import annotations

from collections.abc import AsyncIterator
from functools import lru_cache

from app.ai.llm.base import LLMProvider, Message
from app.core.config import get_settings


class StubLLM:
    """Deterministic, offline provider used when no real LLM is configured.

    Produces a grounded, citation-referencing answer by extracting the context
    block from the prompt. Good enough to exercise the full agent pipeline and
    tests without network access or API keys.
    """

    name = "stub"

    def _answer(self, messages: list[Message]) -> str:
        question = next(
            (m.content for m in reversed(messages) if m.role == "user"), ""
        ).strip()
        context = "\n".join(m.content for m in messages if m.role == "system")
        snippet = ""
        marker = "Context:"
        if marker in context:
            body = context.split(marker, 1)[1].strip()
            snippet = " ".join(body.split())[:400]
        if snippet:
            return (
                f"Based on the retrieved context, here is the analysis for: "
                f"\"{question}\".\n\n{snippet}\n\nKey supporting evidence is cited above [1]."
            )
        return (
            f"I could not find supporting documents for: \"{question}\". "
            "Please ingest and process relevant documents, then try again."
        )

    async def complete(self, messages: list[Message], *, max_tokens: int = 1024) -> str:
        return self._answer(messages)[: max_tokens * 4]

    async def stream(
        self, messages: list[Message], *, max_tokens: int = 1024
    ) -> AsyncIterator[str]:
        for token in self._answer(messages).split(" "):
            yield token + " "


class AnthropicLLM:
    """Anthropic Claude provider (production)."""

    name = "anthropic"

    def __init__(self, model: str, api_key: str) -> None:
        from anthropic import AsyncAnthropic

        self._client = AsyncAnthropic(api_key=api_key)
        self._model = model

    @staticmethod
    def _split(messages: list[Message]) -> tuple[str, list[dict[str, str]]]:
        system = "\n\n".join(m.content for m in messages if m.role == "system")
        turns = [
            {"role": m.role, "content": m.content}
            for m in messages
            if m.role in ("user", "assistant")
        ]
        return system, turns

    async def complete(self, messages: list[Message], *, max_tokens: int = 1024) -> str:
        system, turns = self._split(messages)
        resp = await self._client.messages.create(
            model=self._model, max_tokens=max_tokens, system=system, messages=turns
        )
        return "".join(block.text for block in resp.content if block.type == "text")

    async def stream(
        self, messages: list[Message], *, max_tokens: int = 1024
    ) -> AsyncIterator[str]:
        system, turns = self._split(messages)
        async with self._client.messages.stream(
            model=self._model, max_tokens=max_tokens, system=system, messages=turns
        ) as stream:
            async for text in stream.text_stream:
                yield text


class OpenAILLM:
    """OpenAI provider (production)."""

    name = "openai"

    def __init__(self, model: str, api_key: str, base_url: str | None = None) -> None:
        from openai import AsyncOpenAI

        self._client = AsyncOpenAI(api_key=api_key, base_url=base_url or None)
        self._model = model

    async def complete(self, messages: list[Message], *, max_tokens: int = 1024) -> str:
        resp = await self._client.chat.completions.create(
            model=self._model,
            max_tokens=max_tokens,
            messages=[{"role": m.role, "content": m.content} for m in messages],
        )
        return resp.choices[0].message.content or ""

    async def stream(
        self, messages: list[Message], *, max_tokens: int = 1024
    ) -> AsyncIterator[str]:
        stream = await self._client.chat.completions.create(
            model=self._model,
            max_tokens=max_tokens,
            messages=[{"role": m.role, "content": m.content} for m in messages],
            stream=True,
        )
        async for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta


class OllamaLLM:
    """Local Ollama provider (production, on-prem)."""

    name = "ollama"

    def __init__(self, model: str, base_url: str) -> None:
        self._model = model
        self._base_url = base_url.rstrip("/")

    def _prompt(self, messages: list[Message]) -> str:
        return "\n".join(f"{m.role}: {m.content}" for m in messages) + "\nassistant:"

    async def complete(self, messages: list[Message], *, max_tokens: int = 1024) -> str:
        import httpx

        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(
                f"{self._base_url}/api/generate",
                json={"model": self._model, "prompt": self._prompt(messages), "stream": False},
            )
            resp.raise_for_status()
            return resp.json().get("response", "")

    async def stream(
        self, messages: list[Message], *, max_tokens: int = 1024
    ) -> AsyncIterator[str]:
        yield await self.complete(messages, max_tokens=max_tokens)


@lru_cache
def get_llm() -> LLMProvider:
    """Return the configured LLM provider, defaulting to the offline stub."""
    settings = get_settings()
    provider = settings.llm_provider
    try:
        if provider == "anthropic" and settings.llm_api_key:
            return AnthropicLLM(settings.llm_model or "claude-opus-4-8", settings.llm_api_key)
        if provider == "openai" and settings.llm_api_key:
            return OpenAILLM(
                settings.llm_model or "gpt-4o", settings.llm_api_key, settings.llm_base_url
            )
        if provider == "ollama":
            return OllamaLLM(
                settings.llm_model or "llama3", settings.llm_base_url or "http://localhost:11434"
            )
    except Exception:  # noqa: BLE001 - any adapter init failure → stub
        return StubLLM()
    return StubLLM()
