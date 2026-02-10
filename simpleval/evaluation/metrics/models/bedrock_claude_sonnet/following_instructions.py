from typing import Callable, List

from simpleval.evaluation.metrics.models.bedrock_claude_sonnet.base.base_metric import BaseBedrockSonnetMetric
from simpleval.evaluation.metrics.parsers.output_parsing import parse_json_output
from simpleval.evaluation.metrics.prompts.core_prompts import (
    FOLLOWING_INSTRUCTIONS_CORE_PROMPT,
    FOLLOWING_INSTRUCTIONS_POSSIBLE_RESPONSES,
)
from simpleval.evaluation.metrics.prompts.format_instructions import get_json_format_instructions


class FollowingInstructionsMetric(BaseBedrockSonnetMetric):
    """
    This metric evaluates whether the generator model's responses follow the exact directions found in the prompt.
    Responses are graded on a 3-point Likert scale, and then normalized in the output and the job's report card.
    The {prompt} will contain the prompt sent to the generator from your dataset, and the {prediction} is the generator model's response.
    """

    def __init__(self):
        super().__init__()

    @property
    def prefill(self) -> str:
        return '{"reasoning":'

    @property
    def eval_prompt(self) -> str:
        return FOLLOWING_INSTRUCTIONS_CORE_PROMPT + get_json_format_instructions(FOLLOWING_INSTRUCTIONS_POSSIBLE_RESPONSES)

    @property
    def possible_responses(self) -> List[str]:
        return FOLLOWING_INSTRUCTIONS_POSSIBLE_RESPONSES

    @property
    def parser(self) -> Callable:
        """
        The parser that converts the model's output into a structured format.
        """
        return parse_json_output
