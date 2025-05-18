import json
import os
from unittest.mock import mock_open, patch

import pytest

from simpleval.consts import GLOBAL_CONFIG_FILE
from simpleval.global_config.retries import DEFAULT_RETRY_CONFIG, RetryConfigs, get_global_config_retries


@pytest.fixture
def mock_global_config_file():
    return {'retry_configs': {'judge_model': {'stop_after_attempt': 3, 'multiplier': 1.5, 'min': 5, 'max': 20, 'exp_base': 2}}}


@patch('os.path.exists', return_value=True)
@patch('builtins.open', new_callable=mock_open)
def test_get_global_config_retries_with_file(mock_open_file, mock_exists, mock_global_config_file):
    mock_open_file.return_value.read.return_value = json.dumps(mock_global_config_file)
    with patch('os.getcwd', return_value='/mock/path'):
        result = get_global_config_retries()
        assert result.judge_model.stop_after_attempt == 3
        assert result.judge_model.multiplier == 1.5
        assert result.judge_model.min == 5
        assert result.judge_model.max == 20
        assert result.judge_model.exp_base == 2


@patch('os.path.exists', return_value=False)
def test_get_global_config_retries_without_file(mock_exists):
    result = get_global_config_retries()
    assert result.judge_model == DEFAULT_RETRY_CONFIG
