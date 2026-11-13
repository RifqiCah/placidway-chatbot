from backend.app.domain.entities.chat import AnswerStatus
from backend.app.domain.policies.safety import default_safety_chain
from backend.app.domain.value_objects.money import has_unsupported_money


def test_medical_advice_is_refused() -> None:
    decision = default_safety_chain().evaluate("Is this surgery safe for my diabetes?")
    assert decision is not None
    assert decision.status is AnswerStatus.MEDICAL_SAFETY


def test_booking_action_is_refused() -> None:
    decision = default_safety_chain().evaluate("Can you book me an appointment for tomorrow?")
    assert decision is not None
    assert decision.status is AnswerStatus.ACTION_UNSUPPORTED


def test_out_of_scope_question_is_refused() -> None:
    decision = default_safety_chain().evaluate("What is the weather in Cancun?")
    assert decision is not None
    assert decision.status is AnswerStatus.OUT_OF_SCOPE


def test_price_validator_rejects_new_amount() -> None:
    evidence = "Treatment costs start at $18,995 for a three-week program."
    assert has_unsupported_money("It costs $50.", evidence)
    assert not has_unsupported_money("It starts at $18,995.", evidence)

