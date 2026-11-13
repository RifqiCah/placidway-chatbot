import asyncio

from fastapi import APIRouter, Header, HTTPException

from backend.app.api.dependencies import ContainerDependency
from backend.app.api.schemas.refresh import RefreshResponse

router = APIRouter(prefix="/api", tags=["knowledge"])
_refresh_lock = asyncio.Lock()


@router.post("/refresh", response_model=RefreshResponse)
async def refresh(
    container: ContainerDependency,
    x_refresh_token: str | None = Header(default=None),
) -> RefreshResponse:
    configured_token = container.settings.refresh_token
    if not configured_token or x_refresh_token != configured_token:
        raise HTTPException(status_code=403, detail="A valid X-Refresh-Token is required")
    if _refresh_lock.locked():
        raise HTTPException(status_code=409, detail="A refresh is already running")
    async with _refresh_lock:
        result = await asyncio.to_thread(container.refresh_knowledge.execute)
    return RefreshResponse(
        status="refreshed",
        sources=result.sources,
        chunks=result.passages,
        refreshed_at=result.refreshed_at,
    )

