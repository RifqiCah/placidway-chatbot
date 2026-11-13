from __future__ import annotations

import re
from dataclasses import dataclass

from backend.app.application.ports.answer_generator import FallbackAnswerPort
from backend.app.application.ports.llm import LLMPort
from backend.app.application.ports.repositories import GapRepository
from backend.app.application.ports.retriever import RetrieverPort
from backend.app.domain.entities.chat import AnswerMode, AnswerStatus, ChatAnswer, ChatMessage, Citation
from backend.app.domain.entities.knowledge import Passage, SearchResult
from backend.app.domain.policies.conversation import ConversationPolicyChain
from backend.app.domain.policies.safety import SafetyPolicyChain
from backend.app.domain.value_objects.money import MONEY_PATTERN
from backend.app.domain.value_objects.query import query_tokens

UNKNOWN_ANSWER = (
    "I couldn't find that information in the supplied PlacidWay pages. "
    "Please contact PlacidWay or request a free quote for a confirmed answer."
)
MEDICAL_DISCLAIMER = "This is general website information, not medical advice. Please consult a qualified doctor."


@dataclass(slots=True)
class AnswerQuestionUseCase:
    retriever: RetrieverPort
    llm: LLMPort
    fallback: FallbackAnswerPort
    conversation: ConversationPolicyChain
    safety: SafetyPolicyChain
    gap_repository: GapRepository

    async def execute(self, messages: tuple[ChatMessage, ...]) -> ChatAnswer:
        question = messages[-1].content
        if conversation_decision := self.conversation.evaluate(question):
            return ChatAnswer(conversation_decision.answer, AnswerStatus.ANSWERED, AnswerMode.EXTRACTIVE)
        if safety_decision := self.safety.evaluate(question):
            return ChatAnswer(safety_decision.answer, safety_decision.status, AnswerMode.EXTRACTIVE)

        retrieval_query = self._retrieval_query(messages)
        results = self.retriever.search(retrieval_query, limit=6)
        if not self._has_sufficient_evidence(results, retrieval_query):
            return self._unknown(question, "low_retrieval_score")

        evidence = tuple(result.passage for result in results)
        disclaimer = MEDICAL_DISCLAIMER if self._is_medical_topic(question) else None
        if self._is_price_challenge(question):
            price_guardrail_answer = self._fallback_answer(question, results, disclaimer)
            if price_guardrail_answer is not None:
                return price_guardrail_answer

        history = "\n".join(f"{message.role}: {message.content}" for message in messages[-6:-1])
        generated = await self.llm.generate(question, history, evidence)

        if generated is not None:
            if not generated.is_answerable:
                if self._should_try_fallback_after_llm_refusal(question):
                    fallback_answer = self._fallback_answer(question, results, disclaimer)
                    if fallback_answer is not None:
                        return fallback_answer
                return self._unknown(question, "llm_marked_unanswerable", AnswerMode.LLM)
            cited = tuple(evidence[index - 1] for index in generated.source_indices)
            return ChatAnswer(
                answer=generated.answer,
                citations=self._citations(cited),
                status=AnswerStatus.ANSWERED,
                mode=AnswerMode.LLM,
                disclaimer=disclaimer,
            )

        fallback_answer = self._fallback_answer(question, results, disclaimer)
        if fallback_answer is not None:
            return fallback_answer
        return self._unknown(question, "extractive_answer_not_found")

    def _fallback_answer(
        self,
        question: str,
        results: tuple[SearchResult, ...],
        disclaimer: str | None,
    ) -> ChatAnswer | None:
        fallback = self.fallback.generate(question, results)
        if not fallback.is_answerable or not fallback.used_passages:
            return None
        return ChatAnswer(
            answer=fallback.answer,
            citations=self._citations(fallback.used_passages),
            status=AnswerStatus.ANSWERED,
            mode=AnswerMode.EXTRACTIVE,
            disclaimer=disclaimer,
        )

    @staticmethod
    def _is_follow_up(text: str) -> bool:
        normalized = " ".join(text.casefold().split())
        prefixes = (
            "what about",
            "and what about",
            "and how about",
            "how about",
            "recovery time",
            "what is its",
            "what's its",
            "does it",
            "is it",
            "can it",
            "bagaimana dengan",
            "dan bagaimana",
            "berapa lama pemulihan",
            "kalau",
            "lalu",
        )
        if normalized.startswith(prefixes):
            return True
        return bool(re.search(r"\b(its|that|those|same treatment|same package|this package)\b", normalized))

    @classmethod
    def _retrieval_query(cls, messages: tuple[ChatMessage, ...]) -> str:
        latest = messages[-1].content
        if cls._is_price_challenge(latest) and (price_context := cls._most_recent_price_context(messages[:-1])):
            return f"{price_context} {latest}"
        if not cls._is_follow_up(latest):
            return latest
        previous = [message.content for message in messages[:-1] if message.role == "user"][-2:]
        return " ".join([*previous, latest])

    @staticmethod
    def _is_price_challenge(text: str) -> bool:
        lowered = text.casefold()
        challenge_terms = ("confirm", "heard", "really", "correct", "is that", "katanya", "benar")
        return bool(MONEY_PATTERN.search(text)) and any(term in lowered for term in challenge_terms)

    @staticmethod
    def _most_recent_price_context(messages: tuple[ChatMessage, ...]) -> str | None:
        topic_terms = (
            "cost",
            "price",
            "treatment",
            "therapy",
            "package",
            "clinic",
            "itc",
            "cancer",
            "medicine",
            "biaya",
            "harga",
            "pengobatan",
            "paket",
        )
        for message in reversed(messages):
            if message.role != "user":
                continue
            lowered = message.content.casefold()
            if any(term in lowered for term in topic_terms):
                return message.content
        return None

    @classmethod
    def _should_try_fallback_after_llm_refusal(cls, question: str) -> bool:
        lowered = question.casefold()
        return "recovery" in lowered or "pemulihan" in lowered or cls._is_price_challenge(question)

    @staticmethod
    def _has_sufficient_evidence(results: tuple[SearchResult, ...], query: str) -> bool:
        if not results or results[0].score < 1.25:
            return False
        generic = {"cost", "price", "pricing", "treatment", "therapy", "package", "clinic", "information", "confirm"}
        specific_terms = set(query_tokens(query)) - generic
        if not specific_terms:
            return True
        evidence_terms = set(query_tokens(" ".join(result.passage.text for result in results[:3])))
        return bool(specific_terms.intersection(evidence_terms))

    @staticmethod
    def _citations(passages: tuple[Passage, ...]) -> tuple[Citation, ...]:
        seen: set[str] = set()
        citations: list[Citation] = []
        for passage in passages:
            if passage.url not in seen:
                seen.add(passage.url)
                citations.append(Citation(passage.title, passage.url))
        return tuple(citations)

    @staticmethod
    def _is_medical_topic(question: str) -> bool:
        return any(
            term in question.casefold()
            for term in ("cancer", "treatment", "therapy", "procedure", "surgery", "kanker", "pengobatan")
        )

    def _unknown(
        self,
        question: str,
        reason: str,
        mode: AnswerMode = AnswerMode.EXTRACTIVE,
    ) -> ChatAnswer:
        self.gap_repository.append(question, reason)
        return ChatAnswer(UNKNOWN_ANSWER, AnswerStatus.UNKNOWN, mode)

