from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from threading import RLock


class JsonlGapRepository:
    def __init__(self, path: Path):
        self._path = path
        self._lock = RLock()
        self._path.parent.mkdir(parents=True, exist_ok=True)

    def append(self, question: str, reason: str) -> None:
        record = {"timestamp": datetime.now(UTC).isoformat(), "question": question, "reason": reason}
        try:
            with self._lock, self._path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(record, ensure_ascii=False) + "\n")
        except OSError:
            # Observability must not turn a safe fallback into a server error.
            pass

