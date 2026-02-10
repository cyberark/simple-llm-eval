from typing import Callable, List

from simpleval.evaluation.metrics.models.bedrock_claude_sonnet.base.base_metric import BaseBedrockSonnetMetric
from simpleval.evaluation.metrics.parsers.output_parsing import parse_json_output
from simpleval.evaluation.metrics.prompts.core_prompts import (
    COMPLETENESS_CORE_PROMPT,
    COMPLETENESS_POSSIBLE_RESPONSES,
)
from simpleval.evaluation.metrics.prompts.format_instructions import get_json_format_instructions


class CompletenessMetric(BaseBedrockSonnetMetric):
    """
    Completeness - Measures if the model's response answers every question from the prompt.
    For this metric, if you supplied a ground response it is considered.
    Responses are graded on a 5-point Likert scale, and then normalized in the output and the job's report card.
    The {prompt} will contain the prompt sent to the generator from your dataset,
    and the {prediction} is the generator model's responses.
    The {ground_truth} is used when you supply a ground truth response in your prompt dataset.
    """

    def __init__(self):
        super().__init__()

    @property
    def prefill(self) -> str:
        return '{"reasoning":'

    @property
    def eval_prompt(self) -> str:
        return COMPLETENESS_CORE_PROMPT + get_json_format_instructions(COMPLETENESS_POSSIBLE_RESPONSES)

    @property
    def possible_responses(self) -> List[str]:
        return COMPLETENESS_POSSIBLE_RESPONSES

    @property
    def parser(self) -> Callable:
        """
        The parser that converts the model's output into a structured format.
        """
        return parse_json_output
