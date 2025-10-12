import pytest
from unittest.mock import patch, Mock
import os
from llm_providers import MLopsConfig


class TestMLopsConfig:
    def test_providers_structure(self):
        assert hasattr(MLopsConfig, 'PROVIDERS')
        assert isinstance(MLopsConfig.PROVIDERS, dict)
        assert "openai" in MLopsConfig.PROVIDERS
        assert "anthropic" in MLopsConfig.PROVIDERS
        assert "grok" in MLopsConfig.PROVIDERS
        assert "ollama" in MLopsConfig.PROVIDERS

    def test_get_provider_config_openai(self):
        config = MLopsConfig.get_provider_config("openai")
        
        assert config is not None
        assert "api_base" in config
        assert "api_key" in config
        assert "models_small" in config
        assert "models_big" in config
        assert config["api_base"] == "https://api.openai.com/v1"

    def test_get_provider_config_anthropic(self):
        config = MLopsConfig.get_provider_config("anthropic")
        
        assert config is not None
        assert "api_base" in config
        assert "api_key" in config
        assert "models" in config
        assert "claude-3-opus-20240229" in config["models"]

    def test_get_provider_config_grok(self):
        config = MLopsConfig.get_provider_config("grok")
        
        assert config is not None
        assert "api_base" in config
        assert "api_key" in config
        assert "models" in config
        assert "grok-1" in config["models"]
        assert "grok-1.5" in config["models"]

    def test_get_provider_config_ollama(self):
        config = MLopsConfig.get_provider_config("ollama")
        
        assert config is not None
        assert "api_base" in config
        assert config["api_key"] is None
        assert "models" in config

    def test_get_provider_config_case_insensitive(self):
        config_lower = MLopsConfig.get_provider_config("openai")
        config_upper = MLopsConfig.get_provider_config("OPENAI")
        
        assert config_lower == config_upper

    def test_get_provider_config_invalid(self):
        config = MLopsConfig.get_provider_config("invalid_provider")
        
        assert config is None

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test_key", "OPENAI_API_BASE": "https://test.com"})
    def test_provider_config_with_env_vars(self):
        # Reload to pick up new env vars
        from importlib import reload
        import llm_providers
        reload(llm_providers)
        
        config = llm_providers.MLopsConfig.get_provider_config("openai")
        
        assert config["api_key"] == "test_key"
        assert config["api_base"] == "https://test.com"

    def test_ollama_models_parsing(self):
        with patch.dict(os.environ, {"OLLAMA_MODELS": "llama2, phi , starcoder "}):
            from importlib import reload
            import llm_providers
            reload(llm_providers)
            
            config = llm_providers.MLopsConfig.get_provider_config("ollama")
            expected_models = ["llama2", "phi", "starcoder"]
            
            assert config["models"] == expected_models

    def test_default_ollama_models(self):
        with patch.dict(os.environ, {}, clear=True):
            from importlib import reload
            import llm_providers
            reload(llm_providers)
            
            config = llm_providers.MLopsConfig.get_provider_config("ollama")
            default_models = ["llama2", "phi", "starcoder"]
            
            assert config["models"] == default_models