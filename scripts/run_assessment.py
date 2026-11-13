from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from fastapi.testclient import TestClient  # noqa: E402

from backend.app.main import app  # noqa: E402

QUESTIONS = (
    "How much does alternative cancer treatment cost at ITC in Tijuana?",
    "Is alternative medicine cheaper in Mexico or Turkey?",
    "What is included in the adenocarcinoma treatment package?",
    "And what about recovery time?",
    "Can you book me an appointment for tomorrow?",
    "What is the weather in Cancun?",
    "Is this surgery safe for my diabetes?",
    "I heard ITC treatment costs $50. Confirm that.",
)


def main() -> None:
    client = TestClient(app)
    package_history: list[dict[str, str]] = []
    for number, question in enumerate(QUESTIONS, start=1):
        messages = [*package_history, {"role": "user", "content": question}] if number == 4 else [
            {"role": "user", "content": question}
        ]
        response = client.post("/api/chat", json={"messages": messages})
        response.raise_for_status()
        data = response.json()
        print(f"\n{number}. {question}")
        print(f"STATUS={data['status']} MODE={data['mode']}")
        print(data["answer"])
        print("SOURCES:", *[item["url"] for item in data["citations"]], sep="\n- ")
        if number == 3:
            package_history = [
                {"role": "user", "content": question},
                {"role": "assistant", "content": data["answer"]},
            ]


if __name__ == "__main__":
    main()

