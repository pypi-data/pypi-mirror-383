import pytest
from unittest.mock import patch, Mock, MagicMock
import logging
import tempfile
import os
from logger import ColorFormatter, get_logger


class TestColorFormatter:
    def test_color_formatter_debug(self):
        formatter = ColorFormatter()
        record = logging.LogRecord(
            name="test", level=logging.DEBUG, pathname="", lineno=0,
            msg="test message", args=(), exc_info=None
        )
        
        result = formatter.format(record)
        
        assert '\033[94m' in result  # Blue color for DEBUG
        assert '\033[0m' in result   # Reset color

    def test_color_formatter_info(self):
        formatter = ColorFormatter()
        record = logging.LogRecord(
            name="test", level=logging.INFO, pathname="", lineno=0,
            msg="test message", args=(), exc_info=None
        )
        
        result = formatter.format(record)
        
        assert '\033[92m' in result  # Green color for INFO

    def test_color_formatter_unknown_level(self):
        formatter = ColorFormatter()
        record = logging.LogRecord(
            name="test", level=99, pathname="", lineno=0,
            msg="test message", args=(), exc_info=None
        )
        record.levelname = "UNKNOWN"
        
        result = formatter.format(record)
        
        assert '\033[0m' in result  # Should still have reset


class TestGetLogger:
    @patch('logger.Config')
    @patch('logger.os.makedirs')
    def test_get_logger_creates_directory(self, mock_makedirs, mock_config):
        mock_config.LOG_DIR = "/test/logs"
        mock_config.LOG_LEVEL = logging.INFO
        mock_config.LOG_FILE = "test.log"
        
        with patch('logger.logging.getLogger') as mock_get_logger:
            mock_logger = Mock()
            mock_logger.handlers = []
            mock_get_logger.return_value = mock_logger
            
            get_logger("test_logger")
            
            mock_makedirs.assert_called_once_with("/test/logs", exist_ok=True)

    @patch('logger.Config')
    def test_get_logger_no_duplicate_handlers(self, mock_config):
        mock_config.LOG_DIR = "/test/logs"
        mock_config.LOG_LEVEL = logging.INFO
        mock_config.LOG_FILE = "test.log"
        
        with patch('logger.logging.getLogger') as mock_get_logger, \
             patch('logger.os.makedirs'):
            mock_logger = Mock()
            mock_logger.handlers = [Mock()]  # Already has handlers
            mock_get_logger.return_value = mock_logger
            
            result = get_logger("test_logger")
            
            # Should not add new handlers
            assert len(mock_logger.addHandler.call_args_list) == 0