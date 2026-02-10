from typing import Callable, List

from simpleval.evaluation.metrics.models.bedrock_claude_sonnet.base.base_metric import BaseBedrockSonnetMetric
from simpleval.evaluation.metrics.parsers.output_parsing import parse_json_output
from simpleval.evaluation.metrics.prompts.core_prompts import (
    RELEVANCE_CORE_PROMPT,
    RELEVANCE_POSSIBLE_RESPONSES,
)
from simpleval.evaluation.metrics.prompts.format_instructions import get_json_format_instructions


class RelevanceMetric(BaseBedrockSonnetMetric):
    """
    Relevance - Looks at the model's responses and evaluates how relevant the answer is to question from the prompt.
    Responses are graded a 5-point lickert scale, and then normalized in the output and the job's report card.
    The {prompt} will contain the prompt sent to the generator from your dataset, and the {prediction} is the generator model's responses.
    """

    def __init__(self):
        super().__init__()

    @property
    def prefill(self) -> str:
        return '{"reasoning":'

    @property
    def eval_prompt(self) -> str:
        return RELEVANCE_CORE_PROMPT + get_json_format_instructions(RELEVANCE_POSSIBLE_RESPONSES)

    @property
    def possible_responses(self) -> List[str]:
        return RELEVANCE_POSSIBLE_RESPONSES

    @property
    def parser(self) -> Callable:
        """
        The parser that converts the model's output into a structured format.
        """
        return parse_json_output
