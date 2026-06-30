"""Text chunking for retrieval.

Splits page text into overlapping, roughly word-bounded chunks. Pure Python and
deterministic so it is unit-testable without any model dependencies.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class TextChunk:
    """A contiguous slice of a page's text."""

    index: int
    page_number: int
    text: str
    char_start: int
    char_end: int


def chunk_text(
    text: str,
    page_number: int,
    *,
    chunk_size: int = 1000,
    overlap: int = 150,
    start_index: int = 0,
) -> list[TextChunk]:
    """Split `text` into overlapping chunks, breaking on whitespace when possible."""
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be in [0, chunk_size)")

    text = text.strip()
    if not text:
        return []

    chunks: list[TextChunk] = []
    index = start_index
    pos = 0
    length = len(text)

    while pos < length:
        end = min(pos + chunk_size, length)
        # Prefer to break at the last whitespace within the window.
        if end < length:
            space = text.rfind(" ", pos, end)
            if space > pos:
                end = space
        piece = text[pos:end].strip()
        if piece:
            chunks.append(
                TextChunk(
                    index=index,
                    page_number=page_number,
                    text=piece,
                    char_start=pos,
                    char_end=end,
                )
            )
            index += 1
        if end >= length:
            break
        pos = max(end - overlap, pos + 1)

    return chunks
