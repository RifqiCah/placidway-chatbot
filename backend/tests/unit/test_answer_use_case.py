import asyncio

from backend.app.application.dto.ai import GeneratedAnswer
from backend.app.application.dto.fallback import FallbackAnswer
from backend.app.application.use_cases.answer_question import AnswerQuestionUseCase
from backend.app.domain.entities.chat import AnswerStatus, ChatMessage
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

