from dataclasses import dataclass
from datetime import datetime

from backend.app.application.ports.crawler import CrawlerPort
from backend.app.application.ports.repositories import KnowledgeRepository


@dataclass(frozen=True, slots=True)
class RefreshKnowledgeResult:
    sources: int
    passages: int
    refreshed_at: datetime


@dataclass(slots=True)
class RefreshKnowledgeUseCase:
    crawler: CrawlerPort
    repository: KnowledgeRepository

    def execute(self) -> RefreshKnowledgeResult:
        snapshot = self.crawler.crawl()
        self.repository.replace(snapshot)
        return RefreshKnowledgeResult(
            sources=len(snapshot.sources),
            passages=len(snapshot.passages),
            refreshed_at=snapshot.refreshed_at,
        )

