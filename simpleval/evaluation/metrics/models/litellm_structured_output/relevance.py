from typing import Callable, List, Literal, Type

from pydantic import BaseModel

from simpleval.evaluation.metrics.models.litellm_structured_output.base.base_metric import LiteLLMMetric
from simpleval.evaluation.metrics.parsers.output_parsing import litellm_structured_output_parser
from simpleval.evaluation.metrics.prompts.core_prompts import (
    RELEVANCE_CORE_PROMPT,
    RELEVANCE_POSSIBLE_RESPONSES,
)
from simpleval.evaluation.metrics.prompts.format_instructions import get_json_format_instructions


class RelevanceStructuredResponse(BaseModel):
    reasoning: str
    answer: Literal['not at all', 'slightly', 'somewhat', 'mostly', 'completely']


class RelevanceMetric(LiteLLMMetric):
    """
    Relevance - Looks at the model's responses and evaluates how relevant the answer is to question from the prompt.
    Responses are graded a 5-point lickert scale, and then normalized in the output and the job's report card.
    The {prompt} will contain the prompt sent to the generator from your dataset, and the {prediction} is the generator model's responses.
    """

    def __init__(self):
        super().__init__()

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
        return litellm_structured_output_parser

    @property
    def output_model(self) -> Type[BaseModel]:
        return RelevanceStructuredResponse
