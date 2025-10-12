import os
from dotenv import load_dotenv, find_dotenv
import logging
from .logger import get_logger

class Helpers:
    @classmethod
    def dotenv_load(self):
        """Load environment variables from a .env file found in the project."""
        return load_dotenv(find_dotenv())

    @classmethod
    def ensure_log_dir_exists(selflog_dir: str):
        """Helper to create the log directory if it doesn't exist."""
        os.makedirs(log_dir, exist_ok=True)
    @classmethod
    def get_env_var(key: str, default=None):
        """Retrieve an environment variable, with an optional default fallback."""
        return os.getenv(key, default)



