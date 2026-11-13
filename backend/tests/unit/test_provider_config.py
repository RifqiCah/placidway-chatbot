import pytest

from backend.app.core.config import resolve_llm_provider


def test_deepseek_preset_uses_current_official_endpoint_and_flash_model() -> None:
    provider, base_url, model = resolve_llm_provider("deepseek")
    assert provider == "deepseek"
    assert base_url == "https://api.deepseek.com"
    assert model == "deepseek-flash"


def test_provider_values_can_be_overridden() -> None:
    provider, base_url, model = resolve_llm_provider("custom", "https://llm.example.com/v1/", "custom-model")
    assert (provider, base_url, model) == ("custom", "https://llm.example.com/v1", "custom-model")


def test_unknown_provider_requires_explicit_endpoint_and_model() -> None:
    with pytest.raises(ValueError):
        resolve_llm_provider("custom")

