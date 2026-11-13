from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from backend.app.core.container import get_container  # noqa: E402


if __name__ == "__main__":
    result = get_container().refresh_knowledge.execute()
    print(
        f"Ingested {result.sources} sources into {result.passages} chunks "
        f"at {result.refreshed_at.isoformat()}"
    )

