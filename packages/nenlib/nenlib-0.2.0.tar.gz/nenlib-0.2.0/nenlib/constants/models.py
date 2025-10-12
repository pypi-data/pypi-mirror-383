PROVIDERS = {
    "openai": [
        {"big": "gpt-4o"},
        {"medium": "gpt-4o-mini"},
        {"small": "o1-mini"}
    ],
    "anthropic": [
        {"big": "claude-opus-4-1-20250805"},
        {"medium": "claude-sonnet-4-5-20250929"},
        {"small": "claude-3-5-haiku-20241022"}
    ],
    "grok": [
        "grok-4",
        "grok-3"
    ],
    "ollama": [
        "llama3.1",
        "mistral-large",
        "codellama:34b",
        "gemma2"
    ]
}

DEFAULT_MODEL = "openai/gpt-5-mini"