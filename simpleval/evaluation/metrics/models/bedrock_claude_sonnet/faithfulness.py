from typing import Callable, List

from simpleval.evaluation.metrics.models.bedrock_claude_sonnet.base.base_metric import BaseBedrockSonnetMetric
from simpleval.evaluation.metrics.parsers.output_parsing import parse_json_output
from simpleval.evaluation.metrics.prompts.core_prompts import (
    FAITHFULNESS_CORE_PROMPT,
    FAITHFULNESS_POSSIBLE_RESPONSES,
)
from simpleval.evaluation.metrics.prompts.format_instructions import get_json_format_instructions


class FaithfulnessMetric(BaseBedrockSonnetMetric):
    """
    This metric evaluates the completeness of a prediction based on the given prompt.
    It checks whether the prediction contains all necessary information that can be inferred from the prompt.
    The evaluation is done on a 5-point Likert scale and normalized in the output.
    """

    def __init__(self):
        super().__init__()

    @property
    def prefill(self) -> str:
        return '{"reasoning":'

    @property
    def eval_prompt(self) -> str:
        return FAITHFULNESS_CORE_PROMPT + get_json_format_instructions(FAITHFULNESS_POSSIBLE_RESPONSES)

    @property
    def possible_responses(self) -> List[str]:
        return FAITHFULNESS_POSSIBLE_RESPONSES

    @property
    def parser(self) -> Callable:
        """
        The parser that converts the model's output into a structured format.
        """
        return parse_json_output
