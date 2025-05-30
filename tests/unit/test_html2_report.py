import html
import os
from unittest import mock
from unittest.mock import patch

import pytest

from simpleval.commands.reporting.eval.html2.html2_report import AGGREGATE_METRIC_PLACEHOLDER, DATA_ITEMS_PLACEHOLDER, \
    EVAL_ERRORS_PLACEHOLDER, EVAL_TESTCASE_TITLE_PLACEHOLDER, HIDDEN_ERRORS_BANNER, LLM_ERRORS_PLACEHOLDER, _generate_html_report2, \
    _validate_eval_html_template
from simpleval.evaluation.metrics.calc import MeanScores, Scores
from simpleval.evaluation.schemas.eval_result_schema import EvalTestResult
from simpleval.testcases.schemas.llm_task_result import LlmTaskResult


@pytest.mark.parametrize('llm_task_errors_count, eval_errors_count', [(0, 0), (1, 1)])
@patch('simpleval.commands.reporting.eval.html2.html2_report.save_html_report')
def test_generate_html_report2(save_html_report, llm_task_errors_count, eval_errors_count):

    eval_results = [
        EvalTestResult(metric='test_metric1', result='pass', explanation='y not pass',
                       llm_run_result=LlmTaskResult(name='yo', prompt='yoyo', prediction='yoyoma',
                                                    expected_prediction='yoyoma'), normalized_score=0.9),
        EvalTestResult(metric='test_metric2', result='pass', explanation='y not pass',
                       llm_run_result=LlmTaskResult(name='yo', prompt='yoyo', prediction='yoyoma',
                                                    expected_prediction='yoyoma'), normalized_score=0.9),
    ]

    metric_means = MeanScores(metrics={
        'metric1': Scores(mean=0.5, std_dev=0.1),
        'metric2': Scores(mean=0.5, std_dev=0.1)
    }, aggregate_mean=0.85, aggregate_std_dev=0.1)

    result = _generate_html_report2(name='test_name', testcase='test_case', eval_results=eval_results, mean_scores=metric_means,
                                    llm_task_errors_count=llm_task_errors_count, eval_errors_count=eval_errors_count)

    assert result


@pytest.mark.parametrize('template,missing_placeholder', [
    ('', 'data items placeholder'),
    (DATA_ITEMS_PLACEHOLDER, 'aggregate metric placeholder'),
    (f'{DATA_ITEMS_PLACEHOLDER}\n{AGGREGATE_METRIC_PLACEHOLDER}', 'llm errors placeholder'),
    (f'{DATA_ITEMS_PLACEHOLDER}\n{AGGREGATE_METRIC_PLACEHOLDER}\n{LLM_ERRORS_PLACEHOLDER}', 'eval errors placeholder'),
    (f'{DATA_ITEMS_PLACEHOLDER}\n{AGGREGATE_METRIC_PLACEHOLDER}\n{LLM_ERRORS_PLACEHOLDER}\n{EVAL_ERRORS_PLACEHOLDER}',
     'hidden errors banner placeholder'),
])
def test_validate_eval_html_template_invalid(template, missing_placeholder):
    with pytest.raises(ValueError):
        _validate_eval_html_template(template)


def test_validate_eval_html_template_valid():
    valid_template = f'''{EVAL_TESTCASE_TITLE_PLACEHOLDER}
    {DATA_ITEMS_PLACEHOLDER}
    {AGGREGATE_METRIC_PLACEHOLDER}
    {LLM_ERRORS_PLACEHOLDER}
    {EVAL_ERRORS_PLACEHOLDER}
    {HIDDEN_ERRORS_BANNER}'''

    _validate_eval_html_template(valid_template)  # Should not raise any exception


def test_html_escape():

    xss_string = '<script>alert(\'XSS\')</script>'

    eval_results = [
        EvalTestResult(
            metric='test_metric1', result='pass' + xss_string, explanation='y not pass' + xss_string,
            llm_run_result=LlmTaskResult(name='yo', prompt='yoyo', prediction='yoyoma' + xss_string,
                                         expected_prediction='yoyoma'), normalized_score=0.9)
    ]

    metric_means = MeanScores(metrics={
        'metric1': Scores(mean=0.5, std_dev=0.1),
        'metric2': Scores(mean=0.5, std_dev=0.1)
    }, aggregate_mean=0.85, aggregate_std_dev=0.1)

    with mock.patch('webbrowser.open', return_value=True):
        report_file_path = _generate_html_report2(name='test_name', testcase='test_case', eval_results=eval_results,
                                                  mean_scores=metric_means, llm_task_errors_count=0, eval_errors_count=0)
        with open(report_file_path, 'r', encoding='utf-8') as file:
            written_content = file.read()

        assert xss_string not in written_content

        escaped_xss = html.escape(xss_string)
        assert written_content.count(escaped_xss) == 3

        os.remove(report_file_path)
