from typing import Protocol

from backend.app.domain.entities.knowledge import KnowledgeSnapshot


class CrawlerPort(Protocol):
    def crawl(self) -> KnowledgeSnapshot: ...

