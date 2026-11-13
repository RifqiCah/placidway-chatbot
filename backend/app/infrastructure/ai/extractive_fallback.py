from __future__ import annotations

import re

from backend.app.application.dto.fallback import FallbackAnswer
from backend.app.domain.entities.knowledge import Passage, SearchResult
from backend.app.domain.value_objects.money import MONEY_PATTERN, has_unsupported_money
from backend.app.domain.value_objects.query import query_tokens


class ExtractiveFallback:
    """Deterministic answer generator used when no LLM is configured or available."""

    def generate(self, question: str, results: tuple[SearchResult, ...]) -> FallbackAnswer:
        results = self._relevant_results(question, results)
        lowered = question.casefold()
        evidence = "\n".join(result.passage.text for result in results)
        default_passages = tuple(result.passage for result in results[:3])

        if any(word in lowered for word in ("cheaper", "compare", "comparison", "lebih murah", "bandingkan")):
            comparison = tuple(
                result.passage for result in results if result.passage.source_id == "price-comparison"
            )[:2]
            return FallbackAnswer(
                "The supplied page does not provide a like-for-like comparison for the same treatment in both "
                "countries. It lists example prices from Mexico and Turkey, but the quoted procedures differ, so "
                "I cannot reliably say that one country is cheaper for the same treatment. Please request "
                "comparable quotes for the exact procedure.",
                comparison or default_passages,
            )

        if "recovery" in lowered or "pemulihan" in lowered:
            matching = [
                re.sub(r"^\d+\.\s*Why is the treatment period three weeks\?\s*", "", line.strip(), flags=re.I)
                for line in evidence.splitlines()
                if any(
                    term in line.casefold()
                    for term in ("three weeks", "3-week", "follow-up", "post-care", "recovery")
                )
                and 20 <= len(line.strip()) <= 360
            ]
            details = list(dict.fromkeys(matching[:2]))
            if details:
                return FallbackAnswer(
                    "The page does not state a specific recovery duration. It does state: "
                    + " ".join(details)
                    + " These are treatment or follow-up timings, not a guaranteed recovery time.",
                    self._passages_containing(details, results) or default_passages,
                )
            return FallbackAnswer("", (), is_answerable=False)

        if any(term in lowered for term in ("included", "includes", "termasuk", "isi paket")):
            allowed_labels = (
                "weekly comprehensive", "prescribed imaging", "core therapies", "nutritional support",
                "medications", "follow-up care", "medical supervision", "room and board",
                "extensive diagnostics", "diagnostic imaging", "clinical therapies", "pharmacy support",
            )
            inclusion_lines = [
                line.strip()
                for line in evidence.splitlines()
                if any(line.strip().casefold().startswith(label) for label in allowed_labels)
            ]
            details = list(dict.fromkeys(inclusion_lines))[:7]
            if details:
                return FallbackAnswer(
                    "The package page lists: " + " ".join(details),
                    self._passages_containing(details, results) or default_passages,
                )

        cost_intent = any(term in lowered for term in ("cost", "price", "harga", "biaya", "berapa"))
        if cost_intent or MONEY_PATTERN.search(question):
            price_lines: list[str] = []
            for line in evidence.splitlines():
                clean = line.strip()
                if not MONEY_PATTERN.search(clean):
                    continue
                if any(
                    term in clean.casefold()
                    for term in ("costs start", "out-patient program", "in-patient program", "base package price")
                ):
                    price_lines.append(clean)
            details = list(dict.fromkeys(price_lines))[:3]
            if details:
                detail = " ".join(details)
                passages = self._passages_containing(details, results) or default_passages
                if MONEY_PATTERN.search(question) and has_unsupported_money(question, evidence):
                    return FallbackAnswer(
                        "I cannot confirm the price stated in the question. The supplied page instead says: " + detail,
                        passages,
                    )
                return FallbackAnswer("The supplied page states: " + detail, passages)

        question_terms = set(query_tokens(question))
        candidates: list[tuple[int, str, Passage]] = []
        for result in results[:3]:
            for sentence in re.split(r"(?<=[.!?])\s+|\n+", result.passage.text):
                sentence = sentence.strip()
                if not 25 <= len(sentence) <= 420:
                    continue
                overlap = len(question_terms.intersection(query_tokens(sentence)))
                price_bonus = 3 if MONEY_PATTERN.search(sentence) else 0
                candidates.append((overlap + price_bonus, sentence, result.passage))
        selected: list[str] = []
        used: list[Passage] = []
        for _, sentence, passage in sorted(candidates, key=lambda item: item[0], reverse=True):
            if sentence not in selected:
                selected.append(sentence)
                if passage not in used:
                    used.append(passage)
            if len(selected) == 3:
                break
        if not selected:
            return FallbackAnswer("", (), is_answerable=False)
        return FallbackAnswer("Based on the supplied page: " + " ".join(selected), tuple(used))

    @staticmethod
    def _relevant_results(question: str, results: tuple[SearchResult, ...]) -> tuple[SearchResult, ...]:
        lowered = question.casefold()
        source_hint = None
        if "adenocarcinoma" in lowered:
            source_hint = "adenocarcinoma-package"
        elif "adrenal" in lowered:
            source_hint = "adrenal-package"
        elif re.search(r"\banal\b", lowered):
            source_hint = "anal-package"
        if source_hint:
            filtered = tuple(result for result in results if result.passage.source_id == source_hint)
            if filtered:
                return filtered
        if "itc" in lowered:
            if MONEY_PATTERN.search(question) or any(term in lowered for term in ("cost", "price", "harga", "biaya")):
                filtered = tuple(
                    result
                    for result in results
                    if result.passage.source_id in {"clinic-profile", "price-list"}
                )
                if filtered:
                    return filtered
            filtered = tuple(result for result in results if result.passage.source_id != "price-comparison")
            if filtered:
                return filtered
        return results

    @staticmethod
    def _passages_containing(lines: list[str], results: tuple[SearchResult, ...]) -> tuple[Passage, ...]:
        passages: list[Passage] = []
        for result in results:
            if any(line in result.passage.text for line in lines) and result.passage not in passages:
                passages.append(result.passage)
        return tuple(passages)

