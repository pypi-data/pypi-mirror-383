import os
from dotenv import load_dotenv, find_dotenv



class MLopsConfig:
    """
    MLopsConfig provides configuration details for supported LLM providers.

    Usage:
        - Get all providers: MLopsConfig.PROVIDERS
        - Get a specific provider config: MLopsConfig.get_provider_config("openai")

    Environment variables should be set for API keys and optionally API bases:
        OPENAI_API_KEY, OPENAI_API_BASE
        ANTHROPIC_API_KEY, ANTHROPIC_API_BASE
        GROK_API_KEY, GROK_API_BASE
        OLLAMA_API_BASE, OLLAMA_MODELS
    """
    PROVIDERS = {
        "openai": {
            "api_base": os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1"),
            "api_key": os.getenv("OPENAI_API_KEY"),
            "models_small": ["gpt-5-nano", "gpt-5-mini", "gpt-4o-mini"],
            "models_big": ["gpt-5", "gpt-4o"]
        },
        "anthropic": {
            "api_base": os.getenv("ANTHROPIC_API_BASE", "https://api.anthropic.com/v1"),
            "api_key": os.getenv("ANTHROPIC_API_KEY"),
            "models": [
                "claude-3-opus-20240229",
                "claude-3-sonnet-20240229",
                "claude-3-haiku-20240307"
            ]
        },
        "grok": {
            "api_base": os.getenv("GROK_API_BASE", "https://api.grok.x.com/v1"),
            "api_key": os.getenv("GROK_API_KEY"),
            "models": ["grok-1", "grok-1.5"]
        },
        "ollama": {
            "api_base": os.getenv("OLLAMA_API_BASE", "http://localhost:11434/api"),
            "api_key": None,
            "models": [
                model.strip()
                for model in os.getenv("OLLAMA_MODELS", "llama2,phi,starcoder").split(",")
                if model.strip()
            ]
        },
    }

    @classmethod
    def get_provider_config(cls, provider: str):
        """
        Returns the configuration dictionary for a given provider name, or None if not found.

        Args:
            provider (str): The provider name, e.g. "openai", "anthropic", "grok", "ollama".

        Returns:
            dict or None: The configuration for the provider, or None if not defined.
        """
        return cls.PROVIDERS.get(provider.lower())
