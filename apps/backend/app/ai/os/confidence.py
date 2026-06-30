"""Confidence engine.

Derives a 0–1 confidence score for an answer from retrieval evidence: how many
citations support it and how strong their relevance scores are. Keeps the AI
layer honest — answers with thin or weak evidence score low.
"""

from __future__ import annotations

from app.services.retrieval import Citation


def compute_confidence(citations: list[Citation]) -> float:
    """Combine evidence count and top relevance into a 0–1 confidence score."""
    if not citations:
        return 0.0

    top = max(c.score for c in citations)
    # Normalize a possibly-unbounded rerank score into [0, 1].
    strength = top / (1.0 + abs(top)) if top > 0 else 0.0

    # More supporting citations → more confidence, with diminishing returns.
    coverage = min(len(citations), 4) / 4.0

    score = 0.65 * strength + 0.35 * coverage
    return round(max(0.0, min(1.0, score)), 3)


def confidence_label(score: float) -> str:
    if score >= 0.75:
        return "high"
    if score >= 0.45:
        return "medium"
    return "low"
