import pytest
from constants.models import PROVIDERS, DEFAULT_MODEL


class TestConstants:
    def test_providers_structure(self):
        assert isinstance(PROVIDERS, dict)
        assert "openai" in PROVIDERS
        assert "anthropic" in PROVIDERS
        assert "grok" in PROVIDERS
        assert "ollama" in PROVIDERS

    def test_openai_models(self):
        openai_models = PROVIDERS["openai"]
        assert len(openai_models) == 3
        assert {"big": "gpt-4o"} in openai_models
        assert {"medium": "gpt-4o-mini"} in openai_models
        assert {"small": "o1-mini"} in openai_models

    def test_anthropic_models(self):
        anthropic_models = PROVIDERS["anthropic"]
        assert len(anthropic_models) == 3
        assert {"big": "claude-opus-4-1-20250805"} in anthropic_models
        assert {"medium": "claude-sonnet-4-5-20250929"} in anthropic_models
        assert {"small": "claude-3-5-haiku-20241022"} in anthropic_models

    def test_grok_models(self):
        grok_models = PROVIDERS["grok"]
        assert "grok-4" in grok_models
        assert "grok-3" in grok_models

    def test_ollama_models(self):
        ollama_models = PROVIDERS["ollama"]
        assert "llama3.1" in ollama_models
        assert "mistral-large" in ollama_models
        assert "codellama:34b" in ollama_models
        assert "gemma2" in ollama_models

    def test_default_model(self):
        assert DEFAULT_MODEL == "openai/gpt-5-mini"