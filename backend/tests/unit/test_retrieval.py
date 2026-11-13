from backend.app.core.config import settings
from backend.app.infrastructure.persistence.json_knowledge_repository import JsonKnowledgeRepository
from backend.app.infrastructure.retrieval.bm25_retriever import Bm25Retriever


def make_retriever() -> Bm25Retriever:
    return Bm25Retriever(JsonKnowledgeRepository(settings.knowledge_path))


def test_cost_query_retrieves_exact_itc_price() -> None:
    results = make_retriever().search("How much does alternative cancer treatment cost at ITC?", limit=5)
    assert results
    assert "$18,995" in " ".join(result.passage.text for result in results)


def test_package_query_retrieves_correct_page() -> None:
    results = make_retriever().search("What is included in the adenocarcinoma package?", limit=3)
    assert results[0].passage.source_id == "adenocarcinoma-package"


def test_indonesian_query_expansion() -> None:
    results = make_retriever().search("Berapa harga pengobatan kanker di ITC?", limit=5)
    assert any("$18,995" in result.passage.text for result in results)

