from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from backend.app.api.routes import chat_router, health_router, refresh_router
from backend.app.core.config import settings


def create_app() -> FastAPI:
    application = FastAPI(
        title="PlacidWay Grounded Knowledge Chatbot",
        description="Answers only from seven approved PlacidWay pages.",
        version="2.0.0",
    )
    application.add_middleware(
        CORSMiddleware,
        allow_origins=list(settings.allowed_origins),
        allow_credentials=False,
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type", "X-Refresh-Token"],
    )
    application.include_router(chat_router)
    application.include_router(health_router)
    application.include_router(refresh_router)

    if settings.frontend_dist.exists():
        assets = settings.frontend_dist / "assets"
        if assets.exists():
            application.mount("/assets", StaticFiles(directory=assets), name="frontend-assets")

        @application.get("/{path:path}", include_in_schema=False)
        async def frontend(path: str) -> FileResponse:
            requested = settings.frontend_dist / path
            if path and requested.is_file() and settings.frontend_dist in requested.resolve().parents:
                return FileResponse(requested)
            return FileResponse(settings.frontend_dist / "index.html")
    else:
        @application.get("/", include_in_schema=False)
        async def backend_root() -> JSONResponse:
            return JSONResponse(
                {"service": "PlacidWay chatbot API", "docs": "/docs", "frontend": "run npm --prefix frontend run dev"}
            )
    return application


app = create_app()

