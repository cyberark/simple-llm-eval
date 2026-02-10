from typing import Callable, List, Literal, Type

from pydantic import BaseModel

from simpleval.evaluation.metrics.models.litellm_structured_output.base.base_metric import LiteLLMMetric
from simpleval.evaluation.metrics.parsers.output_parsing import litellm_structured_output_parser
from simpleval.evaluation.metrics.prompts.core_prompts import (
    READABILITY_CORE_PROMPT,
    READABILITY_POSSIBLE_RESPONSES,
)
from simpleval.evaluation.metrics.prompts.format_instructions import get_json_format_instructions


class ReadabilityStructuredResponse(BaseModel):
    reasoning: str
    answer: Literal['unreadable', 'poor readability', 'fair readability', 'good readability', 'excellent readability']


class ReadabilityMetric(LiteLLMMetric):
    """
    Readability - Looks at the model's responses and evaluates the terminological and linguistic complexity of the response.
    Responses are graded a 5-point lickert scale, and then normalized in the output and the job's report card.
    The {prompt} will contain the prompt sent to the generator from your dataset, and the {prediction} is the generator model's responses.
    """

    def __init__(self):
        super().__init__()

    @property
    def eval_prompt(self) -> str:
        return READABILITY_CORE_PROMPT + get_json_format_instructions(READABILITY_POSSIBLE_RESPONSES)

    @property
    def possible_responses(self) -> List[str]:
        return READABILITY_POSSIBLE_RESPONSES

    @property
    def parser(self) -> Callable:
        """
        The parser that converts the model's output into a structured format.
        """
        return litellm_structured_output_parser

    @property
    def output_model(self) -> Type[BaseModel]:
        return ReadabilityStructuredResponse
