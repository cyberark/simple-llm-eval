from unittest.mock import patch

import matplotlib.pyplot as plt
import pytest

from simpleval.cli_args import CONFIG_FILE_HELP
from simpleval.commands.reporting.summarize.summarize_command import summarize_command
from simpleval.commands.reporting.summarize.summarize_py import plot_scores_py
from simpleval.consts import SummaryReportType
from simpleval.evaluation.metrics.calc import MeanScores, Scores
from simpleval.evaluation.schemas.eval_result_schema import EvalTestResult
from simpleval.exceptions import TerminationError
from simpleval.testcases.schemas.llm_task_result import LlmTaskResult


@pytest.fixture
def mock_get_all_testcases():
    with patch('simpleval.commands.reporting.summarize.summarize_command.get_all_testcases') as mock:
        yield mock


@pytest.fixture
def mock_get_all_eval_results():
    with patch('simpleval.commands.reporting.summarize.summarize_command.get_all_eval_results') as mock:
        yield mock


@pytest.fixture
def mock_plot_scores_py():
    with patch('simpleval.commands.reporting.summarize.summarize_command.plot_scores_py') as mock:
        yield mock


@pytest.fixture
def mock_write_summary_report():
    with patch('simpleval.commands.reporting.summarize.summarize_html._write_summary_report') as mock:
        yield mock


@pytest.fixture
def mock_html_get_eval_name():
    with patch('simpleval.commands.reporting.summarize.summarize_html.get_eval_name') as mock:
        yield mock


def test_summarize_command_py(mock_get_all_testcases, mock_get_all_eval_results, mock_plot_scores_py):
    # Setup mocks
    mock_get_all_testcases.return_value = ['testcase1', 'testcase2']
    mock_get_all_eval_results.side_effect = [
        [
            EvalTestResult(metric='metric1', result='result1', explanation='explanation1', normalized_score=0.2,
                           llm_run_result=LlmTaskResult(name='llm_run_result11', prompt='p', prediction='pr', expected_prediction='ep')),
            EvalTestResult(metric='metric2', result='result2', explanation='explanation2', normalized_score=0.7,
                           llm_run_result=LlmTaskResult(name='llm_run_result12', prompt='p', prediction='pr', expected_prediction='ep')),
        ],
        [
            EvalTestResult(metric='metric1', result='result1', explanation='explanation1', normalized_score=0.5,
                           llm_run_result=LlmTaskResult(name='llm_run_result21', prompt='p', prediction='pr', expected_prediction='ep')),
            EvalTestResult(metric='metric2', result='result2', explanation='explanation2', normalized_score=0.3,
                           llm_run_result=LlmTaskResult(name='llm_run_result22', prompt='p', prediction='pr', expected_prediction='ep')),
        ],
    ]

    primary_metric = 'metric1'

    summarize_command(eval_dir='dummy_eval_dir', config_file=CONFIG_FILE_HELP, primary_metric=primary_metric,
                      report_format=SummaryReportType.PY)

    # Assertions
    mock_get_all_testcases.assert_called_once_with('dummy_eval_dir')
    assert mock_get_all_eval_results.call_count == 2
    mock_plot_scores_py.assert_called_once()

    called_testcases, called_scores, _ = mock_plot_scores_py.call_args[1].values()
    assert called_testcases == ['testcase1', 'testcase2']
    # Verify sort (asc) by primary_metric
    assert called_scores[0].metrics[primary_metric].mean < called_scores[1].metrics[primary_metric].mean


def test_summarize_command_html(mock_html_get_eval_name, mock_get_all_testcases, mock_get_all_eval_results):
    # Setup mocks
    mock_html_get_eval_name.return_value = 'eval_name'
    mock_get_all_testcases.return_value = ['testcase1', 'testcase2', 'testcase3']
    mock_get_all_eval_results.side_effect = [
        [
            EvalTestResult(metric='metric1', result='result1', explanation='explanation1', normalized_score=0.2,
                           llm_run_result=LlmTaskResult(name='llm_run_result11', prompt='p', prediction='pr', expected_prediction='ep')),
            EvalTestResult(metric='metric2', result='result2', explanation='explanation2', normalized_score=0.7,
                           llm_run_result=LlmTaskResult(name='llm_run_result12', prompt='p', prediction='pr', expected_prediction='ep')),
            EvalTestResult(metric='metric3', result='result3', explanation='explanation3', normalized_score=0.1,
                           llm_run_result=LlmTaskResult(name='llm_run_result13', prompt='p', prediction='pr', expected_prediction='ep')),
        ],
        [
            EvalTestResult(metric='metric1', result='result1', explanation='explanation1', normalized_score=0.5,
                           llm_run_result=LlmTaskResult(name='llm_run_result21', prompt='p', prediction='pr', expected_prediction='ep')),
            EvalTestResult(metric='metric2', result='result2', explanation='explanation2', normalized_score=0.3,
                           llm_run_result=LlmTaskResult(name='llm_run_result22', prompt='p', prediction='pr', expected_prediction='ep')),
            EvalTestResult(metric='metric3', result='result3', explanation='explanation3', normalized_score=0.1,
                           llm_run_result=LlmTaskResult(name='llm_run_result23', prompt='p', prediction='pr', expected_prediction='ep')),
        ],
        [
            EvalTestResult(metric='metric1', result='result1', explanation='explanation1', normalized_score=0.5,
                           llm_run_result=LlmTaskResult(name='llm_run_result21', prompt='p', prediction='pr', expected_prediction='ep')),
            EvalTestResult(metric='metric2', result='result2', explanation='explanation2', normalized_score=0.3,
                           llm_run_result=LlmTaskResult(name='llm_run_result22', prompt='p', prediction='pr', expected_prediction='ep')),
            EvalTestResult(metric='metric3', result='result3', explanation='explanation3', normalized_score=0.1,
                           llm_run_result=LlmTaskResult(name='llm_run_result33', prompt='p', prediction='pr', expected_prediction='ep')),
        ],
    ]

    with patch('simpleval.commands.reporting.compare.compare_html.webbrowser.open') as mock_open:
        summarize_command(eval_dir='dummy_eval_dir', config_file=CONFIG_FILE_HELP, primary_metric='metric2',
                          report_format=SummaryReportType.HTML)

    # Assertions
    mock_get_all_testcases.assert_called_once_with('dummy_eval_dir')
    assert mock_get_all_eval_results.call_count == 3


def test_summarize_command_primary_metric(mock_html_get_eval_name, mock_get_all_testcases, mock_get_all_eval_results,
                                          mock_write_summary_report):
    # Setup mocks
    mock_html_get_eval_name.return_value = 'eval_name'
    mock_get_all_testcases.return_value = ['testcase1', 'testcase2']
    mock_get_all_eval_results.side_effect = [
        [
            EvalTestResult(metric='metric1', result='result1', explanation='explanation1', normalized_score=0.2,
                           llm_run_result=LlmTaskResult(name='llm_run_result11', prompt='p', prediction='pr', expected_prediction='ep')),
            EvalTestResult(metric='metric2', result='result2', explanation='explanation2', normalized_score=0.7,
                           llm_run_result=LlmTaskResult(name='llm_run_result12', prompt='p', prediction='pr', expected_prediction='ep')),
        ],
        [
            EvalTestResult(metric='metric1', result='result1', explanation='explanation1', normalized_score=0.5,
                           llm_run_result=LlmTaskResult(name='llm_run_result21', prompt='p', prediction='pr', expected_prediction='ep')),
            EvalTestResult(metric='metric2', result='result2', explanation='explanation2', normalized_score=0.3,
                           llm_run_result=LlmTaskResult(name='llm_run_result22', prompt='p', prediction='pr', expected_prediction='ep')),
        ],
    ]

    primary_metric = 'metric1'

    summarize_command(eval_dir='dummy_eval_dir', config_file=CONFIG_FILE_HELP, primary_metric=primary_metric,
                      report_format=SummaryReportType.HTML)

    # Assertions
    mock_get_all_testcases.assert_called_once_with('dummy_eval_dir')
    assert mock_get_all_eval_results.call_count == 2
    mock_write_summary_report.assert_called_once()
    datasets = mock_write_summary_report.call_args[1]['datasets']
    assert datasets[0].get(primary_metric) is not None


def test_summarize_command_no_primary_metric(mock_html_get_eval_name, mock_get_all_testcases, mock_get_all_eval_results,
                                             mock_write_summary_report):
    # Setup mocks
    mock_html_get_eval_name.return_value = 'eval_name'
    mock_get_all_testcases.return_value = ['testcase1', 'testcase2']
    mock_get_all_eval_results.side_effect = [
        [
            EvalTestResult(metric='metric1', result='result1', explanation='explanation1', normalized_score=0.2,
                           llm_run_result=LlmTaskResult(name='llm_run_result11', prompt='p', prediction='pr', expected_prediction='ep')),
            EvalTestResult(metric='metric2', result='result2', explanation='explanation2', normalized_score=0.7,
                           llm_run_result=LlmTaskResult(name='llm_run_result12', prompt='p', prediction='pr', expected_prediction='ep')),
        ],
        [
            EvalTestResult(metric='metric1', result='result1', explanation='explanation1', normalized_score=0.5,
                           llm_run_result=LlmTaskResult(name='llm_run_result21', prompt='p', prediction='pr', expected_prediction='ep')),
            EvalTestResult(metric='metric2', result='result2', explanation='explanation2', normalized_score=0.3,
                           llm_run_result=LlmTaskResult(name='llm_run_result22', prompt='p', prediction='pr', expected_prediction='ep')),
        ],
    ]

    summarize_command(eval_dir='dummy_eval_dir', config_file=CONFIG_FILE_HELP, primary_metric='', report_format=SummaryReportType.HTML)

    # Assertions
    mock_get_all_testcases.assert_called_once_with('dummy_eval_dir')
    assert mock_get_all_eval_results.call_count == 2
    mock_write_summary_report.assert_called_once()
    datasets = mock_write_summary_report.call_args[1]['datasets']
    assert datasets[0].get('metric1') is not None


def test_summarize_command_datasets_creation(mock_html_get_eval_name, mock_get_all_testcases, mock_get_all_eval_results,
                                             mock_write_summary_report):
    # Setup mocks
    mock_html_get_eval_name.return_value = 'eval_name'
    mock_get_all_testcases.return_value = ['testcase1', 'testcase2']
    mock_get_all_eval_results.side_effect = [
        [
            EvalTestResult(metric='metric1', result='result1', explanation='explanation1', normalized_score=0.2,
                           llm_run_result=LlmTaskResult(name='llm_run_result11', prompt='p', prediction='pr', expected_prediction='ep')),
            EvalTestResult(metric='metric2', result='result2', explanation='explanation2', normalized_score=0.7,
                           llm_run_result=LlmTaskResult(name='llm_run_result12', prompt='p', prediction='pr', expected_prediction='ep')),
        ],
        [
            EvalTestResult(metric='metric1', result='result1', explanation='explanation1', normalized_score=0.5,
                           llm_run_result=LlmTaskResult(name='llm_run_result21', prompt='p', prediction='pr', expected_prediction='ep')),
            EvalTestResult(metric='metric2', result='result2', explanation='explanation2', normalized_score=0.3,
                           llm_run_result=LlmTaskResult(name='llm_run_result22', prompt='p', prediction='pr', expected_prediction='ep')),
        ],
    ]

    summarize_command(eval_dir='dummy_eval_dir', config_file=CONFIG_FILE_HELP, primary_metric='metric1',
                      report_format=SummaryReportType.HTML)

    # Assertions
    mock_get_all_testcases.assert_called_once_with('dummy_eval_dir')
    assert mock_get_all_eval_results.call_count == 2
    mock_write_summary_report.assert_called_once()
    datasets = mock_write_summary_report.call_args[1]['datasets']
    assert len(datasets) == 2
    assert all('metric1' in dataset or 'metric2' in dataset for dataset in datasets)


def test_plot_scores_py():
    testcases = ['testcase1', 'testcase2']
    scores = [
        MeanScores(aggregate_mean=0.5, aggregate_std_dev=0.6, metrics={'metric1': Scores(mean=0.5, std_dev=0.2)}),
        MeanScores(aggregate_mean=0.8, aggregate_std_dev=0.7, metrics={'metric1': Scores(mean=0.5, std_dev=0.2)}),
    ]
    primary_metric = 'metric1'

    with patch.object(plt, 'show'):
        plot_scores_py(testcases, scores, primary_metric)


@patch('simpleval.commands.reporting.summarize.summarize_command.get_all_testcases')
@patch('simpleval.commands.reporting.summarize.summarize_command.get_all_eval_results')
@patch('simpleval.commands.reporting.summarize.summarize_command.calc_scores')
@patch('simpleval.commands.reporting.summarize.summarize_command._verify_primary_metric')
def test_invalid_summary_report_type(get_all_testcases, get_all_eval_results, calc_scores, verify_primary_metric):
    with pytest.raises(TerminationError, match='Invalid summary report type: invalid_type'):
        summarize_command(eval_dir='dummy_eval_dir', config_file=CONFIG_FILE_HELP, primary_metric='metric1', report_format='invalid_type')
