import json
from unittest.mock import MagicMock

import pytest
from botocore.exceptions import ClientError

from simpleval.evaluation.judges.judge_utils import BEDROCK_API_KEY_ENV_VAR
from simpleval.evaluation.judges.models.bedrock_claude_sonnet.consts import SONNET45_V1_MODEL_ID
from simpleval.evaluation.judges.models.bedrock_claude_sonnet.judge import BedrockClaudeSonnetJudge
from simpleval.evaluation.metrics.models.bedrock_claude_sonnet.base.base_metric import BaseBedrockSonnetMetric


@pytest.fixture
def mock_metric():
    metric = MagicMock(spec=BaseBedrockSonnetMetric)
    metric.prefill = '{'
    return metric


@pytest.fixture
def judge():
    return BedrockClaudeSonnetJudge()


def test_init_default_model(judge):
    assert judge.model_id == SONNET45_V1_MODEL_ID.format(AWS_REGION='us-east-1')


def test_init_custom_model(mocker):
    mocker.patch('boto3.session.Session').return_value.region_name = 'jj-east-1'
    custom_judge = BedrockClaudeSonnetJudge(model_id=SONNET45_V1_MODEL_ID)
    assert custom_judge.model_id == SONNET45_V1_MODEL_ID.format(AWS_REGION='jj-east-1')


def test_init_invalid_model(mocker):
    mock_logger = mocker.patch('simpleval.evaluation.judges.base_judge.logging.getLogger')
    judge = BedrockClaudeSonnetJudge(model_id='invalid_model')

    assert mock_logger.return_value.warning.call_count == 1
    warning_args = mock_logger.return_value.warning.call_args[0][0]
    assert 'invalid_model is not officially supported for bedrock_claude_sonnet' in warning_args
    assert judge.model_id == 'invalid_model'


def test_run_preliminary_checks_success(mocker, judge, monkeypatch):
    # Ensure API key env var is not set to test STS path
    monkeypatch.delenv(BEDROCK_API_KEY_ENV_VAR, raising=False)
    mocker.patch('boto3.session.Session').return_value.region_name = 'jj-east-1'
    mock_sts_client = mocker.Mock()
    mock_sts_client.get_caller_identity.return_value = {'UserId': 'test'}
    mocker.patch('boto3.client', return_value=mock_sts_client)

    judge.run_preliminary_checks()


def test_run_preliminary_checks_sts_failure(mocker, judge, monkeypatch):
    # Ensure API key env var is not set to test STS path
    monkeypatch.delenv(BEDROCK_API_KEY_ENV_VAR, raising=False)
    mocker.patch('boto3.session.Session').return_value.region_name = 'jj-east-1'
    mock_sts_client = mocker.Mock()
    mock_sts_client.get_caller_identity.side_effect = ClientError(
        {
            'Error': {
                'Code': 'InvalidClientTokenId',
                'Message': 'Invalid token',
            },
        },
        'GetCallerIdentity',
    )
    mocker.patch('boto3.client', return_value=mock_sts_client)

    with pytest.raises(RuntimeError):
        judge.run_preliminary_checks()


def test_run_preliminary_checks_region_failure(mocker, judge, monkeypatch):
    # Ensure API key env var is not set to test STS path
    monkeypatch.delenv(BEDROCK_API_KEY_ENV_VAR, raising=False)
    mocker.patch('boto3.session.Session').return_value.region_name = None

    with pytest.raises(RuntimeError):
        judge.run_preliminary_checks()


def test_run_preliminary_checks_api_key_success(mocker, judge, monkeypatch):
    # Set API key env var to test API key path
    monkeypatch.setenv(BEDROCK_API_KEY_ENV_VAR, 'test-api-key')
    mocker.patch('boto3.session.Session').return_value.region_name = 'jj-east-1'
    mock_bedrock = mocker.Mock()
    mock_bedrock.list_foundation_models.return_value = {'modelSummaries': []}
    
    def client_side_effect(service_name, **kwargs):
        if service_name == 'bedrock':
            return mock_bedrock
        return mocker.Mock()
    
    mocker.patch('boto3.client', side_effect=client_side_effect)

    judge.run_preliminary_checks()
    mock_bedrock.list_foundation_models.assert_called_once()


def test_model_inference_invalid_metric(judge):
    invalid_metric = MagicMock()
    with pytest.raises(TypeError):
        judge._model_inference('test prompt', invalid_metric)


def test_temperature_constant():
    assert BedrockClaudeSonnetJudge.TEMPERATURE == 0.0


def test_max_tokens_constant():
    assert BedrockClaudeSonnetJudge.MAX_TOKENS_TO_SAMPLE == 500


def test_call_claude_completion_success(mocker, judge):

    mock_bedrock_client = mocker.patch('boto3.client')
    mock_bedrock_instance = mock_bedrock_client.return_value
    mock_bedrock_instance.invoke_model.return_value.get.return_value.read.return_value = json.dumps({
        'usage': {
            'input_tokens': 10,
            'output_tokens': 20
        },
        'content': [{
            'text': 'response text'
        }]
    })

    result = judge.call_claude_completion(eval_prompt='test prompt', prefill='{')
    assert result == '{response text'
    mock_bedrock_instance.invoke_model.assert_called_once()


def test_get_claude_body_dict(judge):
    sys_prompt = 'test system prompt'
    prefill = '{'  # Example prefill
    body_dict = judge._BedrockClaudeSonnetJudge__get_claude_body_dict(sys_prompt=sys_prompt, prefill=prefill)

    assert body_dict['system'] == sys_prompt
    assert body_dict['temperature'] == judge.TEMPERATURE
    assert body_dict['max_tokens'] == judge.MAX_TOKENS_TO_SAMPLE
    assert body_dict['messages'][1]['content'][0]['text'] == f'[LLM As a judge] {prefill}'.strip()
