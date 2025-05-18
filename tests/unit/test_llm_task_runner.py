import os
from unittest.mock import patch

import pytest

from simpleval.consts import EVAL_CONFIG_FILE
from simpleval.evaluation.llm_task_runner import run_llm_tasks
from simpleval.evaluation.schemas.base_eval_case_schema import GroundTruth
from simpleval.evaluation.schemas.eval_task_config_schema import EvalTaskConfig
from simpleval.testcases.schemas.llm_task_result import LlmTaskResult


@pytest.fixture
def mock_exists():
    with patch('os.path.exists') as mock:
        yield mock


@pytest.fixture
def mock_get_eval_ground_truth():
    with patch('simpleval.evaluation.llm_task_runner.get_eval_ground_truth') as mock:
        yield mock


@pytest.fixture
def mock_get_eval_config():
    with patch('simpleval.evaluation.llm_task_runner.get_eval_config') as mock:
        yield mock


@pytest.fixture
def mock_load_plugin():
    with patch('simpleval.evaluation.llm_task_runner._load_plugin') as mock:
        yield mock


@pytest.fixture
def mock_write_llm_task_results_file():
    with patch('simpleval.evaluation.llm_task_runner.write_llm_task_results_file') as mock:
        yield mock


@pytest.fixture
def mock_prompt():
    with patch('simpleval.evaluation.llm_task_runner.prompt') as mock:
        yield mock


def test_llm_task_runner(mock_get_eval_ground_truth, mock_get_eval_config, mock_load_plugin, mock_write_llm_task_results_file):
    eval_dir = 'foo_eval'
    testcase = 'foo_testcases'

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
    mock_load_plugin.return_value = lambda name, payload: LlmTaskResult(
        name=name,
        prompt='this is what you send to your llm',
        prediction='hi there!',
        payload=payload,
    )

    results, errors = run_llm_tasks(eval_dir=eval_dir, testcase=testcase, config_file=EVAL_CONFIG_FILE)

    assert results
    assert len(results) == len(ground_truth)
    assert not errors
    mock_write_llm_task_results_file.assert_called_once()
    called_args = mock_write_llm_task_results_file.call_args
    assert called_args[1]['eval_set_dir'] == eval_dir
    assert called_args[1]['testcase'] == testcase
    assert 'results' in called_args[1]
    assert len(called_args[1]['results']) == len(ground_truth)
