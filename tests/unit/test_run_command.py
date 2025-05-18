import os
from unittest.mock import MagicMock, call, patch

import pytest

from simpleval.commands.run_command import _clean_error_files, _clean_results, _prompt_and_exit_on_full_results, run_command
from simpleval.consts import EVAL_CONFIG_FILE
from simpleval.evaluation.eval_runner import run_eval
from simpleval.exceptions import NoWorkToDo
from tests.unit.utils import get_eval_sets_folder, get_testcases_folder


@pytest.mark.parametrize('report_format', ['console', 'html'])
@patch('webbrowser.open', MagicMock())
def test_run_command_console(report_format):
    eval_name = 'dummy_task'
    testcase = 'static_results'

    eval_set_dir = os.path.join(get_eval_sets_folder(), eval_name)

    run_command(
        eval_dir=eval_set_dir,
        config_file=EVAL_CONFIG_FILE,
        testcase=testcase,
        report_format=report_format,
        overwrite_results=True,
    )


@pytest.mark.parametrize('overwrite_results', [True, False])
@patch('simpleval.commands.run_command._clean_results')
@patch('simpleval.commands.run_command._clean_error_files')
@patch('simpleval.commands.run_command._prompt_and_exit_on_full_results')
@patch('simpleval.commands.run_command.run_llm_tasks', return_value=(None, []))
@patch('simpleval.commands.run_command.run_eval', return_value=(None, []))
@patch('simpleval.commands.run_command.ResultsManager.display_results')
def test_run_command_overwrite_results(mock_display_results, mock_run_eval, mock_run_llm_tasks, mock_prompt_and_exit,
                                       mock_clean_error_files, mock_clean_results, overwrite_results):
    eval_name = 'dummy_task'
    testcase = 'static_results'

    eval_set_dir = os.path.join(get_eval_sets_folder(), eval_name)

    run_command(
        eval_dir=eval_set_dir,
        config_file=EVAL_CONFIG_FILE,
        testcase=testcase,
        overwrite_results=overwrite_results,
        report_format='html',
    )

    mock_clean_error_files.assert_called_once_with(eval_set_dir=eval_set_dir, testcase=testcase)
    if overwrite_results:
        mock_clean_results.assert_called_once_with(eval_set_dir=eval_set_dir, testcase=testcase)
        mock_prompt_and_exit.assert_not_called()
    else:
        mock_clean_results.assert_not_called()
        mock_prompt_and_exit.assert_called_once_with(eval_dir=eval_set_dir, config_file=EVAL_CONFIG_FILE, testcase=testcase)


@patch('simpleval.commands.run_command.delete_file')
@patch('simpleval.commands.run_command.get_llm_task_results_file')
@patch('simpleval.commands.run_command.get_eval_result_file')
def test_clean_results(mock_get_eval_result_file, mock_get_llm_task_result_file, mock_delete_file):
    # Arrange
    eval_set_dir = 'eval_set_dir'
    testcase = 'testcase'
    mock_get_llm_task_result_file.return_value = 'testcase_result_file'
    mock_get_eval_result_file.return_value = 'eval_result_file'

    # Act
    _clean_results(eval_set_dir=eval_set_dir, testcase=testcase)

    # Assert
    mock_get_llm_task_result_file.assert_called_once_with(eval_set_dir=eval_set_dir, testcase=testcase)
    mock_get_eval_result_file.assert_called_once_with(eval_set_dir=eval_set_dir, testcase=testcase)
    mock_delete_file.assert_has_calls([call('testcase_result_file'), call('eval_result_file')], any_order=True)


@patch('simpleval.commands.run_command.delete_file')
@patch('simpleval.commands.run_command.get_llm_task_errors_file')
@patch('simpleval.commands.run_command.get_eval_errors_file')
def test_clean_error_files(mock_get_eval_errors_file, mock_get_llm_task_errors_file, mock_delete_file):
    # Arrange
    eval_set_dir = 'eval_set_dir'
    testcase = 'testcase'
    mock_get_llm_task_errors_file.return_value = 'testcase_errors_file'
    mock_get_eval_errors_file.return_value = 'eval_errors_file'

    # Act
    _clean_error_files(eval_set_dir=eval_set_dir, testcase=testcase)

    # Assert
    mock_get_llm_task_errors_file.assert_called_once_with(eval_set_dir=eval_set_dir, testcase=testcase)
    mock_get_eval_errors_file.assert_called_once_with(eval_set_dir=eval_set_dir, testcase=testcase)
    mock_delete_file.assert_has_calls([call('testcase_errors_file'), call('eval_errors_file')], any_order=True)


@patch('simpleval.commands.run_command.get_all_eval_results', return_value=[])
@patch('simpleval.commands.run_command.get_all_llm_task_results', return_value=[])
@patch('simpleval.commands.run_command.get_eval_ground_truth', return_value=[])
@patch('simpleval.commands.run_command.logging.getLogger')
def test_prompt_and_exit_on_full_results_no_testcase_results(mock_get_logger, mock_get_eval_ground_truth, mock_get_all_llm_task_results,
                                                             mock_get_all_eval_results):
    mock_logger = MagicMock()
    mock_get_logger.return_value = mock_logger

    eval_dir = 'dummy_eval_dir'
    testcase_dir = 'dummy_testcase_dir'

    _prompt_and_exit_on_full_results(eval_dir=eval_dir, config_file=EVAL_CONFIG_FILE, testcase=testcase_dir)

    mock_get_all_eval_results.assert_not_called()


@patch('simpleval.commands.run_command.get_all_llm_task_results', return_value=['result'])
@patch('simpleval.commands.run_command.get_all_eval_results', side_effect=FileNotFoundError)
@patch('simpleval.commands.run_command.get_eval_ground_truth', return_value=[])
@patch('simpleval.commands.run_command.logging.getLogger')
def test_prompt_and_exit_on_full_results_no_eval_results(mock_get_logger, mock_get_eval_ground_truth, mock_get_all_eval_results,
                                                         mock_get_all_llm_task_results):
    mock_logger = MagicMock()
    mock_get_logger.return_value = mock_logger

    eval_dir = 'dummy_eval_dir'
    testcase_dir = 'dummy_testcase_dir'

    _prompt_and_exit_on_full_results(eval_dir=eval_dir, config_file=EVAL_CONFIG_FILE, testcase=testcase_dir)

    mock_get_all_eval_results.assert_called_once()


@patch('simpleval.commands.run_command.get_all_llm_task_results', return_value=['result'])
@patch('simpleval.commands.run_command.get_all_eval_results', return_value=['result'])
@patch('simpleval.commands.run_command.get_eval_ground_truth', return_value=['ground_truth'] * 5)
@patch('simpleval.commands.run_command.logging.getLogger')
def test_prompt_and_exit_on_full_results_missing_testcase_results(mock_get_logger, mock_get_eval_ground_truth, mock_get_all_eval_results,
                                                                  mock_get_all_llm_task_results):
    mock_logger = MagicMock()
    mock_get_logger.return_value = mock_logger

    eval_dir = 'dummy_eval_dir'
    testcase_dir = 'dummy_testcase_dir'

    _prompt_and_exit_on_full_results(eval_dir=eval_dir, config_file=EVAL_CONFIG_FILE, testcase=testcase_dir)

    mock_logger.debug.assert_called_with(f'prompt_user_on_full_results: 4 llm task(s) not found for ground truth')


@patch('simpleval.commands.run_command.get_all_llm_task_results', return_value=['result'] * 5)
@patch('simpleval.commands.run_command.get_all_eval_results', return_value=['result'])
@patch('simpleval.commands.run_command.get_eval_ground_truth', return_value=['ground_truth'] * 5)
@patch('simpleval.commands.run_command.get_eval_config', return_value=MagicMock(eval_metrics=['metric1', 'metric2']))
@patch('simpleval.commands.run_command.logging.getLogger')
def test_prompt_and_exit_on_full_results_missing_eval_results(mock_get_logger, mock_get_eval_config, mock_get_eval_ground_truth,
                                                              mock_get_all_eval_results, mock_get_all_llm_task_results):
    mock_logger = MagicMock()
    mock_get_logger.return_value = mock_logger

    eval_dir = 'dummy_eval_dir'
    testcase_dir = 'dummy_testcase_dir'

    _prompt_and_exit_on_full_results(eval_dir=eval_dir, config_file=EVAL_CONFIG_FILE, testcase=testcase_dir)

    mock_logger.error.assert_called_with(f'prompt_user_on_full_results: 9 eval results not found for ground truth')


@patch('simpleval.commands.run_command.get_all_llm_task_results', return_value=['result'] * 5)
@patch('simpleval.commands.run_command.get_all_eval_results', return_value=['result'] * 10)
@patch('simpleval.commands.run_command.get_eval_ground_truth', return_value=['ground_truth'] * 5)
@patch('simpleval.commands.run_command.get_eval_config', return_value=MagicMock(eval_metrics=['metric1', 'metric2']))
@patch('simpleval.commands.run_command.logging.getLogger')
def test_prompt_and_exit_on_full_results_all_results_exist(mock_get_logger, mock_get_eval_config, mock_get_eval_ground_truth,
                                                           mock_get_all_eval_results, mock_get_all_llm_task_results):
    mock_logger = MagicMock()
    mock_get_logger.return_value = mock_logger

    eval_dir = 'dummy_eval_dir'
    testcase_dir = 'dummy_testcase_dir'

    with pytest.raises(NoWorkToDo):
        _prompt_and_exit_on_full_results(eval_dir=eval_dir, config_file=EVAL_CONFIG_FILE, testcase=testcase_dir)


@pytest.mark.parametrize('evals_to_run', [[], [MagicMock()]])
@patch('simpleval.evaluation.eval_runner._write_results_to_file')
@patch('simpleval.evaluation.eval_runner._get_all_evals_by_metric_to_run', return_value=[])
@patch('simpleval.evaluation.eval_runner.filter_existing_eval_results', return_value=[])
@patch('simpleval.evaluation.eval_runner.get_all_eval_results', return_value=[])
@patch('simpleval.evaluation.eval_runner.get_eval_config', return_value=MagicMock(eval_metrics=['metric1']))
def test_run_eval_empty_evals_to_run(mock_get_eval_config, mock_get_all_eval_results, mock_filter_existing_eval_results,
                                     mock_get_all_evals_by_metric_to_run, mock_write_results_to_file, evals_to_run):
    eval_dir = 'dummy_eval_dir'
    testcases_dir = 'dummy_testcases_dir'

    results, errors = run_eval(eval_dir=eval_dir, config_file=EVAL_CONFIG_FILE, testcase=testcases_dir)

    assert results == []
    assert errors == []
    mock_write_results_to_file.assert_not_called()
