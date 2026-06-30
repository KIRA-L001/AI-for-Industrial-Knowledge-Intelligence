"""Embedding providers (provider-agnostic).

`EmbeddingProvider` is the interface used by the embedding service.
`SentenceTransformerEmbedder` is the production implementation; `HashingEmbedder`
is a deterministic, dependency-free fallback so semantic search works offline
and in tests without downloading models. The factory picks the real model when
sentence-transformers is installed, otherwise the hashing fallback.
"""

from __future__ import annotations

import hashlib
import math
import re
from functools import lru_cache
from typing import Protocol

from app.core.config import get_settings

_WORD_RE = re.compile(r"[A-Za-z0-9]+")


class EmbeddingProvider(Protocol):
    dim: int

    def embed(self, texts: list[str]) -> list[list[float]]: ...

    def embed_one(self, text: str) -> list[float]: ...


class HashingEmbedder:
    """Hashed bag-of-words embedder: deterministic, fast, no dependencies.

    Not as semantically rich as a transformer, but stable and adequate for
    offline development/testing of the retrieval pipeline.
    """

    def __init__(self, dim: int = 384) -> None:
        self.dim = dim

    def _vector(self, text: str) -> list[float]:
        vec = [0.0] * self.dim
        for token in _WORD_RE.findall(text.lower()):
            h = int(hashlib.md5(token.encode()).hexdigest(), 16)
            vec[h % self.dim] += 1.0
        norm = math.sqrt(sum(v * v for v in vec))
        if norm > 0:
            vec = [v / norm for v in vec]
        return vec

    def embed(self, texts: list[str]) -> list[list[float]]:
        return [self._vector(t) for t in texts]

    def embed_one(self, text: str) -> list[float]:
        return self._vector(text)


class SentenceTransformerEmbedder:
    """Sentence-Transformers backed embedder (production)."""

    def __init__(self, model_name: str) -> None:
        from sentence_transformers import SentenceTransformer

        self._model = SentenceTransformer(model_name)
        self.dim = int(self._model.get_sentence_embedding_dimension())

    def embed(self, texts: list[str]) -> list[list[float]]:
        vectors = self._model.encode(texts, normalize_embeddings=True)
        return [list(map(float, v)) for v in vectors]

    def embed_one(self, text: str) -> list[float]:
        return self.embed([text])[0]


@lru_cache
def get_embedder() -> EmbeddingProvider:
    """Return the configured embedder (cached), falling back to hashing."""
    settings = get_settings()
    try:
        return SentenceTransformerEmbedder(settings.embedding_model)
    except Exception:  # noqa: BLE001 - missing torch/model → deterministic fallback
        return HashingEmbedder(dim=settings.embedding_dim)
