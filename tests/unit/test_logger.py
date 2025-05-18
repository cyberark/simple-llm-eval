import logging
import os
from unittest.mock import MagicMock, patch

import pytest

from simpleval.consts import BOOKKEEPING_LOG_FILE_NAME, BOOKKEEPING_LOGGER_NAME, LOGGER_NAME
from simpleval.logger import init_bookkeeping_logger, init_logger, log_bookkeeping_data


@patch('simpleval.logger.logging.getLogger')
def test_init_logger(mock_get_logger):
    mock_logger = MagicMock()
    mock_get_logger.return_value = mock_logger

    init_logger()

    mock_get_logger.assert_any_call(LOGGER_NAME)
    mock_get_logger.assert_any_call(BOOKKEEPING_LOGGER_NAME)
    mock_logger.setLevel.assert_called_with(logging.INFO)
    assert mock_logger.addHandler.called


@patch('simpleval.logger.os.makedirs')
@patch('simpleval.logger.open')
@patch('simpleval.logger.os.path.exists')
@patch('simpleval.logger.logging.getLogger')
def test_init_bookkeeping_logger(mock_get_logger, mock_exists, mock_open, mock_makedirs):
    mock_logger = MagicMock()
    mock_get_logger.return_value = mock_logger

    # Mock os.path.exists to return False to ensure the open call is triggered
    mock_exists.return_value = False

    # Mock the value of BOOKKEEPING_LOG_FILE_NAME to match the expected behavior
    bookkeeping_log_file_name = os.path.join(os.getcwd(), 'logs', BOOKKEEPING_LOG_FILE_NAME)

    init_bookkeeping_logger()

    mock_makedirs.assert_called_with('logs', exist_ok=True)
    mock_open.assert_called_with(bookkeeping_log_file_name, 'w', encoding='utf-8')
    mock_logger.setLevel.assert_called_with(logging.INFO)
    assert mock_logger.addHandler.called


@patch('simpleval.logger.logging.getLogger')
def test_log_bookkeeping_data(mock_get_logger):
    mock_logger = MagicMock()
    mock_get_logger.return_value = mock_logger

    log_bookkeeping_data('source', 'model_name', 10, 20)

    mock_get_logger.assert_called_with(BOOKKEEPING_LOGGER_NAME)
    mock_logger.info.assert_called_with('msg', extra={'source': 'source', 'model': 'model_name', 'input_tokens': 10, 'output_tokens': 20})
