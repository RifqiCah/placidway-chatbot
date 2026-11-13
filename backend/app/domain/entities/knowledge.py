from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class Passage:
    id: str
    source_id: str
    page_type: str
    title: str
    url: str
    text: str


@dataclass(frozen=True, slots=True)
class SourceSnapshot:
    id: str
    title: str
    url: str
    page_type: str
    chunks: int
    content_sha256: str


@dataclass(frozen=True, slots=True)
class KnowledgeSnapshot:
    refreshed_at: datetime
    sources: tuple[SourceSnapshot, ...]
    passages: tuple[Passage, ...]
    crawler_user_agent: str
    crawl_delay_seconds: float
    schema_version: int = 1


@dataclass(frozen=True, slots=True)
class SearchResult:
    passage: Passage
    score: float

