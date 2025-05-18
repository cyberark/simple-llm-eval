from unittest.mock import MagicMock, patch

import pytest
import tenacity
from litellm import Choices, Message, ModelResponse, Usage
from litellm.types.utils import PromptTokensDetailsWrapper

from simpleval.evaluation.judges.models.litellm_structured_output.judge import LiteLLMJudge
from simpleval.evaluation.metrics.models.litellm_structured_output.base.base_metric import LiteLLMMetric
from simpleval.evaluation.metrics.models.litellm_structured_output.coherence import CoherenceMetric, CoherenceStructuredResponse
from simpleval.utilities.retryables import LITELLM_LIMITS_EXCEPTIONS

LITELLM_COMPLETION_RESPONSE = ModelResponse(
    id='chatcmpl-b7abe601-ea23-4b93-8774-8a76484a30f9',
    created=1746386830,
    model='gemini-2.0-flash',
    object='chat.completion',
    system_fingerprint=None,
    choices=[
        Choices(
            finish_reason='stop',
            index=0,
            message=Message(
                content='{\n  "answer": "Not at all",\n  "reasoning": "The response consists of only the answer with no surrounding text. The answer also does not contain any punctuation or capitalization problems. The tone is strictly neutral."\n}',
                role='assistant',
                tool_calls=None,
                function_call=None,
                provider_specific_fields=None,
            ),
            logprobs=-0.912177105339206,
        )
    ],
    usage=Usage(
        completion_tokens=49,
        prompt_tokens=827,
        total_tokens=876,
        completion_tokens_details=None,
        prompt_tokens_details=PromptTokensDetailsWrapper(
            audio_tokens=None,
            cached_tokens=None,
            text_tokens=827,
            image_tokens=None,
        ),
    ),
    vertex_ai_grounding_metadata=[],
    vertex_ai_safety_results=[],
    vertex_ai_citation_metadata=[],
)


@pytest.fixture
def mock_metric():
    metric = MagicMock(spec=LiteLLMMetric)
    metric.name = 'mock_metric'
    metric.output_model = 'mock_output_model'
    return metric


@pytest.fixture
def judge():
    return LiteLLMJudge()


def test_init_default_model(judge):
    assert judge.model_id is not None


def test_run_preliminary_checks_invalid_model(judge):
    judge.model_id = None
    with pytest.raises(ValueError, match='Model ID is not set correctly'):
        judge.run_preliminary_checks()


def test_run_preliminary_checks_unsupported_model(judge):
    judge.model_id = 'unsupported_model'
    judge.model_supports_response_format = False
    judge.model_supports_json_schema = False
    with pytest.raises(ValueError, match='does not support structured output'):
        judge.run_preliminary_checks()


def test_model_inference_invalid_metric(judge):
    invalid_metric = MagicMock()
    with pytest.raises(TypeError, match='must be an instance of LiteLLMMetric'):
        judge._model_inference('test prompt', invalid_metric)


def test_model_inference_valid_metric(judge, mock_metric):
    with patch.object(judge, 'call_litellm_completion', return_value='mock_output') as mock_call:
        result = judge._model_inference('test prompt', mock_metric)
        assert result == 'mock_output'
        mock_call.assert_called_once_with(eval_prompt='test prompt', metric=mock_metric)


def test_call_litellm_completion_success(judge) -> None:
    with patch('litellm.completion', return_value=LITELLM_COMPLETION_RESPONSE) as mock_completion, \
         patch('simpleval.evaluation.judges.models.litellm_structured_output.judge.log_bookkeeping_data') as mock_log:

        metric = CoherenceMetric()
        output = judge.call_litellm_completion('test prompt', metric)
        assert isinstance(output, str)

        response = CoherenceStructuredResponse.model_validate_json(output)

        assert response.answer == 'Not at all'
        assert response.reasoning == 'The response consists of only the answer with no surrounding text. The answer also does not contain any punctuation or capitalization problems. The tone is strictly neutral.'
        mock_completion.assert_called_once()
        mock_log.assert_called_once_with(
            source='eval',
            model_name=judge.model_id,
            input_tokens=LITELLM_COMPLETION_RESPONSE.usage.prompt_tokens,
            output_tokens=LITELLM_COMPLETION_RESPONSE.usage.completion_tokens,
        )


def test_call_litellm_judge_eval_success(judge):
    with patch('litellm.completion', return_value=LITELLM_COMPLETION_RESPONSE) as mock_completion:
        metric = CoherenceMetric()
        metric_result = judge.evaluate(
            metric_name=metric.name,
            prompt='test prompt',
            prediction='test prediction',
            ground_truth='test ground truth',
        )
        assert metric_result.result == 'Not at all'
        assert metric_result.explanation == 'The response consists of only the answer with no surrounding text. The answer also does not contain any punctuation or capitalization problems. The tone is strictly neutral.'


@pytest.mark.skip(reason='Using actual retry time takes too long, try top mock with shorter time')
def test_call_litellm_completion_retryable_error(judge, mock_metric):
    # Create a fast retry decorator with minimal wait time and fewer attempts
    fast_retry = tenacity.retry(
        retry=tenacity.retry_if_exception_type(LITELLM_LIMITS_EXCEPTIONS),
        stop=tenacity.stop_after_attempt(2),  # Only retry once
        wait=tenacity.wait_fixed(0.1)  # Wait just 0.1 seconds between retries
    )

    with patch('simpleval.utilities.retryables.litellm_limits_retry', fast_retry), \
         patch('litellm.completion', side_effect=LITELLM_LIMITS_EXCEPTIONS[0](message='hi', model='di', llm_provider='ho')), \
         patch.object(judge.logger, 'error') as mock_error:
        with pytest.raises(tenacity.RetryError):
            judge.call_litellm_completion('test prompt', mock_metric)

        assert any('Call to LiteLLM completion ended with a retryable error' in arg for arg in mock_error.call_args[0])
