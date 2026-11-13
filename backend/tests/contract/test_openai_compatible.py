import asyncio
import json

import httpx

from backend.app.domain.entities.knowledge import Passage
from backend.app.infrastructure.ai.openai_compatible import OpenAICompatibleLLM

PASSAGE = Passage("1", "source", "Pricing", "Price page", "https://example.com", "Price starts at $100 USD.")


def make_transport(answer: str) -> httpx.MockTransport:
    def handler(request: httpx.Request) -> httpx.Response:
        request_body = json.loads(request.content)
        assert request.url.path == "/v1/chat/completions"
        assert request_body["response_format"] == {"type": "json_object"}
        assert request_body["max_tokens"] == 800
        content = json.dumps({"is_answerable": True, "answer": answer, "source_indices": [1]})
        return httpx.Response(200, json={"choices": [{"message": {"content": content}}]})

    return httpx.MockTransport(handler)


def test_adapter_accepts_grounded_provider_response() -> None:
    adapter = OpenAICompatibleLLM(
        "test", "https://example.com/v1", "test-model", transport=make_transport("It starts at $100 USD.")
    )
    result = asyncio.run(adapter.generate("What is the price?", "", (PASSAGE,)))
    assert result is not None and result.is_answerable


def test_adapter_rejects_provider_invented_price() -> None:
    adapter = OpenAICompatibleLLM(
        "test", "https://example.com/v1", "test-model", transport=make_transport("It costs $50 USD.")
    )
    result = asyncio.run(adapter.generate("What is the price?", "", (PASSAGE,)))
    assert result is not None and not result.is_answerable

