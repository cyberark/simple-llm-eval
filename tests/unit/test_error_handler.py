import sys
from unittest.mock import Mock, patch

import pytest
from colorama import Fore

from simpleval.exceptions import NoWorkToDo, TerminationError
from simpleval.utilities.error_handler import handle_exceptions


@patch('simpleval.utilities.error_handler.logging.getLogger')
@patch('sys.exit')
def test_no_work_to_do(mock_exit, mock_get_logger):
    mock_logger = Mock()
    mock_get_logger.return_value = mock_logger

    @handle_exceptions
    def func():
        raise NoWorkToDo()

    func()

    mock_logger.debug.assert_called_once_with('No work to do')
    mock_exit.assert_called_once_with(3)


@patch('simpleval.utilities.error_handler.logging.getLogger')
@patch('sys.exit')
@patch('simpleval.utilities.error_handler.debug_logging_enabled', return_value=False)
def test_termination_error_without_debug(mock_debug_logging, mock_exit, mock_get_logger):
    mock_logger = Mock()
    mock_get_logger.return_value = mock_logger

    @handle_exceptions
    def func():
        raise TerminationError('Termination occurred')

    func()

    mock_logger.error.assert_called_once_with(f'{Fore.RED}Termination occurred{Fore.RESET}')
    mock_exit.assert_called_once_with(2)


@patch('simpleval.utilities.error_handler.logging.getLogger')
@patch('sys.exit')
@patch('simpleval.utilities.error_handler.debug_logging_enabled', return_value=True)
@patch('traceback.TracebackException.from_exception')
def test_termination_error_with_debug(mock_traceback, mock_debug_logging, mock_exit, mock_get_logger):
    mock_logger = Mock()
    mock_get_logger.return_value = mock_logger
    mock_traceback.return_value.format.return_value = ['Formatted traceback', 'Another line']

    @handle_exceptions
    def func():
        raise TerminationError('Termination occurred')

    func()

    # Expect two error calls: one for the message, one for the traceback
    assert mock_logger.error.call_count == 2
    mock_logger.error.assert_any_call(f'{Fore.RED}Termination occurred{Fore.RESET}')
    mock_logger.error.assert_any_call('Formatted traceback\nAnother line')
    mock_traceback.assert_called_once()
    mock_exit.assert_called_once_with(2)


@patch('simpleval.utilities.error_handler.logging.getLogger')
@patch('sys.exit')
@patch('simpleval.utilities.error_handler.debug_logging_enabled', return_value=True)
@patch('traceback.TracebackException.from_exception')
def test_unexpected_exception_with_debug(mock_traceback, mock_debug_logging, mock_exit, mock_get_logger):
    mock_logger = Mock()
    mock_get_logger.return_value = mock_logger
    mock_traceback.return_value.format.return_value = ['Formatted traceback', 'Another line']

    @handle_exceptions
    def func():
        raise ValueError('Unexpected error')

    func()

    # Expect two error calls: one for the message, one for the traceback
    assert mock_logger.error.call_count == 2
    mock_logger.error.assert_any_call(f'{Fore.RED}An unexpected error occurred: Unexpected error{Fore.RESET}')
    mock_logger.error.assert_any_call('Formatted traceback\nAnother line')
    mock_traceback.assert_called_once()
    mock_exit.assert_called_once_with(1)
