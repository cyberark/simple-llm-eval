from typing import Callable, List, Literal, Type

from pydantic import BaseModel

from simpleval.evaluation.metrics.models.litellm_structured_output.base.base_metric import LiteLLMMetric
from simpleval.evaluation.metrics.parsers.output_parsing import litellm_structured_output_parser
from simpleval.evaluation.metrics.prompts import get_json_schema_format_suffix
from simpleval.evaluation.metrics.prompts.pro_style_and_tone import CORE_PROMPT, POSSIBLE_RESPONSES

PRO_STYLE_TONE_POSSIBLE_RESPONSES = POSSIBLE_RESPONSES


class ProStyleToneStructuredResponse(BaseModel):
    reasoning: str
    answer: Literal['not at all', 'not generally', 'neutral/mixed', 'generally yes', 'completely yes']


class ProStyleToneMetric(LiteLLMMetric):
    """
    Professional style and tone metric evaluates the appropriateness of the style, formatting,
    and tone of a response for professional genres.
    Responses are graded on a 5-point Likert scale, then normalized in the output and the job's report card.
    The {prompt} contains the prompt sent to the generator from your dataset, and the {prediction} is the generator model's response.
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
        return ProStyleToneStructuredResponse
