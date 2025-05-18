import html
import os
from unittest import mock

import pytest

from simpleval.commands.reporting.compare.common import CompareArgs
from simpleval.commands.reporting.compare.compare_html2.compare_html2 import AGGREGATE_DATA_LEFT_SIDE_PLACEHOLDER, \
    AGGREGATE_DATA_RIGHT_SIDE_PLACEHOLDER, DATA_ITEMS_PLACEHOLDER, EVAL_SET_NAME_PLACEHOLDER, _compare_results_html2, _populate_template, \
    _validate_compare_html_template
from simpleval.evaluation.metrics.calc import MeanScores, Scores
from simpleval.evaluation.schemas.eval_result_schema import EvalTestResult
from simpleval.testcases.schemas.llm_task_result import LlmTaskResult


def test_validate_compare_html_template_success():
    template = f"""
    <html>
    <body>
        {DATA_ITEMS_PLACEHOLDER}
        {AGGREGATE_DATA_LEFT_SIDE_PLACEHOLDER}
        {AGGREGATE_DATA_RIGHT_SIDE_PLACEHOLDER}
    </body>
    </html>
    """
    try:
        _validate_compare_html_template(template)
    except ValueError:
        pytest.fail('Unexpected ValueError raised')


def test_validate_compare_html_template_missing_data_items():
    template = f"""
    <html>
    <body>
        {AGGREGATE_DATA_LEFT_SIDE_PLACEHOLDER}
        {AGGREGATE_DATA_RIGHT_SIDE_PLACEHOLDER}
    </body>
    </html>
    """
    with pytest.raises(ValueError, match='HTML2 Report: Compare template does not contain data items placeholder'):
        _validate_compare_html_template(template)


def test_validate_compare_html_template_missing_left_side():
    template = f"""
    <html>
    <body>
        {DATA_ITEMS_PLACEHOLDER}
        {AGGREGATE_DATA_RIGHT_SIDE_PLACEHOLDER}
    </body>
    </html>
    """
    with pytest.raises(ValueError, match='HTML2 Report: Compare template does not contain left side aggregate data placeholders'):
        _validate_compare_html_template(template)


def test_validate_compare_html_template_missing_right_side():
    template = f"""
    <html>
    <body>
        {DATA_ITEMS_PLACEHOLDER}
        {AGGREGATE_DATA_LEFT_SIDE_PLACEHOLDER}
    </body>
    </html>
    """
    with pytest.raises(ValueError, match='HTML2 Report: Compare template does not contain right side aggregate data placeholders'):
        _validate_compare_html_template(template)


@pytest.fixture
def left_side():
    llm_task_result = LlmTaskResult(name='test1', prompt='prompt1', prediction='prediction1', expected_prediction='expected1')
    eval_result = EvalTestResult(metric='metric1', result='result1', explanation='explanation1', normalized_score=0.8,
                                 llm_run_result=llm_task_result)
    mean_scores = MeanScores(metrics={'metric1': Scores(mean=0.8, std_dev=0.1)}, aggregate_mean=0.8, aggregate_std_dev=0.1)
    return CompareArgs(name='eval_name:testcase1', mean_scores=mean_scores, sorted_results=[eval_result])


@pytest.fixture
def right_side():
    llm_task_result = LlmTaskResult(name='test2', prompt='prompt2', prediction='prediction2', expected_prediction='expected2')
    eval_result = EvalTestResult(metric='metric1', result='result2', explanation='explanation2', normalized_score=0.1,
                                 llm_run_result=llm_task_result)
    mean_scores = MeanScores(metrics={'metric1': Scores(mean=0.2, std_dev=0.3)}, aggregate_mean=0.4, aggregate_std_dev=0.2)
    return CompareArgs(name='eval_name:testcase2', mean_scores=mean_scores, sorted_results=[eval_result])


def test_populate_template(left_side, right_side):
    template = f"""
    <html>
    <body>
        {EVAL_SET_NAME_PLACEHOLDER}
        {DATA_ITEMS_PLACEHOLDER}
        {AGGREGATE_DATA_LEFT_SIDE_PLACEHOLDER}
        {AGGREGATE_DATA_RIGHT_SIDE_PLACEHOLDER}
    </body>
    </html>
    """
    eval_set = 'test_eval_set'
    populated_template = _populate_template(eval_set=eval_set, template=template, left_side=left_side, right_side=right_side)

    assert eval_set in populated_template
    assert 'testcase1' in populated_template
    assert 'testcase2' in populated_template
    assert 'metric1' in populated_template
    assert '0.1' in populated_template
    assert '0.2' in populated_template
    assert '0.4' in populated_template


def test_compare_results_html2(left_side, right_side):
    eval_set = 'test_eval_set'
    with mock.patch('webbrowser.open', return_value=True):
        report_file_path = _compare_results_html2(eval_set=eval_set, left_side=left_side, right_side=right_side)

        with open(report_file_path, 'r') as file:
            written_content = file.read()

        assert eval_set in written_content
        assert 'testcase1' in written_content
        assert 'testcase2' in written_content
        assert 'metric1' in written_content
        assert '0.1' in written_content
        assert '0.2' in written_content
        assert '0.4' in written_content

        os.remove(report_file_path)


def test_html_escape(left_side, right_side):

    xss_string = '<script>alert(\'XSS\')</script>'

    left_side.sorted_results[0].llm_run_result.prediction += xss_string
    left_side.sorted_results[0].result += xss_string
    left_side.sorted_results[0].explanation += xss_string

    right_side.sorted_results[0].llm_run_result.prediction += xss_string
    right_side.sorted_results[0].result += xss_string
    right_side.sorted_results[0].explanation += xss_string

    eval_set = 'test_eval_set'
    with mock.patch('webbrowser.open', return_value=True):
        report_file_path = _compare_results_html2(eval_set=eval_set, left_side=left_side, right_side=right_side)

        with open(report_file_path, 'r') as file:
            written_content = file.read()

        assert xss_string not in written_content

        escaped_xss = html.escape(xss_string)
        assert written_content.count(escaped_xss) == 6

        os.remove(report_file_path)
