

import pytest

from simpleval.evaluation.judges.base_judge import BaseJudge
from simpleval.evaluation.judges.models.anthropic.judge import AnthropicJudge
from simpleval.evaluation.judges.models.azure.judge import AzureJudge
from simpleval.evaluation.judges.models.bedrock_claude_sonnet.judge import BedrockClaudeSonnetJudge
from simpleval.evaluation.judges.models.gemini.judge import GeminiJudge
from simpleval.evaluation.judges.models.open_ai.judge import OpenAIJudge
from simpleval.evaluation.judges.models.vertex_ai.judge import VertexAIJudge

@pytext.mark.judgetest
@pytest.mark.parametrize('judge_type', [
    BedrockClaudeSonnetJudge,
    GeminiJudge,
    OpenAIJudge,
    AzureJudge,
    AnthropicJudge,
    VertexAIJudge,
])
def test_judges_minimal(setup, judge_type: BaseJudge):
    """
    Test minimal functionality of judges.
    """
    judge = judge_type()
    judge.


    