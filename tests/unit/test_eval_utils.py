import json
import os
from unittest.mock import mock_open, patch

import pytest
from colorama import Fore, Style

from simpleval.consts import EVAL_CONFIG_FILE, EVAL_ERROR_FILE_NAME, EVAL_RESULTS_FILE, LLM_TASKS_ERROR_FILE_NAME, LLM_TASKS_RESULT_FILE
from simpleval.evaluation.schemas.base_eval_case_schema import GroundTruth
from simpleval.evaluation.schemas.eva_task_schema import EvalTask
from simpleval.evaluation.schemas.eval_result_schema import EvalTestResult
from simpleval.evaluation.schemas.eval_task_config_schema import EvalTaskConfig
from simpleval.evaluation.utils import eval_result_found, get_all_eval_results, get_all_testcases, get_empty_eval_set_folder, \
    get_empty_testcase_folder, get_eval_config, get_eval_errors_file, get_eval_ground_truth, get_eval_name, get_eval_result_file, \
    get_eval_results_sorted_by_name_metric, get_llm_task_errors_file, get_llm_task_results_file, highlight_regex, \
    is_llm_task_result_found
from simpleval.testcases.schemas.llm_task_result import LlmTaskResult
from tests.unit.utils import get_test_resources_folder


@pytest.fixture
def eval_dir():
    return os.path.join(get_test_resources_folder(), 'eval_sets/valid')


def test_get_eval_ground_truth(eval_dir):
    result = get_eval_ground_truth(eval_dir)
    assert len(result) > 0
    assert isinstance(result[0], GroundTruth)


def test_get_eval_ground_truth_file_not_found(tmp_path):
    eval_dir = str(tmp_path)
    with pytest.raises(FileNotFoundError):
        get_eval_ground_truth(eval_dir)


def test_get_eval_config(eval_dir):
    result = get_eval_config(eval_dir=eval_dir, config_file=EVAL_CONFIG_FILE)
    assert isinstance(result, EvalTaskConfig)


def test_get_eval_config_file_not_found(tmp_path):
    eval_dir = str(tmp_path)
    with pytest.raises(FileNotFoundError):
        get_eval_config(eval_dir=eval_dir, config_file='no-such-file.json')


def test_get_eval_config_invalid_metrics(eval_dir):
    invalid_config_data = {
        'name': 'foo',
        'max_concurrent_judge_tasks': 10,
        'max_concurrent_llm_tasks': 10,
        'eval_metrics': ['dummy', 'no-such_metric'],
        'llm_as_a_judge_name': 'dummy_judge'
    }

    with patch('builtins.open', mock_open(read_data=json.dumps(invalid_config_data))), \
         patch('json.load', return_value=invalid_config_data):
        with pytest.raises(ValueError) as ex:
            get_eval_config(eval_dir=eval_dir, config_file=EVAL_CONFIG_FILE)
        assert "Invalid Metric(s): `['dummy', 'no-such_metric']`" in str(ex.value)


def test_get_eval_name(eval_dir):
    assert get_eval_name(eval_dir=eval_dir, config_file=EVAL_CONFIG_FILE) == os.path.basename(eval_dir)


def test_highlight_regex():
    text = 'This is a test string.'
    pattern = r'test'
    highlighted_text = highlight_regex(text, pattern)
    expected_text = f'This is a {Fore.BLUE}test{Style.RESET_ALL} string.'
    assert highlighted_text == expected_text


def test_get_empty_eval_dir():
    folder = get_empty_eval_set_folder()
    assert os.path.exists(folder)
    assert os.path.isdir(folder)


def test_get_empty_testcase_dir():
    folder = get_empty_testcase_folder()
    assert os.path.exists(folder)
    assert os.path.isdir(folder)


@pytest.fixture
def testcase_results():
    return [
        LlmTaskResult(name='test1', prompt='Prompt 1', prediction='Prediction 1', expected_prediction='Expected Prediction 1',
                      payload={'key1': 'value1'}),
        LlmTaskResult(name='test2', prompt='Prompt 2', prediction='Prediction 2', expected_prediction='Expected Prediction 2',
                      payload={'key2': 'value2'})
    ]


@pytest.fixture
def eval_results_data():
    return [
        EvalTestResult(
            name='test1', metric='accuracy', result='0.95', explanation='Test explanation', normalized_score=0.95,
            llm_run_result=LlmTaskResult(name='test1', prompt='Prompt 1', prediction='Prediction 1',
                                         expected_prediction='Expected Prediction 1', payload={'key1': 'value1'})),
        EvalTestResult(
            name='test2', metric='accuracy', result='0.90', explanation='Test explanation', normalized_score=0.90,
            llm_run_result=LlmTaskResult(name='test2', prompt='Prompt 2', prediction='Prediction 2',
                                         expected_prediction='Expected Prediction 2', payload={'key2': 'value2'}))
    ]


def test_eval_result_found(eval_results_data):
    eval_task1 = EvalTask(
        metric='accuracy', ground_truth=GroundTruth(name='test1', description='Prompt 1', expected_result='Expected Prediction 1',
                                                    payload={}))
    eval_task2 = EvalTask(
        metric='accuracy', ground_truth=GroundTruth(name='test3', description='Prompt 3', expected_result='Expected Prediction 3',
                                                    payload={}))
    assert eval_result_found(eval_results_data, eval_task1) is True
    assert eval_result_found(eval_results_data, eval_task2) is False


def test_get_testcase_result_file():
    eval_set_dir = '/path/to/eval_set'
    testcase = 'some-testcase'
    expected_path = os.path.join(eval_set_dir, 'testcases', testcase, LLM_TASKS_RESULT_FILE)
    assert get_llm_task_results_file(eval_set_dir, testcase) == expected_path


def test_get_eval_result_file():
    eval_set_dir = '/path/to/eval_set'
    testcase = 'some-testcase'
    expected_path = os.path.join(eval_set_dir, 'testcases', testcase, EVAL_RESULTS_FILE)
    assert get_eval_result_file(eval_set_dir, testcase) == expected_path


def test_get_testcase_errors_file():
    eval_set_dir = '/path/to/eval_set'
    testcase = 'some-testcase'
    expected_path = os.path.join(eval_set_dir, 'testcases', testcase, LLM_TASKS_ERROR_FILE_NAME)
    assert get_llm_task_errors_file(eval_set_dir, testcase) == expected_path


def test_get_eval_errors_file():
    eval_set_dir = '/path/to/eval_set'
    testcase = 'some-testcase'
    expected_path = os.path.join(eval_set_dir, 'testcases', testcase, EVAL_ERROR_FILE_NAME)
    assert get_eval_errors_file(eval_set_dir, testcase) == expected_path


def test_get_all_eval_results_file_not_found(tmp_path):
    with pytest.raises(FileNotFoundError):
        get_all_eval_results(str(tmp_path), 'no-such-testcase', fail_on_missing=True)


def test_get_eval_results_sorted_by_name_metric(tmp_path, eval_results_data):
    testcase = 'foo'
    eval_set_dir = tmp_path
    testcase_dir = eval_set_dir / 'testcases' / testcase
    os.makedirs(testcase_dir, exist_ok=True)
    eval_results_file = testcase_dir / EVAL_RESULTS_FILE
    with eval_results_file.open('w') as f:
        for result in eval_results_data:
            f.write(result.model_dump_json() + '\n')

    results = get_eval_results_sorted_by_name_metric(eval_set_dir, testcase)
    assert len(results) == 2
    assert results[0].name_metric == 'test1:accuracy'
    assert results[1].name_metric == 'test2:accuracy'

    assert results[0].llm_run_result.name == 'test1'
    assert results[1].llm_run_result.name == 'test2'


def test_testcase_result_found(testcase_results):
    assert is_llm_task_result_found(testcase_results, 'test1') is True
    assert is_llm_task_result_found(testcase_results, 'test3') is False


def test_get_all_eval_results_happy_flow(tmp_path, eval_results_data):
    testcase = 'foo'
    eval_set_dir = tmp_path
    testcase_dir = eval_set_dir / 'testcases' / testcase
    os.makedirs(testcase_dir, exist_ok=True)
    eval_results_file = testcase_dir / EVAL_RESULTS_FILE

    with eval_results_file.open('w') as f:
        for result in eval_results_data:
            f.write(result.model_dump_json() + '\n')

    results = get_all_eval_results(eval_set_dir, testcase)
    assert len(results) == 2
    assert results[0].name_metric == 'test1:accuracy'
    assert results[1].name_metric == 'test2:accuracy'
    assert results[0].metric == 'accuracy'
    assert results[1].metric == 'accuracy'
    assert results[0].result == '0.95'
    assert results[1].result == '0.90'
    assert results[0].llm_run_result.name == 'test1'
    assert results[1].llm_run_result.name == 'test2'


def test_get_all_testcases():
    eval_path = os.path.join('simpleval', 'eval_sets', 'dummy_task')
    result = get_all_testcases(eval_path)
    # static_results has eval_results.jsonl, so it should be filtered out
    # Only static_results2 should be returned
    assert len(result) == 1
    assert 'static_results2' in result
    assert 'static_results' not in result
