from typing import Protocol

from backend.app.application.dto.fallback import FallbackAnswer
from backend.app.domain.entities.knowledge import SearchResult


class FallbackAnswerPort(Protocol):
    def generate(self, question: str, results: tuple[SearchResult, ...]) -> FallbackAnswer: ...

