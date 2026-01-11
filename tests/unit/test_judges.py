import json
import xml.etree.ElementTree
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from pydantic import ValidationError
from tenacity import RetryError

from simpleval.evaluation.judges.base_judge import BaseJudge
from simpleval.evaluation.judges.consts import JUDGE_MODULE_FILE, JUDGE_PACKAGE
from simpleval.evaluation.judges.judge_provider import JudgeProvider
from simpleval.evaluation.judges.models.anthropic.judge import AnthropicJudge
from simpleval.evaluation.judges.models.azure.judge import AzureJudge
from simpleval.evaluation.judges.models.dummy_judge.judge import DummyJudge
from simpleval.evaluation.judges.models.gemini.judge import GeminiJudge
from simpleval.evaluation.judges.models.generic_bedrock.judge import GenericBedrockJudge
from simpleval.evaluation.judges.models.open_ai.judge import OpenAIJudge
from simpleval.evaluation.judges.models.vertex_ai.judge import VertexAIJudge
from simpleval.evaluation.metrics.base_metric import EvaluationMetric
from simpleval.evaluation.metrics.parsers.common import RETRYABLE_PARSING_ERRORS

ALL_METRICS_LIST = [
    'coherence',
    'completeness',
    'correctness',
    'faithfulness',
    'following_instructions',
    'helpfulness',
    'no_ground_truth',
    'no_ground_truth_simple',
    'pro_style_and_tone',
    'readability',
    'relevance',
]

EXPECTED_METRICS = {
    'anthropic': ALL_METRICS_LIST,
    'azure': ALL_METRICS_LIST,
    'bedrock_claude_sonnet': ALL_METRICS_LIST,
    'dummy_judge': ['dummy', 'completeness'],
    'gemini': ALL_METRICS_LIST,
    'generic_bedrock': ALL_METRICS_LIST,
    'litellm_structured_output': ALL_METRICS_LIST,
    'open_ai': ALL_METRICS_LIST,
    'vertex_ai': ALL_METRICS_LIST,
}


def test_base_judge_default_attributes():
    judge_name = 'dummy_judge'
    judge: BaseJudge = JudgeProvider.get_judge(judge_name)

    assert isinstance(judge, BaseJudge)
    assert judge.name == judge_name
    assert judge.model_id == DummyJudge.DEFAULT_MODEL_ID
    assert judge._supported_model_ids == [DummyJudge.DEFAULT_MODEL_ID, 'test_model_id_2']
    assert judge._metrics_model == 'test_metric'

    metrics = judge.list_metrics()
    assert len(metrics) == 2

    for metric in metrics:
        metric = judge.get_metric(metric)
        assert isinstance(metric, EvaluationMetric)

    metrics_dir = Path(judge.get_metrics_dir())
    expected_path_suffix = Path('simpleval/evaluation/metrics/models/test_metric')
    assert metrics_dir.parts[-len(expected_path_suffix.parts):] == expected_path_suffix.parts


def test_all_judges():
    judges_names = JudgeProvider.list_judges()
    assert len(judges_names) == len(EXPECTED_METRICS)
    assert all(judge in EXPECTED_METRICS for judge in judges_names)

    judges = JudgeProvider.get_all_judges()

    assert len(judges) == len(EXPECTED_METRICS)

    for judge_name, judge in judges.items():
        assert judge_name in EXPECTED_METRICS
        metric_names = EXPECTED_METRICS[judge_name]

        assert isinstance(judge, BaseJudge)
        assert judge.name == judge_name

        metric_names = judge.list_metrics()
        assert len(metric_names) > 0

        for metric_name in metric_names:
            metric_name = judge.get_metric(metric_name)
            assert isinstance(metric_name, EvaluationMetric)
            assert metric_name.name in EXPECTED_METRICS[judge_name]

        metrics = judge.get_all_metrics()
        assert len(metrics) == len(metric_names)

        for metric_name in metrics:
            metric = metrics[metric_name]
            assert isinstance(metric, EvaluationMetric)
            assert metric.name in metric_names


def test_judge_consts():
    judge_name = 'dummy_judge'
    package = JUDGE_PACKAGE.format(judge_name=judge_name)
    module_name = Path(JUDGE_MODULE_FILE).stem
    assert package == f'simpleval.evaluation.judges.models.{judge_name}.{module_name}'

    try:
        __import__(package)
    except ImportError:
        raise AssertionError(f'Failed to import {package}')


def test_judges_dir():
    path = Path(JudgeProvider.judges_dir())
    expected_path_suffix = Path('simpleval/evaluation/judges/models')
    assert path.parts[-len(expected_path_suffix.parts):] == expected_path_suffix.parts
    assert path.exists()
    assert path.is_dir()


def test_get_judge_module_not_found():
    judge_name = 'no-such-judge'
    with pytest.raises(ValueError, match=f'Judge `{judge_name}` module not found'):
        JudgeProvider.get_judge(judge_name)


@patch('time.sleep', return_value=None)
def test_parsing_retry(mock_sleep):
    judge_name = 'dummy_judge'
    judge: BaseJudge = JudgeProvider.get_judge(judge_name)

    for error in RETRYABLE_PARSING_ERRORS:
        if error is ValidationError:
            judge._model_inference = MagicMock(side_effect=error([], []))
        elif error is json.JSONDecodeError:
            judge._model_inference = MagicMock(side_effect=error('Test error', 'doc', 0))
        elif error is xml.etree.ElementTree.ParseError:
            judge._model_inference = MagicMock(side_effect=error('Test error'))
        else:
            judge._model_inference = MagicMock(side_effect=error('Test error'))

        with pytest.raises(RetryError):
            judge.evaluate(metric_name='dummy', prompt='prompt', prediction='prediction', ground_truth='ground_truth')


def test_list_judges():
    judge_names_all = JudgeProvider.list_judges(filter_internal=False)
    assert len(judge_names_all) > 1
    assert 'dummy_judge' in judge_names_all

    judge_names_filtered = JudgeProvider.list_judges(filter_internal=True)
    assert len(judge_names_filtered) == len(judge_names_all) - 1
    assert 'dummy_judge' not in judge_names_filtered


def test_open_ai_judge():
    judge_name = 'open_ai'
    judge: BaseJudge = JudgeProvider.get_judge(judge_name)

    assert isinstance(judge, OpenAIJudge)
    assert judge.name == judge_name
    assert judge.model_id == 'gpt-4.1-mini-2025-04-14'
    assert judge._metrics_model == 'litellm_structured_output'


def test_anthropic_judge():
    judge_name = 'anthropic'
    judge: BaseJudge = JudgeProvider.get_judge(judge_name)

    assert isinstance(judge, AnthropicJudge)
    assert judge.name == judge_name
    assert judge.model_id == 'claude-haiku-4-5'
    assert judge._metrics_model == 'litellm_structured_output'


def test_vertex_ai_judge():
    judge_name = 'vertex_ai'
    judge: BaseJudge = JudgeProvider.get_judge(judge_name)

    assert isinstance(judge, VertexAIJudge)
    assert judge.name == judge_name
    assert judge.model_id == 'vertex_ai/gemini-2.0-flash'
    assert judge._metrics_model == 'litellm_structured_output'


def test_gemini_judge():
    judge_name = 'gemini'
    judge: BaseJudge = JudgeProvider.get_judge(judge_name)

    assert isinstance(judge, GeminiJudge)
    assert judge.name == judge_name
    assert judge.model_id == 'gemini/gemini-2.5-flash'
    assert judge._metrics_model == 'litellm_structured_output'


def test_azure_judge():
    judge_name = 'azure'
    judge: BaseJudge = JudgeProvider.get_judge(judge_name)

    assert isinstance(judge, AzureJudge)
    assert judge.name == judge_name
    assert judge.model_id == 'azure/gpt-4.1-mini'
    assert judge._metrics_model == 'litellm_structured_output'


def test_generic_bedrock_judge():
    judge_name = 'generic_bedrock'
    judge: BaseJudge = JudgeProvider.get_judge(judge_name)

    assert isinstance(judge, GenericBedrockJudge)
    assert judge.name == judge_name
    assert judge.model_id == 'amazon.nova-pro-v1:0'
    assert judge._metrics_model == 'litellm_structured_output'


def test_azure_run_preliminary_checks():
    judge_name = 'azure'
    judge: BaseJudge = JudgeProvider.get_judge(judge_name)

    # mock verify_env_var and check if it was called three times with all three env vars
    with patch('simpleval.evaluation.judges.models.azure.judge.verify_env_var') as mock_verify_env_var:
        judge.run_preliminary_checks()
        assert mock_verify_env_var.call_count == 3
        mock_verify_env_var.assert_any_call('AZURE_OPENAI_API_KEY')
        mock_verify_env_var.assert_any_call('AZURE_API_BASE')
        mock_verify_env_var.assert_any_call('AZURE_API_VERSION')


@pytest.mark.parametrize(
    'judge_name, env_vars',
    [
        ('gemini', ['GEMINI_API_KEY']),
        ('open_ai', ['OPENAI_API_KEY']),
        ('vertex_ai', ['GOOGLE_APPLICATION_CREDENTIALS', 'VERTEXAI_LOCATION', 'VERTEXAI_PROJECT']),
    ],
)
def test_run_preliminary_checks(judge_name, env_vars):
    judge: BaseJudge = JudgeProvider.get_judge(judge_name)

    with patch(f'simpleval.evaluation.judges.models.{judge_name}.judge.verify_env_var') as mock_verify_env_var:
        judge.run_preliminary_checks()
        assert mock_verify_env_var.call_count == len(env_vars)
        for env_var in env_vars:
            mock_verify_env_var.assert_any_call(env_var)
