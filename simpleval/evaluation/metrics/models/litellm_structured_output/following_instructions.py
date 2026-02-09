from typing import Callable, List, Literal, Type

from pydantic import BaseModel

from simpleval.evaluation.metrics.models.litellm_structured_output.base.base_metric import LiteLLMMetric
from simpleval.evaluation.metrics.parsers.output_parsing import litellm_structured_output_parser
from simpleval.evaluation.metrics.prompts import get_json_schema_format_suffix
from simpleval.evaluation.metrics.prompts.following_instructions import CORE_PROMPT, POSSIBLE_RESPONSES

FOLLOWING_INSTRUCTIONS_POSSIBLE_RESPONSES = POSSIBLE_RESPONSES


class FollowingInstructionsStructuredResponse(BaseModel):
    reasoning: str
    answer: Literal['No', 'Not applicable', 'Yes']


class FollowingInstructionsMetric(LiteLLMMetric):
    """
    This metric evaluates whether the generator model's responses follow the exact directions found in the prompt.
    Responses are graded on a 3-point Likert scale, and then normalized in the output and the job's report card.
    The {prompt} will contain the prompt sent to the generator from your dataset, and the {prediction} is the generator model's response.
    """

    def __init__(self):
        super().__init__()

    @property
    def eval_prompt(self) -> str:
        return CORE_PROMPT + get_json_schema_format_suffix(POSSIBLE_RESPONSES)

    @property
    def possible_responses(self) -> List[str]:
        return POSSIBLE_RESPONSES

    @property
    def parser(self) -> Callable:
        """
        The parser that converts the model's output into a structured format.
        """
        return litellm_structured_output_parser

    @property
    def output_model(self) -> Type[BaseModel]:
        return FollowingInstructionsStructuredResponse
