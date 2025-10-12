from dotenv import load_dotenv, find_dotenv 

def load_all_configs():
    """
    Loads LLM provider and logging configuration modules into memory.
    This should be called on import to ensure that all configuration details and
    environment variables are available throughout the application.
    """
    # Ensure .env variables are loaded
    load_dotenv(find_dotenv())
    # Load LLM and logging configs
    from . import llm_providers
    from . import config
    from .helpers import get_env_var

# Load all configs automatically on import
load_all_configs()