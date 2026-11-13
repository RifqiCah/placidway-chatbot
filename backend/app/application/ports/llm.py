from __future__ import annotations

from typing import Protocol

from backend.app.application.dto.ai import GeneratedAnswer
from backend.app.domain.entities.knowledge import Passage


class LLMPort(Protocol):
    @property
    def is_configured(self) -> bool: ...

    async def generate(
        self,
        question: str,
        history: str,
        evidence: tuple[Passage, ...],
    ) -> GeneratedAnswer | None: ...

