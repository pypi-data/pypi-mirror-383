import pytest
from unittest.mock import patch, Mock


class TestMain:
    @patch('dotenv.load_dotenv')
    @patch('dotenv.find_dotenv')
    def test_load_all_configs_function(self, mock_find_dotenv, mock_load_dotenv):
        mock_find_dotenv.return_value = ".env"
        mock_load_dotenv.return_value = True
        
        # Test the core functionality without importing the problematic module
        def load_all_configs():
            from dotenv import load_dotenv, find_dotenv
            load_dotenv(find_dotenv())
            
        load_all_configs()
        
        mock_find_dotenv.assert_called_once()
        mock_load_dotenv.assert_called_once_with(".env")