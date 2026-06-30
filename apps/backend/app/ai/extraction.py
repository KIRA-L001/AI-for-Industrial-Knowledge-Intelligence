"""Entity and relationship extraction from document text.

Defines a strategy interface so an LLM-backed extractor can replace the default
heuristic one without changing callers. The heuristic extractor recognizes
industrial equipment tags and compliance standards and links entities that
co-occur, giving a usable knowledge graph offline.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Protocol


@dataclass(frozen=True)
class ExtractedEntity:
    name: str
    entity_type: str  # equipment | standard | organization | ...
    normalized: str


@dataclass(frozen=True)
class ExtractedRelationship:
    source: str  # normalized entity name
    target: str
    rel_type: str


@dataclass
class ExtractionResult:
    entities: list[ExtractedEntity] = field(default_factory=list)
    relationships: list[ExtractedRelationship] = field(default_factory=list)


class ExtractionStrategy(Protocol):
    """Pluggable extraction backend."""

    def extract(self, text: str) -> ExtractionResult: ...


# Equipment tags like P-101, V-2003, HX-12, PSV-4501.
_TAG_RE = re.compile(r"\b([A-Z]{1,4}-\d{2,5})\b")
# Common Indian/industrial compliance standards.
_STANDARD_RE = re.compile(
    r"\b(OISD(?:-STD)?-?\d{2,3}|PESO|Factory Act|API\s?\d{3,4}"
    r"|ASME(?:\s[A-Z0-9.]+)?|IS\s?\d{3,5})\b",
    re.IGNORECASE,
)


def _normalize(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip()).upper()


class HeuristicExtractor:
    """Regex/co-occurrence extractor (default, dependency-free)."""

    def extract(self, text: str) -> ExtractionResult:
        entities: dict[str, ExtractedEntity] = {}

        for match in _TAG_RE.finditer(text):
            norm = _normalize(match.group(1))
            entities.setdefault(
                norm, ExtractedEntity(name=match.group(1), entity_type="equipment", normalized=norm)
            )
        for match in _STANDARD_RE.finditer(text):
            norm = _normalize(match.group(1))
            entities.setdefault(
                norm, ExtractedEntity(name=match.group(1), entity_type="standard", normalized=norm)
            )

        # Link each equipment tag to each standard mentioned in the same text
        # (a coarse "governed_by" relation, refined by the LLM extractor later).
        equipment = [e for e in entities.values() if e.entity_type == "equipment"]
        standards = [e for e in entities.values() if e.entity_type == "standard"]
        relationships = [
            ExtractedRelationship(
                source=eq.normalized, target=st.normalized, rel_type="governed_by"
            )
            for eq in equipment
            for st in standards
        ]

        return ExtractionResult(entities=list(entities.values()), relationships=relationships)


def get_extractor() -> ExtractionStrategy:
    """Default extraction strategy."""
    return HeuristicExtractor()
