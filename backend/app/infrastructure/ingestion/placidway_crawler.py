from __future__ import annotations

import hashlib
import time
import urllib.robotparser
from datetime import UTC, datetime

import httpx

from backend.app.domain.entities.knowledge import KnowledgeSnapshot, Passage, SourceSnapshot
from backend.app.domain.entities.source import Source
from backend.app.infrastructure.ingestion.chunker import TextChunker
from backend.app.infrastructure.ingestion.html_extractor import HtmlContentExtractor


class PlacidWayCrawler:
    def __init__(
        self,
        sources: tuple[Source, ...],
        extractor: HtmlContentExtractor,
        chunker: TextChunker,
        user_agent: str,
        robots_url: str = "https://www.placidway.com/robots.txt",
        minimum_delay_seconds: float = 3.0,
    ):
        self._sources = sources
        self._extractor = extractor
        self._chunker = chunker
        self._user_agent = user_agent
        self._robots_url = robots_url
        self._minimum_delay = minimum_delay_seconds

    def crawl(self) -> KnowledgeSnapshot:
        passages: list[Passage] = []
        source_snapshots: list[SourceSnapshot] = []
        with httpx.Client(
            headers={"User-Agent": self._user_agent, "Accept": "text/html,application/xhtml+xml"},
            follow_redirects=True,
            timeout=30.0,
        ) as client:
            robots, crawl_delay = self._load_robots(client)
            last_request_at = 0.0
            for source in self._sources:
                if not robots.can_fetch(self._user_agent, source.url):
                    raise PermissionError(f"robots.txt disallows {source.url}")
                wait_for = crawl_delay - (time.monotonic() - last_request_at)
                if wait_for > 0:
                    time.sleep(wait_for)
                response = client.get(source.url)
                last_request_at = time.monotonic()
                response.raise_for_status()
                extracted = self._extractor.extract(response.text)
                source_passages = self._chunker.chunk(source, extracted)
                if not source_passages:
                    raise ValueError(f"No usable content extracted from {source.url}")
                passages.extend(source_passages)
                source_snapshots.append(
                    SourceSnapshot(
                        id=source.id,
                        title=extracted.title or source.title,
                        url=source.url,
                        page_type=source.page_type,
                        chunks=len(source_passages),
                        content_sha256=hashlib.sha256(response.content).hexdigest(),
                    )
                )
        return KnowledgeSnapshot(
            refreshed_at=datetime.now(UTC),
            sources=tuple(source_snapshots),
            passages=tuple(passages),
            crawler_user_agent=self._user_agent,
            crawl_delay_seconds=crawl_delay,
        )

    def _load_robots(self, client: httpx.Client) -> tuple[urllib.robotparser.RobotFileParser, float]:
        response = client.get(self._robots_url)
        response.raise_for_status()
        parser = urllib.robotparser.RobotFileParser()
        parser.set_url(self._robots_url)
        parser.parse(response.text.splitlines())
        declared = parser.crawl_delay(self._user_agent) or parser.crawl_delay("*") or self._minimum_delay
        return parser, max(float(declared), self._minimum_delay)

