import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from pydantic import ValidationError

from simpleval.commands.reporting.eval.eval_report_command import eval_report_command
from simpleval.commands.reporting.eval.eval_report_file_command import eval_report_file_command
from simpleval.consts import ReportFormat
from simpleval.exceptions import TerminationError


@patch('simpleval.commands.reporting.eval.eval_report_command.get_all_eval_results')
@patch('simpleval.commands.reporting.eval.eval_report_command.ResultsManager')
@patch('simpleval.commands.reporting.eval.eval_report_command.get_eval_name')
def test_eval_report_command_console(mock_get_eval_name, mock_ResultsManager, mock_get_all_eval_results):
    mock_get_all_eval_results.return_value = 'mock_results'
    mock_get_eval_name.return_value = 'mock_eval_name'
    mock_results_manager = MagicMock()
    mock_ResultsManager.return_value = mock_results_manager

    eval_report_command('mock_eval_dir', 'config_file.json', 'mock_testcase_dir', 'console')

    mock_get_all_eval_results.assert_called_once_with(eval_set_dir='mock_eval_dir', testcase='mock_testcase_dir')
    mock_get_eval_name.assert_called_once_with(eval_dir='mock_eval_dir', config_file='config_file.json')
    mock_results_manager.display_results.assert_called_once_with(
        name='mock_eval_name',
        testcase='mock_testcase_dir',
        eval_results='mock_results',
        output_format=ReportFormat.CONSOLE,
        llm_tasks_errors_count=0,
        eval_errors_count=0,
    )


@patch('simpleval.commands.reporting.eval.eval_report_command.get_all_eval_results')
@patch('simpleval.commands.reporting.eval.eval_report_command.ResultsManager')
@patch('simpleval.commands.reporting.eval.eval_report_command.get_eval_name')
def test_eval_report_command_html(mock_get_eval_name, mock_ResultsManager, mock_get_all_eval_results):
    mock_get_all_eval_results.return_value = 'mock_results'
    mock_get_eval_name.return_value = 'mock_eval_name'
    mock_results_manager = MagicMock()
    mock_ResultsManager.return_value = mock_results_manager

    eval_report_command('mock_eval_dir', 'config_file.json', 'mock_testcase_dir', 'html')

    mock_get_all_eval_results.assert_called_once_with(eval_set_dir='mock_eval_dir', testcase='mock_testcase_dir')
    mock_get_eval_name.assert_called_once_with(eval_dir='mock_eval_dir', config_file='config_file.json')
    mock_results_manager.display_results.assert_called_once_with(name='mock_eval_name', testcase='mock_testcase_dir',
                                                                 eval_results='mock_results', llm_tasks_errors_count=0, eval_errors_count=0,
                                                                 output_format='html')


@patch('simpleval.commands.reporting.eval.eval_report_command.get_all_eval_results', side_effect=FileNotFoundError('File not found'))
def test_eval_report_command_file_not_found(mock_get_all_eval_results):
    with pytest.raises(TerminationError) as excinfo:
        eval_report_command('mock_eval_dir', 'config_file.json', 'mock_testcase_dir', 'console')

    assert str(excinfo.value) == 'Error occurred trying to report results: File not found'


@patch('simpleval.commands.reporting.eval.eval_report_command.get_all_eval_results', side_effect=ValidationError('Validation error', []))
def test_eval_report_command_validation_error(mock_get_all_eval_results):
    with pytest.raises(TerminationError) as excinfo:
        eval_report_command('mock_eval_dir', 'config_file.json', 'mock_testcase_dir', 'console')

    assert str(excinfo.value).startswith('Error occurred trying to report results: 0 validation errors for Validation error')


def test_eval_report_file_command():
    parent_folder = Path(__file__).parent.parent
    eval_results_file = parent_folder / 'resources/eval_sets/valid/testcases/foo_testcase/eval_results.jsonl'
    eval_results_file = str(eval_results_file)
    assert os.path.exists(eval_results_file)

    eval_report_file_command(name='mock_name', eval_results_file=eval_results_file, report_format='console')
