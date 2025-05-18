import os
from pathlib import Path
from unittest.mock import patch

import pytest

from simpleval.commands.reporting.compare.compare_command import compare_results_files
from simpleval.consts import ReportFormat
from simpleval.evaluation.metrics.calc import MeanScores
from tests.unit.test_testcases import TEST_EVAL_SET_VALID_FOLDER, TEST_FOO_TESTCASE_NAME

EVAL_RESULT_FILE1 = os.path.join(TEST_EVAL_SET_VALID_FOLDER, 'testcases', TEST_FOO_TESTCASE_NAME, 'eval_results.jsonl')
EVAL_RESULT_FILE2 = os.path.join(TEST_EVAL_SET_VALID_FOLDER, 'testcases', TEST_FOO_TESTCASE_NAME, 'eval_results.jsonl')


def test_run_compare_command_console():
    eval_set_name = 'test_eval_set'

    compare_results_files(
        name=eval_set_name,
        eval_results_file1=EVAL_RESULT_FILE1,
        eval_results_file2=EVAL_RESULT_FILE2,
        report_format=ReportFormat.CONSOLE,
    )


@pytest.mark.parametrize('report_format', [ReportFormat.HTML, ReportFormat.HTML2])
def test_run_compare_command_htmls(report_format):
    eval_set_name = 'test_eval_set'

    with patch('simpleval.commands.reporting.compare.compare_html.webbrowser.open') as mock_open:
        compare_results_files(
            name=eval_set_name,
            eval_results_file1=EVAL_RESULT_FILE1,
            eval_results_file2=EVAL_RESULT_FILE2,
            report_format=report_format,
        )
        mock_open.assert_called_once()


def test_compare_results_report_called_with_correct_names():
    with patch('simpleval.commands.reporting.compare.compare_command.get_all_eval_results', return_value=[]), \
         patch('simpleval.commands.reporting.compare.compare_command.calc_scores', return_value=MeanScores(aggregate_mean=1, aggregate_std_dev=0, metrics={})), \
         patch('simpleval.commands.reporting.compare.compare_command.get_eval_results_sorted_by_name_metric', return_value=[]), \
         patch('simpleval.commands.reporting.compare.compare_command._compare_results_report') as mock_compare_results_report, \
         patch('os.path.exists', return_value=True):

        eval_set_name = 'test_eval_set'
        testcase1 = str(Path(EVAL_RESULT_FILE1).stem)
        testcase2 = str(Path(EVAL_RESULT_FILE2).stem)

        compare_results_files(
            name=eval_set_name,
            eval_results_file1=EVAL_RESULT_FILE1,
            eval_results_file2=EVAL_RESULT_FILE2,
            report_format=ReportFormat.CONSOLE,
        )

        mock_compare_results_report.assert_called_once()
        left_side, right_side = mock_compare_results_report.call_args[1]['left_side'], mock_compare_results_report.call_args[1][
            'right_side']

        assert left_side.name == f'{eval_set_name}:{testcase1}', 'comparable name must end with the testcase name'
        assert right_side.name == f'{eval_set_name}:{testcase2}', 'comparable name must end with the testcase name'
