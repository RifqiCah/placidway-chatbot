from __future__ import annotations

import math
from collections import Counter
from threading import RLock

from backend.app.application.ports.repositories import KnowledgeRepository
from backend.app.domain.entities.knowledge import Passage, SearchResult
from backend.app.domain.value_objects.query import query_tokens


class Bm25Retriever:
    def __init__(self, repository: KnowledgeRepository):
        self._repository = repository
        self._lock = RLock()
        self._revision = ""
        self._passages: tuple[Passage, ...] = ()
        self._tokens: tuple[list[str], ...] = ()
        self._term_frequencies: tuple[Counter[str], ...] = ()
        self._document_frequencies: Counter[str] = Counter()
        self._average_length = 1.0

    def search(self, query: str, limit: int = 6) -> tuple[SearchResult, ...]:
        self._ensure_index()
        tokens = query_tokens(query)
        if not tokens:
            return ()
        document_count = len(self._passages)
        k1, b = 1.5, 0.75
        scored: list[SearchResult] = []
        for passage, terms, passage_tokens in zip(
            self._passages,
            self._term_frequencies,
            self._tokens,
            strict=True,
        ):
            score = 0.0
            for token in tokens:
                frequency = terms.get(token, 0)
                if not frequency:
                    continue
                document_frequency = self._document_frequencies[token]
                inverse_frequency = math.log(
                    1 + (document_count - document_frequency + 0.5) / (document_frequency + 0.5)
                )
                denominator = frequency + k1 * (
                    1 - b + b * len(passage_tokens) / self._average_length
                )
                score += inverse_frequency * (frequency * (k1 + 1)) / denominator
            title_tokens = set(query_tokens(passage.title))
            score += 0.65 * sum(1 for token in tokens if token in title_tokens)
            if score > 0:
                scored.append(SearchResult(passage, score))
        return tuple(sorted(scored, key=lambda item: item.score, reverse=True)[:limit])

    def _ensure_index(self) -> None:
        revision = self._repository.revision()
        if revision == self._revision:
            return
        with self._lock:
            revision = self._repository.revision()
            if revision == self._revision:
                return
            snapshot = self._repository.load()
            passages = snapshot.passages
            tokens = tuple(
                query_tokens(f"{passage.title} {passage.page_type} {passage.text}")
                for passage in passages
            )
            term_frequencies = tuple(Counter(values) for values in tokens)
            document_frequencies: Counter[str] = Counter()
            for values in tokens:
                document_frequencies.update(set(values))
            self._passages = passages
            self._tokens = tokens
            self._term_frequencies = term_frequencies
            self._document_frequencies = document_frequencies
            self._average_length = sum(map(len, tokens)) / max(len(tokens), 1)
            self._revision = revision

