import asyncio

from backend.app.application.dto.ai import GeneratedAnswer
from backend.app.application.dto.fallback import FallbackAnswer
from backend.app.application.use_cases.answer_question import AnswerQuestionUseCase
from backend.app.domain.entities.chat import AnswerMode, AnswerStatus, ChatMessage
from backend.app.domain.entities.knowledge import Passage, SearchResult
from backend.app.domain.policies.conversation import default_conversation_chain
from backend.app.domain.policies.safety import default_safety_chain

PASSAGE = Passage("1", "source", "Clinic", "Source", "https://example.com", "The supported price is $100 USD.")


class FakeRetriever:
    def search(self, query: str, limit: int = 6) -> tuple[SearchResult, ...]:
        return (SearchResult(PASSAGE, 5.0),)


class FakeLlm:
    is_configured = True

    async def generate(self, question: str, history: str, evidence: tuple[Passage, ...]) -> GeneratedAnswer:
        return GeneratedAnswer("The supported price is $100 USD.", (1,), True)


class UnanswerableLlm:
    is_configured = True

    async def generate(self, question: str, history: str, evidence: tuple[Passage, ...]) -> GeneratedAnswer:
        return GeneratedAnswer("", (), False)


class FailingLlm:
    is_configured = True

    async def generate(self, question: str, history: str, evidence: tuple[Passage, ...]) -> GeneratedAnswer:
        raise AssertionError("The deterministic price guardrail must run before the LLM")


class FakeFallback:
    def generate(self, question: str, results: tuple[SearchResult, ...]) -> FallbackAnswer:
        return FallbackAnswer("fallback", (PASSAGE,))


class InMemoryGapRepository:
    def __init__(self) -> None:
        self.records: list[tuple[str, str]] = []

    def append(self, question: str, reason: str) -> None:
        self.records.append((question, reason))


def test_use_case_depends_on_ports_and_returns_server_owned_citation() -> None:
    use_case = AnswerQuestionUseCase(
        FakeRetriever(),
        FakeLlm(),
        FakeFallback(),
        default_conversation_chain(),
        default_safety_chain(),
        InMemoryGapRepository(),
    )
    result = asyncio.run(use_case.execute((ChatMessage("user", "What is the supported price?"),)))
    assert result.status is AnswerStatus.ANSWERED
    assert result.citations[0].url == "https://example.com"


def test_short_self_contained_question_starts_a_new_topic() -> None:
    messages = (
        ChatMessage("user", "What is included in the adenocarcinoma treatment package?"),
        ChatMessage("assistant", "The package includes supported therapies."),
        ChatMessage("user", "And what about recovery time?"),
        ChatMessage("assistant", "The page does not specify recovery time."),
        ChatMessage("user", "Is Live Cell Therapy cheaper in Mexico or Turkey?"),
    )

    assert AnswerQuestionUseCase._retrieval_query(messages) == messages[-1].content


def test_explicit_follow_up_uses_recent_user_context() -> None:
    messages = (
        ChatMessage("user", "What is included in the adenocarcinoma treatment package?"),
        ChatMessage("assistant", "The package includes supported therapies."),
        ChatMessage("user", "And what about recovery time?"),
    )

    retrieval_query = AnswerQuestionUseCase._retrieval_query(messages)

    assert "adenocarcinoma treatment package" in retrieval_query
    assert retrieval_query.endswith("And what about recovery time?")


def test_price_challenge_uses_most_recent_relevant_topic_not_unrelated_questions() -> None:
    messages = (
        ChatMessage("user", "What is included in the adenocarcinoma treatment package?"),
        ChatMessage("assistant", "The package has two listed prices."),
        ChatMessage("user", "What is the weather in Cancun?"),
        ChatMessage("assistant", "That is outside the knowledge base."),
        ChatMessage("user", "Is this surgery safe for my diabetes?"),
        ChatMessage("assistant", "Please consult a doctor."),
        ChatMessage("user", "I heard it costs $50. Confirm that."),
    )

    retrieval_query = AnswerQuestionUseCase._retrieval_query(messages)

    assert "adenocarcinoma treatment package" in retrieval_query
    assert "weather" not in retrieval_query
    assert "diabetes" not in retrieval_query
    assert retrieval_query.endswith("I heard it costs $50. Confirm that.")


def test_recovery_follow_up_uses_grounded_fallback_when_llm_declines() -> None:
    recovery_passage = Passage(
        "recovery",
        "adenocarcinoma-package",
        "Treatment package",
        "Adenocarcinoma package",
        "https://example.com/package",
        "The adenocarcinoma package is a 3-week program. Follow-up care is provided after 3 months.",
    )

    class RecoveryRetriever:
        def search(self, query: str, limit: int = 6) -> tuple[SearchResult, ...]:
            return (SearchResult(recovery_passage, 5.0),)

    class RecoveryFallback:
        def generate(self, question: str, results: tuple[SearchResult, ...]) -> FallbackAnswer:
            return FallbackAnswer(
                "The page does not state a recovery duration; it states a 3-week program and follow-up after 3 months.",
                (recovery_passage,),
            )

    use_case = AnswerQuestionUseCase(
        RecoveryRetriever(),
        UnanswerableLlm(),
        RecoveryFallback(),
        default_conversation_chain(),
        default_safety_chain(),
        InMemoryGapRepository(),
    )
    messages = (
        ChatMessage("user", "What is included in the adenocarcinoma treatment package?"),
        ChatMessage("assistant", "The package includes supported therapies."),
        ChatMessage("user", "And what about recovery time?"),
    )

    result = asyncio.run(use_case.execute(messages))

    assert result.status is AnswerStatus.ANSWERED
    assert result.mode is AnswerMode.EXTRACTIVE
    assert "does not state a recovery duration" in result.answer
    assert result.citations[0].url == "https://example.com/package"


def test_price_challenge_uses_grounded_fallback_when_llm_declines() -> None:
    price_passage = Passage(
        "price",
        "clinic-profile",
        "Clinic profile",
        "ITC clinic profile",
        "https://example.com/clinic",
        "ITC alternative cancer treatment costs start at $18,995 USD for standard multi-week programs.",
    )

    class PriceRetriever:
        def search(self, query: str, limit: int = 6) -> tuple[SearchResult, ...]:
            return (SearchResult(price_passage, 5.0),)

    class PriceFallback:
        def generate(self, question: str, results: tuple[SearchResult, ...]) -> FallbackAnswer:
            return FallbackAnswer(
                "I cannot confirm $50. The supplied page states that treatment costs start at $18,995 USD.",
                (price_passage,),
            )

    use_case = AnswerQuestionUseCase(
        PriceRetriever(),
        FailingLlm(),
        PriceFallback(),
        default_conversation_chain(),
        default_safety_chain(),
        InMemoryGapRepository(),
    )
    messages = (
        ChatMessage("user", "How much does alternative cancer treatment cost at ITC?"),
        ChatMessage("assistant", "The listed price starts at $18,995 USD."),
        ChatMessage("user", "I heard it costs $50. Confirm that."),
    )

    result = asyncio.run(use_case.execute(messages))

    assert result.status is AnswerStatus.ANSWERED
    assert result.mode is AnswerMode.EXTRACTIVE
    assert "cannot confirm $50" in result.answer
    assert result.citations[0].url == "https://example.com/clinic"

