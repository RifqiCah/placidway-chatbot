from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)


def test_greeting_is_answered_in_english_without_citations() -> None:
    response = client.post(
        "/api/chat",
        json={"messages": [{"role": "user", "content": "halo"}]},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["answer"].startswith("Hello!")
    assert body["status"] == "answered"
    assert body["citations"] == []


def test_health_reports_seven_sources() -> None:
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["sources"] == 7
    assert response.json()["llm_provider"] == "deepseek"
    assert response.json()["llm_model"] == "deepseek-flash"


def test_cost_answer_has_exact_price_and_source() -> None:
    response = client.post(
        "/api/chat",
        json={"messages": [{"role": "user", "content": "How much does alternative cancer treatment cost at ITC?"}]},
    )
    assert response.status_code == 200
    body = response.json()
    assert "$18,995" in body["answer"]
    assert body["citations"]


def test_unknown_question_uses_honest_fallback() -> None:
    response = client.post(
        "/api/chat",
        json={"messages": [{"role": "user", "content": "Do you offer pediatric cardiac transplants?"}]},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "unknown"


def test_refresh_requires_token() -> None:
    response = client.post("/api/refresh")
    assert response.status_code == 403


def test_wrong_price_is_not_confirmed() -> None:
    response = client.post(
        "/api/chat",
        json={"messages": [{"role": "user", "content": "I heard ITC treatment costs $50. Confirm that."}]},
    )
    assert response.status_code == 200
    assert "$50" not in response.json()["answer"]

