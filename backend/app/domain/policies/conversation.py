from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True, slots=True)
class ConversationDecision:
    answer: str


class ConversationPolicy(Protocol):
    def evaluate(self, message: str) -> ConversationDecision | None: ...


@dataclass(frozen=True, slots=True)
class RegexConversationPolicy:
    pattern: str
    answer: str

    def evaluate(self, message: str) -> ConversationDecision | None:
        if re.fullmatch(self.pattern, message.strip(), flags=re.IGNORECASE):
            return ConversationDecision(self.answer)
        return None


@dataclass(frozen=True, slots=True)
class ConversationPolicyChain:
    policies: tuple[ConversationPolicy, ...]

    def evaluate(self, message: str) -> ConversationDecision | None:
        for policy in self.policies:
            if decision := policy.evaluate(message):
                return decision
        return None


def default_conversation_chain() -> ConversationPolicyChain:
    scope = "ITC Immunity Therapy Center, treatment packages, clinic information, and published costs"
    return ConversationPolicyChain(
        policies=(
            RegexConversationPolicy(
                r"(hi|hello|hey|halo|hai|good morning|good afternoon|good evening)( there)?[!.?]*",
                f"Hello! I can help you with questions about {scope} based on the supplied PlacidWay pages. "
                "What would you like to know?",
            ),
            RegexConversationPolicy(
                r"(thanks|thank you|thank you very much|terima kasih)[!.]*",
                "You're welcome! Feel free to ask another question about the clinic, treatment packages, or "
                "published costs.",
            ),
            RegexConversationPolicy(
                r"(what can you do|how can you help|who are you|kamu bisa apa)[?.!]*",
                f"I answer questions about {scope} using only the seven approved PlacidWay pages. I can also "
                "compare prices when the same information is available in the sources.",
            ),
            RegexConversationPolicy(
                r"(bye|goodbye|see you|sampai jumpa)[!.]*",
                "Goodbye! If you need more information later, I can help with PlacidWay clinic, package, and "
                "pricing questions.",
            ),
        )
    )

