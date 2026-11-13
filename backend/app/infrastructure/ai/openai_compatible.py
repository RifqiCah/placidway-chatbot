from __future__ import annotations

import json
import re
from typing import Any

import httpx

from backend.app.application.dto.ai import GeneratedAnswer
from backend.app.domain.entities.knowledge import Passage
from backend.app.domain.value_objects.money import has_unsupported_money
from backend.app.infrastructure.ai.prompt_builder import SYSTEM_PROMPT, build_user_prompt


class OpenAICompatibleLLM:
    def __init__(
        self,
        api_key: str,
        base_url: str,
        model: str,
        timeout_seconds: float = 45.0,
        transport: httpx.AsyncBaseTransport | None = None,
    ):
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._model = model
        self._timeout_seconds = timeout_seconds
        self._transport = transport

    @property
    def is_configured(self) -> bool:
        return bool(self._api_key)

    async def generate(
        self,
        question: str,
        history: str,
        evidence: tuple[Passage, ...],
    ) -> GeneratedAnswer | None:
        if not self.is_configured:
            return None
        payload = {
            "model": self._model,
            "temperature": 0,
            "max_tokens": 800,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": build_user_prompt(question, history, evidence)},
            ],
        }
        try:
            async with httpx.AsyncClient(timeout=self._timeout_seconds, transport=self._transport) as client:
                response = await client.post(
                    f"{self._base_url}/chat/completions",
                    headers={"Authorization": f"Bearer {self._api_key}"},
                    json=payload,
                )
                response.raise_for_status()
            parsed = self._parse_json(response.json()["choices"][0]["message"]["content"])
        except (httpx.HTTPError, KeyError, TypeError, ValueError, json.JSONDecodeError):
            return None

        indices = tuple(
            sorted(
                {
                    int(value)
                    for value in parsed.get("source_indices", [])
                    if str(value).isdigit() and 1 <= int(value) <= len(evidence)
                }
            )
        )
        answer = str(parsed.get("answer", "")).strip()
        selected_evidence = "\n".join(evidence[index - 1].text for index in indices)
        answerable = bool(parsed.get("is_answerable"))
        if answerable and (not indices or not answer or has_unsupported_money(answer, selected_evidence)):
            answerable = False
        return GeneratedAnswer(answer, indices, answerable)

    @staticmethod
    def _parse_json(content: str) -> dict[str, Any]:
        content = content.strip()
        if content.startswith("```"):
            content = re.sub(r"^```(?:json)?\s*|\s*```$", "", content, flags=re.IGNORECASE)
        parsed: object = json.loads(content)
        if not isinstance(parsed, dict):
            raise ValueError("LLM response must be a JSON object")
        return {str(key): value for key, value in parsed.items()}

