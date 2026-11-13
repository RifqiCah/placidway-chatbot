from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from threading import RLock

from backend.app.domain.entities.knowledge import KnowledgeSnapshot, Passage, SourceSnapshot


class JsonKnowledgeRepository:
    def __init__(self, path: Path):
        self._path = path
        self._lock = RLock()
        self._path.parent.mkdir(parents=True, exist_ok=True)

    def load(self) -> KnowledgeSnapshot:
        if not self._path.exists():
            raise FileNotFoundError("Knowledge base is missing. Run: python scripts/ingest.py")
        with self._lock:
            payload = json.loads(self._path.read_text(encoding="utf-8"))
        return KnowledgeSnapshot(
            schema_version=int(payload.get("schema_version", 1)),
            refreshed_at=datetime.fromisoformat(payload["refreshed_at"]),
            crawler_user_agent=payload["crawler"]["user_agent"],
            crawl_delay_seconds=float(payload["crawler"]["crawl_delay_seconds"]),
            sources=tuple(SourceSnapshot(**source) for source in payload["sources"]),
            passages=tuple(Passage(**passage) for passage in payload["chunks"]),
        )

    def replace(self, snapshot: KnowledgeSnapshot) -> None:
        payload = {
            "schema_version": snapshot.schema_version,
            "refreshed_at": snapshot.refreshed_at.isoformat(),
            "crawler": {
                "user_agent": snapshot.crawler_user_agent,
                "crawl_delay_seconds": snapshot.crawl_delay_seconds,
            },
            "sources": [
                {
                    "id": source.id,
                    "title": source.title,
                    "url": source.url,
                    "page_type": source.page_type,
                    "chunks": source.chunks,
                    "content_sha256": source.content_sha256,
                }
                for source in snapshot.sources
            ],
            "chunks": [
                {
                    "id": passage.id,
                    "source_id": passage.source_id,
                    "page_type": passage.page_type,
                    "title": passage.title,
                    "url": passage.url,
                    "text": passage.text,
                }
                for passage in snapshot.passages
            ],
        }
        temporary = self._path.with_suffix(".tmp")
        with self._lock:
            temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
            temporary.replace(self._path)

    def revision(self) -> str:
        if not self._path.exists():
            return "missing"
        stat = self._path.stat()
        return f"{stat.st_mtime_ns}:{stat.st_size}"

