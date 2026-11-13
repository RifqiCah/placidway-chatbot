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


def test_false_price_is_rejected_and_replaced_with_supported_price() -> None:
    passage = Passage(
        "price",
        "clinic-profile",
        "Clinic profile",
        "ITC clinic profile",
        "https://example.com/clinic",
        "Treatment costs start at $18,995 USD for standard multi-week programs.",
    )

    result = ExtractiveFallback().generate(
        "I heard it costs $50. Confirm that.",
        (SearchResult(passage, 5.0),),
    )

    assert result.is_answerable
    assert result.answer.startswith("I cannot confirm the price stated in the question.")
    assert "$18,995 USD" in result.answer
    assert result.used_passages == (passage,)


def test_false_package_price_lists_each_supported_program_once() -> None:
    passage = Passage(
        "package-price",
        "adenocarcinoma-package",
        "Treatment package",
        "Adenocarcinoma package",
        "https://example.com/package",
        "\n".join(
            (
                "Out-Patient Program 3 Weeks $18,995",
                "In-Patient Program 3 Weeks $30,000",
                "Included in the Out-Patient Program ($18,995 USD)",
                "Included in the In-Patient Program ($30,000 USD)",
            )
        ),
    )

    result = ExtractiveFallback().generate(
        "I heard it costs $50. Confirm that.",
        (SearchResult(passage, 5.0),),
    )

    assert result.answer == (
        "I cannot confirm the price stated in the question. The supplied package page lists "
        "the Out-Patient Program at $18,995 USD and the In-Patient Program at $30,000 USD."
    )
    assert result.used_passages == (passage,)
