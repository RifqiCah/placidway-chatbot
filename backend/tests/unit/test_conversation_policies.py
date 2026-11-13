import pytest

from backend.app.domain.policies.conversation import default_conversation_chain


@pytest.mark.parametrize("message", ["hello", "Halo!", "hi there", "good morning"])
def test_greetings_receive_an_english_scoped_response(message: str) -> None:
    decision = default_conversation_chain().evaluate(message)
    assert decision is not None
    assert decision.answer.startswith("Hello!")
    assert "PlacidWay" in decision.answer


@pytest.mark.parametrize("message", ["thank you", "terima kasih"])
def test_thanks_receive_an_english_response(message: str) -> None:
    decision = default_conversation_chain().evaluate(message)
    assert decision is not None
    assert decision.answer.startswith("You're welcome!")


def test_factual_question_is_not_swallowed_by_conversation_policy() -> None:
    assert default_conversation_chain().evaluate("Hello, how much does treatment cost?") is None

