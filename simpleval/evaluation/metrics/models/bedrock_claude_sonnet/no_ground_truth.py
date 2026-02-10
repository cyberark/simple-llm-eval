from typing import Callable, List

from simpleval.evaluation.metrics.models.bedrock_claude_sonnet.base.base_metric import BaseBedrockSonnetMetric
from simpleval.evaluation.metrics.parsers.output_parsing import parse_json_output
from simpleval.evaluation.metrics.prompts.core_prompts import (
    NO_GROUND_TRUTH_CORE_PROMPT,
    NO_GROUND_TRUTH_POSSIBLE_RESPONSES,
)
from simpleval.evaluation.metrics.prompts.format_instructions import get_json_format_instructions


class NoGroundTruthMetric(BaseBedrockSonnetMetric):
    """
    When no ground truth is provided in the prompt dataset, the following prompt is used to evaluate the model's response.
    """

    def __init__(self):
        super().__init__()

    @property
    def prefill(self) -> str:
        return '{"reasoning":'

    @property
    def eval_prompt(self) -> str:
        return NO_GROUND_TRUTH_CORE_PROMPT + get_json_format_instructions(NO_GROUND_TRUTH_POSSIBLE_RESPONSES)

    @property
    def possible_responses(self) -> List[str]:
        return NO_GROUND_TRUTH_POSSIBLE_RESPONSES

    @property
    def parser(self) -> Callable:
        """
        The parser that converts the model's output into a structured format.
        """
        return parse_json_output
