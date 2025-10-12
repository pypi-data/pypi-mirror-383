import pytest
from unittest.mock import patch, Mock
import logging
import os
from config import LogConfig


class TestLogConfig:
    def test_log_levels_structure(self):
        assert LogConfig.LOG_LEVELS["DEBUG"] == logging.DEBUG
        assert LogConfig.LOG_LEVELS["INFO"] == logging.INFO
        assert LogConfig.LOG_LEVELS["WARNING"] == logging.WARNING
        assert LogConfig.LOG_LEVELS["ERROR"] == logging.ERROR
        assert LogConfig.LOG_LEVELS["CRITICAL"] == logging.CRITICAL

    def test_created_time_exists(self):
        assert hasattr(LogConfig, 'CREATED_TIME')
        assert isinstance(LogConfig.CREATED_TIME, str)

    def test_log_file_format(self):
        assert hasattr(LogConfig, 'LOG_FILE')
        assert LogConfig.LOG_FILE.endswith('.log')

    def test_dotenv_path(self):
        assert LogConfig.DOTENV_PATH == ".env"

    @patch('config.os.path.exists')
    @patch('config.os.makedirs')
    def test_log_dir_creation(self, mock_makedirs, mock_exists):
        mock_exists.return_value = False
        
        # Reload config to trigger directory creation logic
        from importlib import reload
        import config
        reload(config)
        
        mock_makedirs.assert_called_with("./logs", exist_ok=True)