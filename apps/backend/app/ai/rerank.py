"""Cross-encoder reranking with a dependency-free lexical fallback.

`Reranker` scores (query, passage) pairs for relevance. `CrossEncoderReranker`
uses a Sentence-Transformers cross-encoder in production; `LexicalReranker`
scores by token overlap so the retrieval pipeline reranks offline and in tests.
"""

from __future__ import annotations

import re
from functools import lru_cache
from typing import Protocol

from app.core.config import get_settings

_WORD_RE = re.compile(r"[A-Za-z0-9]+")


class Reranker(Protocol):
    def score(self, query: str, passages: list[str]) -> list[float]: ...


class LexicalReranker:
    """Jaccard token-overlap reranker (deterministic, no dependencies)."""

    def score(self, query: str, passages: list[str]) -> list[float]:
        q_tokens = set(_WORD_RE.findall(query.lower()))
        if not q_tokens:
            return [0.0] * len(passages)
        scores: list[float] = []
        for passage in passages:
            p_tokens = set(_WORD_RE.findall(passage.lower()))
            if not p_tokens:
                scores.append(0.0)
                continue
            overlap = len(q_tokens & p_tokens)
            union = len(q_tokens | p_tokens)
            scores.append(overlap / union if union else 0.0)
        return scores


class CrossEncoderReranker:
    """Sentence-Transformers CrossEncoder reranker (production)."""

    def __init__(self, model_name: str) -> None:
        from sentence_transformers import CrossEncoder

        self._model = CrossEncoder(model_name)

    def score(self, query: str, passages: list[str]) -> list[float]:
        if not passages:
            return []
        pairs = [(query, p) for p in passages]
        return [float(s) for s in self._model.predict(pairs)]


@lru_cache
def get_reranker() -> Reranker:
    """Return the configured reranker (cached), falling back to lexical."""
    settings = get_settings()
    try:
        return CrossEncoderReranker(settings.reranker_model)
    except Exception:  # noqa: BLE001 - missing model → deterministic fallback
        return LexicalReranker()
