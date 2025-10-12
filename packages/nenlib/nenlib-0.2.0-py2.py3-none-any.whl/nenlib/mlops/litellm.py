import yaml
from dataclasses import dataclass, field
from typing import Dict, Any, List

@dataclass
class LiteLLMConfig:
    """
    Configuration class for LiteLLM integration, leveraging PROVIDERS dict.
    Generates model_list for proxy config or SDK Router.
    """
    providers: Dict[str, List[Any]] = field(default_factory=dict)  # e.g., the existing PROVIDERS
    default_rpm: int = 100  # Default requests per minute for load balancing
    default_tpm: int = 1000  # Default tokens per minute
    ollama_base: str = "http://localhost:11434"  # Default Ollama endpoint

    def _get_prefix(self, provider: str) -> str:
        """Get LiteLLM model prefix for provider."""
        prefixes = {
            "openai": "openai",
            "anthropic": "anthropic",
            "grok": "xai",
            "ollama": "ollama"
        }
        return prefixes.get(provider, "")

    def _get_env_key(self, provider: str) -> str:
        """Get environment variable for API key."""
        env_vars = {
            "openai": "OPENAI_API_KEY",
            "anthropic": "ANTHROPIC_API_KEY",
            "grok": "XAI_API_KEY",
            "ollama": "none"  # No key for local Ollama
        }
        return env_vars.get(provider, "API_KEY")

    def generate_model_list(self) -> List[Dict[str, Any]]:
        """
        Generate LiteLLM-compatible model_list from PROVIDERS.
        Each entry: {'model_name': str, 'litellm_params': dict}.
        """
        model_list = []
        for provider, models in self.providers.items():
            prefix = self._get_prefix(provider)
            env_key = self._get_env_key(provider)
            for model_info in models:
                if isinstance(model_info, dict):  # e.g., {"big": "gpt-4o"} for OpenAI/Anthropic
                    size, model = list(model_info.items())[0]
                    model_name = f"{provider}-{size}-{model}"
                else:  # List str, e.g., for Grok/Ollama
                    model_name = f"{provider}-{model_info}"
                
                litellm_params = {
                    "model": f"{prefix}/{model}",
                    "api_key": f"os.environ/{env_key}",
                    "rpm": self.default_rpm,
                    "tpm": self.default_tpm
                }
                
                # Provider-specific overrides
                if provider == "ollama":
                    litellm_params.update({
                        "api_base": self.ollama_base,
                        "api_key": "none"
                    })
                elif provider == "grok":
                    litellm_params["api_base"] = "https://api.x.ai/v1"
                elif provider == "anthropic":
                    litellm_params["api_key"] = f"os.environ/{env_key}"  # Already set
                
                model_list.append({
                    "model_name": model_name,
                    "litellm_params": litellm_params,
                    "model_info": {"provider": provider, "tier": size if isinstance(model_info, dict) else "default"}  # Optional metadata
                })
        
        return model_list

    def to_yaml(self, router_strategy: str = "simple-shuffle") -> str:
        """
        Export full config.yaml as string, including router_settings.
        """
        config = {
            "model_list": self.generate_model_list(),
            "router_settings": {
                "routing_strategy": router_strategy  # e.g., "least-busy" for LLMOps resilience
            },
            "litellm_settings": {
                "num_retries": 3  # Fallback retries
            }
        }
        return yaml.dump(config, default_flow_style=False, sort_keys=False)


