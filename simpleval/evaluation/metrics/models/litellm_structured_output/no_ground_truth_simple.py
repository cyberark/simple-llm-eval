from typing import Callable, List, Literal, Type

from pydantic import BaseModel

from simpleval.evaluation.metrics.models.litellm_structured_output.base.base_metric import LiteLLMMetric
from simpleval.evaluation.metrics.parsers.output_parsing import litellm_structured_output_parser
from simpleval.evaluation.metrics.prompts.core_prompts import (
    NO_GROUND_TRUTH_SIMPLE_CORE_PROMPT,
    NO_GROUND_TRUTH_SIMPLE_POSSIBLE_RESPONSES,
)
from simpleval.evaluation.metrics.prompts.format_instructions import get_json_format_instructions


class NoGroundTruthSimpleStructuredResponse(BaseModel):
    reasoning: str
    answer: Literal['incorrect', 'partially correct', 'correct']


class NoGroundTruthSimpleMetric(LiteLLMMetric):
    """
    When no ground truth is provided in the prompt dataset, the following prompt is used to evaluate the model's response.
    """

    def __init__(self):
        super().__init__()

    @property
    def eval_prompt(self) -> str:
        return NO_GROUND_TRUTH_SIMPLE_CORE_PROMPT + get_json_format_instructions(NO_GROUND_TRUTH_SIMPLE_POSSIBLE_RESPONSES)

    @property
    def possible_responses(self) -> List[str]:
        return NO_GROUND_TRUTH_SIMPLE_POSSIBLE_RESPONSES

    @property
    def parser(self) -> Callable:
        """
        The parser that converts the model's output into a structured format.
        """
        return litellm_structured_output_parser

    @property
    def output_model(self) -> Type[BaseModel]:
        return NoGroundTruthSimpleStructuredResponse
