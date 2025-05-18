from pathlib import Path

import pytest

from simpleval.consts import EVAL_RESULTS_FILE
from simpleval.evaluation.schemas.eval_result_schema import EvalTestResult
from simpleval.evaluation.utils import get_all_eval_results, get_all_llm_task_results, get_eval_result_file, \
    get_eval_results_sorted_by_name_metric, get_llm_task_result
from simpleval.testcases.schemas.llm_task_result import LlmTaskResult

TEST_EVAL_SET_VALID_FOLDER = Path(__file__).parent.parent / 'resources' / 'eval_sets' / 'valid'
TEST_FOO_TESTCASE_NAME = 'foo_testcase'


def test_get_all_llm_task_results():
    results = get_all_llm_task_results(TEST_EVAL_SET_VALID_FOLDER, TEST_FOO_TESTCASE_NAME)
    assert len(results) > 0
    assert isinstance(results[0], LlmTaskResult)


def test_get_llm_task_result():
    result = get_llm_task_result(TEST_EVAL_SET_VALID_FOLDER, TEST_FOO_TESTCASE_NAME, 'dummy eval case 1')
    assert result.name == 'dummy eval case 1'
    with pytest.raises(ValueError):
        get_llm_task_result(TEST_EVAL_SET_VALID_FOLDER, TEST_FOO_TESTCASE_NAME, 'nonexistent case')


def test_get_testcase_eval_result_file():
    result_file = get_eval_result_file('/fake/dir', 'foo-testcase')
    assert result_file == f'/fake/dir/testcases/foo-testcase/{EVAL_RESULTS_FILE}'


def test_get_all_eval_results():
    results = get_all_eval_results(TEST_EVAL_SET_VALID_FOLDER, TEST_FOO_TESTCASE_NAME)
    assert len(results) > 0
    assert isinstance(results[0], EvalTestResult)


def test_get_eval_results_sorted_by_name_metric():
    results = get_eval_results_sorted_by_name_metric(TEST_EVAL_SET_VALID_FOLDER, TEST_FOO_TESTCASE_NAME)
    assert len(results) > 0
    assert all(result.name_metric == f'{result.llm_run_result.name}:{result.metric}' for result in results)

    sorted_results = sorted(results, key=lambda x: x.name_metric)
    assert results == sorted_results
