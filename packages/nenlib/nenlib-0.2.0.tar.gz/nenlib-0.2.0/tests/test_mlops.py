import pytest
from mlops import MLOpsConfig


class TestMLOpsConfig:
    def test_mlops_config_initialization(self):
        config = MLOpsConfig()
        assert config is not None
        assert isinstance(config, MLOpsConfig)