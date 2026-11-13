from backend.app.domain.entities.knowledge import Passage, SearchResult
from backend.app.infrastructure.ai.extractive_fallback import ExtractiveFallback


def test_recovery_question_returns_bounded_unknown_with_relevant_citation() -> None:
    passage = Passage(
        "package",
        "adenocarcinoma-package",
        "Treatment package",
        "Adenocarcinoma package",
        "https://example.com/package",
        "The adenocarcinoma package includes laboratory work, imaging, and integrative therapies.",
    )

    result = ExtractiveFallback().generate(
        "And what about recovery time?",
        (SearchResult(passage, 5.0),),
    )

    assert result.is_answerable
    assert "does not state a specific recovery duration" in result.answer
    assert result.used_passages == (passage,)
