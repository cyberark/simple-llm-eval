from unittest.mock import patch

import pytest

from simpleval.commands.reporting.compare.compare_command import compare_results
from simpleval.consts import ReportFormat
from simpleval.evaluation.metrics.calc import MeanScores
from simpleval.exceptions import TerminationError
from tests.unit.test_testcases import TEST_EVAL_SET_VALID_FOLDER, TEST_FOO_TESTCASE_NAME


def test_run_compare_command_console():
    compare_results(
        eval_set_dir=TEST_EVAL_SET_VALID_FOLDER,
        testcase1=TEST_FOO_TESTCASE_NAME,
        testcase2=TEST_FOO_TESTCASE_NAME,
        report_format=ReportFormat.CONSOLE,
    )


def test_run_compare_command_html():
    with patch('simpleval.commands.reporting.compare.compare_html.webbrowser.open') as mock_open:
        compare_results(
            eval_set_dir=TEST_EVAL_SET_VALID_FOLDER,
            testcase1=TEST_FOO_TESTCASE_NAME,
            testcase2=TEST_FOO_TESTCASE_NAME,
            report_format=ReportFormat.HTML2,
        )
        mock_open.assert_called_once()


def test_compare_results_report_called_with_correct_names():
    eval_set_name = 'test_eval_set'
    testcase1 = 'testcase1'
    testcase2 = 'testcase2'

    with patch('simpleval.commands.reporting.compare.compare_command.get_eval_set_name', return_value=eval_set_name), \
         patch('simpleval.commands.reporting.compare.compare_command.get_llm_task_results_file', return_value='dummy_path'), \
         patch('simpleval.commands.reporting.compare.compare_command.get_all_eval_results', return_value=[]), \
         patch('simpleval.commands.reporting.compare.compare_command.calc_scores', return_value=MeanScores(aggregate_mean=1, aggregate_std_dev=0, metrics={})), \
         patch('simpleval.commands.reporting.compare.compare_command.get_eval_results_sorted_by_name_metric', return_value=[]), \
         patch('simpleval.commands.reporting.compare.compare_command._compare_results_report') as mock_compare_results_report, \
         patch('os.path.exists', return_value=True):

        compare_results(
            eval_set_dir=TEST_EVAL_SET_VALID_FOLDER,
            testcase1=testcase1,
            testcase2=testcase2,
            report_format=ReportFormat.CONSOLE,
        )

        mock_compare_results_report.assert_called_once()
        left_side, right_side = mock_compare_results_report.call_args[1]['left_side'], mock_compare_results_report.call_args[1][
            'right_side']
        assert left_side.name == f'{eval_set_name}:{testcase1}', 'comparable name must end with the testcase name'
        assert right_side.name == f'{eval_set_name}:{testcase2}', 'comparable name must end with the testcase name'


@pytest.mark.parametrize('ignore_missing_llm_results', [True, False])
def test_compare_results_ignore_missing_llm_results_files_exist(ignore_missing_llm_results):
    eval_set_name = 'test_eval_set'
    testcase1 = 'testcase1'
    testcase2 = 'testcase2'

    with patch('simpleval.commands.reporting.compare.compare_command.get_eval_set_name', return_value=eval_set_name), \
         patch('simpleval.commands.reporting.compare.compare_command.get_llm_task_results_file', return_value='dummy_path'), \
         patch('simpleval.commands.reporting.compare.compare_command.get_all_eval_results', return_value=[]), \
         patch('simpleval.commands.reporting.compare.compare_command.calc_scores', return_value=MeanScores(aggregate_mean=1, aggregate_std_dev=0, metrics={})), \
         patch('simpleval.commands.reporting.compare.compare_command.get_eval_results_sorted_by_name_metric', return_value=[]), \
         patch('simpleval.commands.reporting.compare.compare_command._compare_results_report') as mock_compare_results_report, \
         patch('os.path.exists', return_value=True):

        compare_results(
            eval_set_dir=TEST_EVAL_SET_VALID_FOLDER,
            testcase1=testcase1,
            testcase2=testcase2,
            report_format=ReportFormat.CONSOLE,
            ignore_missing_llm_results=ignore_missing_llm_results,
        )

        mock_compare_results_report.assert_called_once()


def test_compare_results_file_not_found():
    with pytest.raises(TerminationError) as ex:
        compare_results(
            eval_set_dir='missing_dir',
            testcase1='testcase1',
            testcase2='testcase2',
            report_format=ReportFormat.CONSOLE,
        )
