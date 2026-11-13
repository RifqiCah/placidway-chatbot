from __future__ import annotations

import hashlib

from backend.app.domain.entities.knowledge import Passage
from backend.app.domain.entities.source import Source
from backend.app.infrastructure.ingestion.html_extractor import ExtractedPage


class TextChunker:
    def __init__(self, target_chars: int = 1_100, overlap_blocks: int = 1):
        self._target_chars = target_chars
        self._overlap_blocks = overlap_blocks

    def chunk(self, source: Source, page: ExtractedPage) -> tuple[Passage, ...]:
        passages: list[Passage] = []
        current: list[str] = []
        current_size = 0

        def emit() -> None:
            nonlocal current, current_size
            if not current:
                return
            text = "\n".join(current).strip()
            if len(text) >= 40:
                raw_id = f"{source.id}:{len(passages)}:{text[:100]}"
                passages.append(
                    Passage(
                        id=hashlib.sha256(raw_id.encode("utf-8")).hexdigest()[:16],
                        source_id=source.id,
                        page_type=source.page_type,
                        title=page.title or source.title,
                        url=source.url,
                        text=text,
                    )
                )
            current = current[-self._overlap_blocks :] if self._overlap_blocks else []
            current_size = sum(len(item) for item in current)

        for block in page.blocks:
            if current and current_size + len(block) > self._target_chars:
                emit()
            current.append(block)
            current_size += len(block)
        emit()
        return tuple(passages)

