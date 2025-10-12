# nenlib

A library for LLM provider configuration and logging utilities.

## Installation

```bash
pip install nenlib
# or
uv add nenlib
```

## Usage

```python
from nenlib import PROVIDERS, MLopsConfig, LiteLLMConfig

# Access provider configurations
print(PROVIDERS)

# Use MLOps configuration
config = MLopsConfig.get_provider_config("openai")

# Generate LiteLLM configuration
lite_config = LiteLLMConfig(providers=PROVIDERS)
model_list = lite_config.generate_model_list()
```