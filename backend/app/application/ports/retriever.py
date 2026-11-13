from typing import Protocol

from backend.app.domain.entities.knowledge import SearchResult


class RetrieverPort(Protocol):
    def search(self, query: str, limit: int = 6) -> tuple[SearchResult, ...]: ...

