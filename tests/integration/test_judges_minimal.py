import os
import pytest

from simpleval.evaluation.judges.models.anthropic.judge import AnthropicJudge
from simpleval.evaluation.judges.models.azure.judge import AzureJudge
from simpleval.evaluation.judges.models.bedrock_claude_sonnet.judge import BedrockClaudeSonnetJudge
from simpleval.evaluation.judges.models.gemini.judge import GeminiJudge
from simpleval.evaluation.judges.models.open_ai.judge import OpenAIJudge
from simpleval.evaluation.judges.models.vertex_ai.judge import VertexAIJudge

RUN_ALL_MINIMAL_JUDGE_TESTS = 'RUN_ALL_MINIMAL_JUDGE_TESTS'
RUN_BEDROCK_SONNET_MINIMAL_TEST = 'RUN_BEDROCK_SONNET_MINIMAL_TEST'
RUN_GEMINI_MINIMAL_TEST = 'RUN_GEMINI_MINIMAL_TEST'
RUN_OPENAI_MINIMAL_TEST = 'RUN_OPENAI_MINIMAL_TEST'
RUN_AZURE_MINIMAL_TEST = 'RUN_AZURE_MINIMAL_TEST'
RUN_ANTHROPIC_MINIMAL_ENV = 'RUN_ANTHROPIC_MINIMAL_TEST'
RUN_VERTEX_AI_MINIMAL_ENV = 'RUN_VERTEX_AI_MINIMAL_TEST'


def env_var_on(var_name: str) -> bool:
    return os.environ.get(var_name) == '1'


@pytest.mark.skipif(
    not env_var_on(RUN_BEDROCK_SONNET_MINIMAL_TEST) and not env_var_on(RUN_ALL_MINIMAL_JUDGE_TESTS),
    reason='To run this, set relevant env var to "1"',
)
def test_bedrock_sonnet_minimal():
    """
    Test minimal functionality of judges.
    """
    judge = BedrockClaudeSonnetJudge()
    metrics = judge.list_metrics()
    result = judge.evaluate(metric_name=metrics[0], prompt='say something nice', prediction='have a nice day')
    assert result


@pytest.mark.skipif(
    not env_var_on(RUN_GEMINI_MINIMAL_TEST) and not env_var_on(RUN_ALL_MINIMAL_JUDGE_TESTS),
    reason='To run this, set relevant env var to "1"',
)
def test_gemini_minimal():
    """
    Test minimal functionality of Gemini judge.
    """
    judge = GeminiJudge()
    metrics = judge.list_metrics()
    result = judge.evaluate(metric_name=metrics[0], prompt='say something nice', prediction='have a nice day')
    assert result


@pytest.mark.skipif(
    not env_var_on(RUN_OPENAI_MINIMAL_TEST) and not env_var_on(RUN_ALL_MINIMAL_JUDGE_TESTS),
    reason='To run this, set relevant env var to "1"',
)
def test_openai_minimal():
    """
    Test minimal functionality of OpenAI judge.
    """
    judge = OpenAIJudge()
    metrics = judge.list_metrics()
    result = judge.evaluate(metric_name=metrics[0], prompt='say something nice', prediction='have a nice day')
    assert result


@pytest.mark.skipif(
    not env_var_on(RUN_AZURE_MINIMAL_TEST) and not env_var_on(RUN_ALL_MINIMAL_JUDGE_TESTS),
    reason='To run this, set relevant env var to "1"',
)
def test_azure_minimal():
    """
    Test minimal functionality of Azure judge.
    """
    judge = AzureJudge()
    metrics = judge.list_metrics()
    result = judge.evaluate(metric_name=metrics[0], prompt='say something nice', prediction='have a nice day')
    assert result


@pytest.mark.skipif(
    not env_var_on(RUN_ANTHROPIC_MINIMAL_ENV) and not env_var_on(RUN_ALL_MINIMAL_JUDGE_TESTS),
    reason='To run this, set relevant env var to "1"',
)
def test_anthropic_minimal():
    """
    Test minimal functionality of Anthropic judge.
    """
    judge = AnthropicJudge()
    metrics = judge.list_metrics()
    result = judge.evaluate(metric_name=metrics[0], prompt='say something nice', prediction='have a nice day')
    assert result


@pytest.mark.skipif(
    not env_var_on(RUN_VERTEX_AI_MINIMAL_ENV) and not env_var_on(RUN_ALL_MINIMAL_JUDGE_TESTS),
    reason='To run this, set relevant env var to "1"',
)
def test_vertex_ai_minimal():
    """
    Test minimal functionality of Vertex AI judge.
    """
    judge = VertexAIJudge()
    metrics = judge.list_metrics()
    result = judge.evaluate(metric_name=metrics[0], prompt='say something nice', prediction='have a nice day')
    assert result
