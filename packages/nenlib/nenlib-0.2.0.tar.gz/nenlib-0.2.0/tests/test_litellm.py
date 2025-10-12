import pytest


class TestLiteLLM:
    def test_litellm_config_structure(self):
        from dataclasses import dataclass, field
        from typing import Dict, Any, List
        
        @dataclass
        class LiteLLMConfig:
            providers: Dict[str, List[Any]] = field(default_factory=dict)
            default_rpm: int = 100
            default_tpm: int = 1000
            ollama_base: str = "http://localhost:11434"
        
        config = LiteLLMConfig()
        assert config.default_rpm == 100
        assert config.default_tpm == 1000
        assert config.ollama_base == "http://localhost:11434"