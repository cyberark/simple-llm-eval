import json
from unittest.mock import MagicMock, patch

import pytest

from simpleval.consts import EVAL_CONFIG_FILE
from simpleval.evaluation.eval_runner import _get_all_evals_by_metric_to_run, filter_existing_eval_results, run_eval
from simpleval.evaluation.metrics.metric_result_schema import MetricResult
from simpleval.evaluation.schemas.base_eval_case_schema import GroundTruth
from simpleval.evaluation.schemas.eva_task_schema import EvalTask
from simpleval.evaluation.schemas.eval_result_schema import EvalTestResult
from simpleval.evaluation.schemas.eval_task_config_schema import EvalTaskConfig
from simpleval.testcases.schemas.llm_task_result import LlmTaskResult


@pytest.fixture
def mock_get_eval_ground_truth():
    with patch('simpleval.evaluation.eval_runner.get_eval_ground_truth') as mock:
        yield mock


@pytest.fixture
def mock_get_eval_config():
    with patch('simpleval.evaluation.eval_runner.get_eval_config') as mock:
        yield mock


@pytest.fixture
def mock_write_results_to_file():
    with patch('simpleval.evaluation.eval_runner._write_results_to_file') as mock:
        yield mock


@pytest.fixture
def mock_get_judge():
    with patch('simpleval.evaluation.eval_runner.JudgeProvider.get_judge') as mock:
        yield mock


@pytest.fixture
def mock_get_llm_task_result():
    with patch('simpleval.evaluation.eval_runner.get_llm_task_result') as mock:
        yield mock


def test_eval_runner(mock_get_eval_ground_truth, mock_get_eval_config, mock_write_results_to_file, mock_get_judge,
                     mock_get_llm_task_result):
    eval_dir = 'foo_eval'
    testcase = 'foo_testcase'

    ground_truth = [
        GroundTruth(name='foo1', description='bar', expected_result='baz', payload={'qux': 'quux'}),
        GroundTruth(name='foo2', description='bar', expected_result='baz', payload={'qux': 'quux'}),
        GroundTruth(name='foo3', description='bar', expected_result='baz', payload={'qux': 'quux'}),
        GroundTruth(name='foo4', description='bar', expected_result='baz', payload={'qux': 'quux'}),
        GroundTruth(name='foo5', description='bar', expected_result='baz', payload={'qux': 'quux'}),
        GroundTruth(name='foo6', description='bar', expected_result='baz', payload={'qux': 'quux'}),
    ]

    eval_config = EvalTaskConfig(name='foo_eval', llm_as_a_judge_name='foo', eval_metrics=['bar'], max_concurrent_llm_tasks=5,
                                 max_concurrent_judge_tasks=5)

    mock_get_eval_ground_truth.return_value = ground_truth
    mock_get_eval_config.return_value = eval_config

    mock_judge = MagicMock()
    mock_judge.evaluate.return_value = MetricResult(result='result', explanation='explanation', normalized_score=1.0)
    mock_get_judge.return_value = mock_judge

    mock_llm_task_result = LlmTaskResult(name='foo', expected_prediction='expected', prompt='prompt', prediction='prediction', payload={})
    mock_get_llm_task_result.return_value = mock_llm_task_result

    results, errors = run_eval(eval_dir=eval_dir, config_file=EVAL_CONFIG_FILE, testcase=testcase)

    assert results
    assert len(results) == len(ground_truth)
    assert not errors
    mock_write_results_to_file.assert_called_once()
    called_args = mock_write_results_to_file.call_args
    assert called_args[0][0] == eval_dir
    assert called_args[0][1] == testcase
    assert len(called_args[0][2]) == len(ground_truth)


def test_filter_existing_eval_results():
    existing_eval_results = [
        EvalTestResult(
            name='foo1', metric='metric1', result='result1', explanation='explanation1', normalized_score=1.0,
            llm_run_result=LlmTaskResult(name='foo1', expected_prediction='expected', prompt='prompt', prediction='prediction',
                                         payload={})),
        EvalTestResult(
            name='foo2', metric='metric2', result='result2', explanation='explanation2', normalized_score=1.0,
            llm_run_result=LlmTaskResult(name='foo2', expected_prediction='expected', prompt='prompt', prediction='prediction',
                                         payload={})),
    ]

    all_evals_to_run = [
        EvalTask(metric='metric2', ground_truth=GroundTruth(name='foo2', description='bar', expected_result='baz', payload={})),
        EvalTask(metric='metric3', ground_truth=GroundTruth(name='foo3', description='bar', expected_result='baz', payload={})),
    ]

    filtered_evals = filter_existing_eval_results(existing_eval_results, all_evals_to_run)

    assert len(filtered_evals) == 1
    assert filtered_evals[0].ground_truth.name == 'foo3'
    assert filtered_evals[0].metric == 'metric3'


def test_get_all_evals_by_metric_to_run(mock_get_eval_ground_truth, mock_get_eval_config):
    eval_dir = 'foo_eval'

    ground_truth = [
        GroundTruth(name='foo1', description='bar', expected_result='baz', payload={'qux': 'quux'}),
        GroundTruth(name='foo2', description='bar', expected_result='baz', payload={'qux': 'quux'}),
    ]

    eval_config = EvalTaskConfig(name='foo_eval', llm_as_a_judge_name='foo', eval_metrics=['metric1', 'metric2'],
                                 max_concurrent_llm_tasks=5, max_concurrent_judge_tasks=5)

    mock_get_eval_ground_truth.return_value = ground_truth
    mock_get_eval_config.return_value = eval_config

    evals_to_run = _get_all_evals_by_metric_to_run(eval_dir, eval_config)

    assert len(evals_to_run) == 4
    assert evals_to_run[0].metric == 'metric1'
    assert evals_to_run[0].ground_truth.name == 'foo1'
    assert evals_to_run[1].metric == 'metric2'
    assert evals_to_run[1].ground_truth.name == 'foo1'
    assert evals_to_run[2].metric == 'metric1'
    assert evals_to_run[2].ground_truth.name == 'foo2'
    assert evals_to_run[3].metric == 'metric2'
    assert evals_to_run[3].ground_truth.name == 'foo2'
