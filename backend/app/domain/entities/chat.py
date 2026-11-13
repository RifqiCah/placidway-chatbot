from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum


class AnswerStatus(StrEnum):
    ANSWERED = "answered"
    UNKNOWN = "unknown"
    MEDICAL_SAFETY = "medical_safety"
    ACTION_UNSUPPORTED = "action_unsupported"
    OUT_OF_SCOPE = "out_of_scope"


class AnswerMode(StrEnum):
    LLM = "llm"
    EXTRACTIVE = "extractive"


@dataclass(frozen=True, slots=True)
class ChatMessage:
    role: str
    content: str


@dataclass(frozen=True, slots=True)
class Citation:
    title: str
    url: str


@dataclass(frozen=True, slots=True)
class ChatAnswer:
    answer: str
    status: AnswerStatus
    mode: AnswerMode
    citations: tuple[Citation, ...] = field(default_factory=tuple)
    disclaimer: str | None = None

