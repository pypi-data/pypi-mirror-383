# nenlib

Utilities and helpers for LLMOps with LiteLLM integration.

## Installation

```bash
pip install nenlib
# or
uv add nenlib
```

## Quick Start

```python
import nenlib

# Setup logging
logger = nenlib.setup_logger()
logger.info("Starting LLMOps workflow")

# Access provider configurations
print(nenlib.PROVIDERS)
print(nenlib.DEFAULT_MODEL)
```

## Core Components

### 1. Provider Configurations

Access pre-configured LLM providers:

```python
from nenlib.constants import PROVIDERS, DEFAULT_MODEL

# Available providers: openai, anthropic, grok, ollama
openai_config = PROVIDERS["openai"]
# [{"big": "gpt-4o"}, {"medium": "gpt-4o-mini"}, {"small": "o1-mini"}]
```

### 2. MLOps Integration

```python
from nenlib.mlops import MLopsConfig, LiteLLMConfig

# Get provider configuration
config = MLopsConfig.get_provider_config("openai")
print(config["api_base"])  # https://api.openai.com/v1

# Generate LiteLLM configuration
lite_config = LiteLLMConfig(providers=PROVIDERS)
model_list = lite_config.generate_model_list()
yaml_config = lite_config.to_yaml()
```

### 3. Logging

```python
from nenlib.logging import setup_logger

# Creates logs/nenlib-YYYY-MM-DD.log
logger = setup_logger()
logger.info("Process started")
logger.error("Something went wrong")
```

### 4. Helper Utilities

```python
from nenlib.helpers import Helpers

# Load environment variables
Helpers.dotenv_load()

# Get environment variable with fallback
api_key = Helpers.get_env_var("OPENAI_API_KEY", "default_key")

# Ensure log directory exists
Helpers.ensure_log_dir_exists("logs")
```

## Configuration

### Environment Variables

Set these environment variables for provider access:

```bash
# OpenAI
export OPENAI_API_KEY="your_openai_key"
export OPENAI_API_BASE="https://api.openai.com/v1"  # optional

# Anthropic
export ANTHROPIC_API_KEY="your_anthropic_key"

# Grok/X.AI
export XAI_API_KEY="your_grok_key"

# Ollama (local)
export OLLAMA_API_BASE="http://localhost:11434"  # optional
export OLLAMA_MODELS="llama3.1,mistral-large"    # optional
```

### LiteLLM Proxy Setup

Use the included `config.yaml` for LiteLLM proxy:

```bash
# Start LiteLLM proxy
litellm --config config.yaml

# Or generate custom config
python -c "
from nenlib.mlops import LiteLLMConfig
from nenlib.constants import PROVIDERS
config = LiteLLMConfig(providers=PROVIDERS)
with open('my_config.yaml', 'w') as f:
    f.write(config.to_yaml())
"
```

## Project Structure

```
nenlib/
├── constants/          # Provider configurations
│   ├── __init__.py
│   └── models.py
├── helpers/           # Utility functions
│   ├── __init__.py
│   └── utils.py
├── logging/           # Logging setup
│   ├── __init__.py
│   └── logger.py
├── mlops/            # LiteLLM and provider integrations
│   ├── __init__.py
│   ├── litellm.py
│   └── providers.py
├── config.py         # Main configuration
└── mlops.py          # Legacy MLOps config
```

## Development

```bash
# Clone and setup
git clone <repo>
cd nenlib
uv sync --all-extras

# Run tests
uv run pytest

# Format code
uv run ruff format .
uv run isort .
```

## License

MIT License - see LICENSE file for details.