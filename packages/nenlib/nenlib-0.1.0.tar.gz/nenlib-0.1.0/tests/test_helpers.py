import pytest
from unittest.mock import patch, Mock, mock_open
import os
import tempfile
import shutil
from helpers import dotenv_load, ensure_log_dir_exists, get_env_var


class TestDotenvLoad:
    @patch('helpers.load_dotenv')
    @patch('helpers.find_dotenv')
    def test_dotenv_load(self, mock_find_dotenv, mock_load_dotenv):
        mock_find_dotenv.return_value = ".env"
        mock_load_dotenv.return_value = True
        
        result = dotenv_load()
        
        mock_find_dotenv.assert_called_once()
        mock_load_dotenv.assert_called_once_with(".env")
        assert result is True


class TestEnsureLogDirExists:
    def test_ensure_log_dir_exists_new_dir(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            log_dir = os.path.join(temp_dir, "logs")
            
            ensure_log_dir_exists(log_dir)
            
            assert os.path.exists(log_dir)
            assert os.path.isdir(log_dir)

    def test_ensure_log_dir_exists_existing_dir(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            log_dir = os.path.join(temp_dir, "logs")
            os.makedirs(log_dir)
            
            # Should not raise an error
            ensure_log_dir_exists(log_dir)
            
            assert os.path.exists(log_dir)


class TestGetEnvVar:
    @patch.dict(os.environ, {"TEST_VAR": "test_value"})
    def test_get_env_var_exists(self):
        result = get_env_var("TEST_VAR")
        
        assert result == "test_value"

    def test_get_env_var_not_exists_no_default(self):
        result = get_env_var("NON_EXISTENT_VAR")
        
        assert result is None

    def test_get_env_var_not_exists_with_default(self):
        result = get_env_var("NON_EXISTENT_VAR", "default_value")
        
        assert result == "default_value"

    @patch.dict(os.environ, {"TEST_VAR": "test_value"})
    def test_get_env_var_exists_with_default(self):
        result = get_env_var("TEST_VAR", "default_value")
        
        assert result == "test_value"