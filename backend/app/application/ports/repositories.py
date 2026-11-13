from typing import Protocol

from backend.app.domain.entities.knowledge import KnowledgeSnapshot


class KnowledgeRepository(Protocol):
    def load(self) -> KnowledgeSnapshot: ...

    def replace(self, snapshot: KnowledgeSnapshot) -> None: ...

    def revision(self) -> str: ...


class GapRepository(Protocol):
    def append(self, question: str, reason: str) -> None: ...

