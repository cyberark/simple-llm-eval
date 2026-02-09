from typing import Callable, List, Literal, Type

from pydantic import BaseModel

from simpleval.evaluation.metrics.models.litellm_structured_output.base.base_metric import LiteLLMMetric
from simpleval.evaluation.metrics.parsers.output_parsing import litellm_structured_output_parser
from simpleval.evaluation.metrics.prompts import get_json_schema_format_suffix
from simpleval.evaluation.metrics.prompts.correctness import CORE_PROMPT, POSSIBLE_RESPONSES

CORRECTNESS_POSSIBLE_RESPONSES = POSSIBLE_RESPONSES


class CorrectnessStructuredResponse(BaseModel):
    reasoning: str
    answer: Literal['incorrect', 'partially correct', 'correct']


class CorrectnessMetric(LiteLLMMetric):
    """
    Correctness - Measures if the model's response is correct. For this metric, if you supplied a ground truth response, it is considered.
    Responses are graded a 3-point lickert scale, and then normalized in the output and the job's report card.
    The {prompt} will contain the prompt sent to the generator from your dataset, and the {prediction} is the generator model's responses.
    The {ground_truth} is used when you supply a ground truth response in your prompt dataset.
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
        return CorrectnessStructuredResponse
