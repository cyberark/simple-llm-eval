from typing import Callable, List

from simpleval.evaluation.metrics.models.bedrock_claude_sonnet.base.base_metric import BaseBedrockSonnetMetric
from simpleval.evaluation.metrics.parsers.output_parsing import parse_json_output
from simpleval.evaluation.metrics.prompts.core_prompts import (
    HELPFULNESS_CORE_PROMPT,
    HELPFULNESS_POSSIBLE_RESPONSES,
)
from simpleval.evaluation.metrics.prompts.format_instructions import get_json_format_instructions


class HelpfulnessMetric(BaseBedrockSonnetMetric):
    """
    Helpfullness - Looks at how helpful the generator model's responses are in the context of several factors.
    These factors include X, Y, and Z. Responses are graded a 7-point lickert scale,
    and then normalized in the output and the job's report card.
    The {prompt} will contain the prompt sent to the generator from your dataset, and the {prediction} is the generator model's responses.
    """

    def __init__(self):
        super().__init__()

    @property
    def prefill(self) -> str:
        return '{"reasoning":'

    @property
    def eval_prompt(self) -> str:
        return HELPFULNESS_CORE_PROMPT + get_json_format_instructions(HELPFULNESS_POSSIBLE_RESPONSES)

    @property
    def possible_responses(self) -> List[str]:
        return HELPFULNESS_POSSIBLE_RESPONSES

    @property
    def parser(self) -> Callable:
        """
        The parser that converts the model's output into a structured format.
        """
        return parse_json_output
