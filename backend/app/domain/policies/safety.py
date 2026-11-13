from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Protocol

from backend.app.domain.entities.chat import AnswerStatus


@dataclass(frozen=True, slots=True)
class SafetyDecision:
    status: AnswerStatus
    answer: str


class SafetyPolicy(Protocol):
    def evaluate(self, question: str) -> SafetyDecision | None: ...


@dataclass(frozen=True, slots=True)
class RegexSafetyPolicy:
    patterns: tuple[str, ...]
    decision: SafetyDecision

    def evaluate(self, question: str) -> SafetyDecision | None:
        lowered = question.casefold()
        return self.decision if any(re.search(pattern, lowered) for pattern in self.patterns) else None


@dataclass(frozen=True, slots=True)
class SafetyPolicyChain:
    policies: tuple[SafetyPolicy, ...]

    def evaluate(self, question: str) -> SafetyDecision | None:
        for policy in self.policies:
            if decision := policy.evaluate(question):
                return decision
        return None


def default_safety_chain() -> SafetyPolicyChain:
    return SafetyPolicyChain(
        policies=(
            RegexSafetyPolicy(
                patterns=(
                    r"\b(is|apakah)\b.{0,30}\b(safe|aman)\b.{0,40}\b(for me|untuk saya|diabetes|pregnan|hamil)",
                    r"\b(diagnos|should i|haruskah saya|cocok untuk saya|recommend.*dose|dosis)\b",
                ),
                decision=SafetyDecision(
                    AnswerStatus.MEDICAL_SAFETY,
                    "I can share information published on the supplied PlacidWay pages, but I cannot determine "
                    "whether a treatment is safe for your specific medical condition. Please discuss your medical "
                    "history and risks with a qualified doctor.",
                ),
            ),
            RegexSafetyPolicy(
                patterns=(
                    r"\b(book|schedule|reserve|buatkan|pesankan|jadwalkan)\b.{0,40}"
                    r"\b(appointment|consultation|janji|besok|tomorrow)\b",
                ),
                decision=SafetyDecision(
                    AnswerStatus.ACTION_UNSUPPORTED,
                    "I cannot book or schedule an appointment. Please use the PlacidWay contact or free-quote "
                    "form so their team can help with availability.",
                ),
            ),
            RegexSafetyPolicy(
                patterns=(
                    r"\b(weather|cuaca|forecast|temperature)\b",
                    r"\b(stock price|football|soccer score|resep masakan)\b",
                ),
                decision=SafetyDecision(
                    AnswerStatus.OUT_OF_SCOPE,
                    "That is outside this chatbot's knowledge base. I can only answer questions supported by the "
                    "seven supplied PlacidWay clinic, treatment, video, and pricing pages.",
                ),
            ),
        )
    )

