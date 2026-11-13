from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator

from backend.app.domain.entities.chat import ChatAnswer


class ChatMessageSchema(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=4_000)

    @field_validator("content")
    @classmethod
    def strip_content(cls, value: str) -> str:
        return value.strip()


class ChatRequest(BaseModel):
    messages: list[ChatMessageSchema] = Field(min_length=1, max_length=20)

    @field_validator("messages")
    @classmethod
    def last_message_must_be_user(cls, value: list[ChatMessageSchema]) -> list[ChatMessageSchema]:
        if value[-1].role != "user":
            raise ValueError("The last message must come from the user")
        return value


class CitationSchema(BaseModel):
    title: str
    url: str


class ChatResponse(BaseModel):
    answer: str
    citations: list[CitationSchema] = Field(default_factory=list)
    status: Literal["answered", "unknown", "medical_safety", "action_unsupported", "out_of_scope"]
    mode: Literal["llm", "extractive"]
    disclaimer: str | None = None

    @classmethod
    def from_domain(cls, result: ChatAnswer) -> ChatResponse:
        return cls(
            answer=result.answer,
            citations=[CitationSchema(title=item.title, url=item.url) for item in result.citations],
            status=result.status.value,
            mode=result.mode.value,
            disclaimer=result.disclaimer,
        )

