from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(PROJECT_ROOT / ".env")

PROVIDER_PRESETS: dict[str, tuple[str, str]] = {
    "deepseek": ("https://api.deepseek.com", "deepseek-flash"),
    "openai": ("https://api.openai.com/v1", "gpt-4.1-mini"),
}


def resolve_llm_provider(
    provider: str,
    base_url_override: str = "",
    model_override: str = "",
) -> tuple[str, str, str]:
    normalized = provider.strip().casefold() or "deepseek"
    if normalized not in PROVIDER_PRESETS and (not base_url_override or not model_override):
        raise ValueError(f"Unknown LLM provider '{provider}'. Set both LLM_BASE_URL and LLM_MODEL.")
    default_base, default_model = PROVIDER_PRESETS.get(normalized, (base_url_override, model_override))
    return (
        normalized,
        (base_url_override or default_base).rstrip("/"),
        model_override or default_model,
    )


_LLM_PROVIDER, _LLM_BASE_URL, _LLM_MODEL = resolve_llm_provider(
    os.getenv("LLM_PROVIDER", "deepseek"),
    os.getenv("LLM_BASE_URL", "").strip(),
    os.getenv("LLM_MODEL", "").strip(),
)


@dataclass(frozen=True, slots=True)
class Settings:
    project_root: Path = PROJECT_ROOT
    knowledge_path: Path = PROJECT_ROOT / "data" / "knowledge.json"
    unanswered_path: Path = PROJECT_ROOT / "data" / "unanswered.jsonl"
    frontend_dist: Path = PROJECT_ROOT / "frontend" / "dist"
    llm_provider: str = _LLM_PROVIDER
    llm_api_key: str = os.getenv("DEEPSEEK_API_KEY", "").strip() or os.getenv("LLM_API_KEY", "").strip()
    llm_base_url: str = _LLM_BASE_URL
    llm_model: str = _LLM_MODEL
    refresh_token: str = os.getenv("REFRESH_TOKEN", "").strip()
    allowed_origins: tuple[str, ...] = tuple(
        value.strip() for value in os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",") if value.strip()
    )
    crawler_user_agent: str = "PlacidWayAssessmentBot/1.0 (+candidate-assessment; limited-to-seven-URLs)"


settings = Settings()
settings.knowledge_path.parent.mkdir(parents=True, exist_ok=True)

