from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache

from backend.app.application.use_cases.answer_question import AnswerQuestionUseCase
from backend.app.application.use_cases.refresh_knowledge import RefreshKnowledgeUseCase
from backend.app.core.config import Settings, settings
from backend.app.domain.policies.conversation import default_conversation_chain
from backend.app.domain.policies.safety import default_safety_chain
from backend.app.infrastructure.ai.extractive_fallback import ExtractiveFallback
from backend.app.infrastructure.ai.openai_compatible import OpenAICompatibleLLM
from backend.app.infrastructure.ingestion.chunker import TextChunker
from backend.app.infrastructure.ingestion.html_extractor import HtmlContentExtractor
from backend.app.infrastructure.ingestion.placidway_crawler import PlacidWayCrawler
from backend.app.infrastructure.ingestion.placidway_sources import PLACIDWAY_SOURCES
from backend.app.infrastructure.persistence.json_knowledge_repository import JsonKnowledgeRepository
from backend.app.infrastructure.persistence.jsonl_gap_repository import JsonlGapRepository
from backend.app.infrastructure.retrieval.bm25_retriever import Bm25Retriever


@dataclass(slots=True)
class ApplicationContainer:
    settings: Settings
    knowledge_repository: JsonKnowledgeRepository
    answer_question: AnswerQuestionUseCase
    refresh_knowledge: RefreshKnowledgeUseCase
    llm: OpenAICompatibleLLM

    @classmethod
    def build(cls, configuration: Settings) -> ApplicationContainer:
        knowledge_repository = JsonKnowledgeRepository(configuration.knowledge_path)
        gap_repository = JsonlGapRepository(configuration.unanswered_path)
        retriever = Bm25Retriever(knowledge_repository)
        llm = OpenAICompatibleLLM(
            api_key=configuration.llm_api_key,
            base_url=configuration.llm_base_url,
            model=configuration.llm_model,
        )
        crawler = PlacidWayCrawler(
            sources=PLACIDWAY_SOURCES,
            extractor=HtmlContentExtractor(),
            chunker=TextChunker(),
            user_agent=configuration.crawler_user_agent,
        )
        return cls(
            settings=configuration,
            knowledge_repository=knowledge_repository,
            llm=llm,
            answer_question=AnswerQuestionUseCase(
                retriever=retriever,
                llm=llm,
                fallback=ExtractiveFallback(),
                conversation=default_conversation_chain(),
                safety=default_safety_chain(),
                gap_repository=gap_repository,
            ),
            refresh_knowledge=RefreshKnowledgeUseCase(crawler, knowledge_repository),
        )


@lru_cache(maxsize=1)
def get_container() -> ApplicationContainer:
    return ApplicationContainer.build(settings)

