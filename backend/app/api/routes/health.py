from fastapi import APIRouter

from backend.app.api.dependencies import ContainerDependency

router = APIRouter(prefix="/api", tags=["health"])


@router.get("/health")
async def health(container: ContainerDependency) -> dict[str, object]:
    try:
        snapshot = container.knowledge_repository.load()
        return {
            "status": "ok",
            "sources": len(snapshot.sources),
            "chunks": len(snapshot.passages),
            "refreshed_at": snapshot.refreshed_at.isoformat(),
            "llm_configured": container.llm.is_configured,
            "llm_provider": container.settings.llm_provider,
            "llm_model": container.settings.llm_model,
        }
    except (FileNotFoundError, ValueError, KeyError):
        return {"status": "degraded", "reason": "knowledge_base_missing"}

