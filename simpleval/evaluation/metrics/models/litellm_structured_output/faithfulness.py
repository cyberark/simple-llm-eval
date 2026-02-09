from typing import Callable, List, Literal, Type

from pydantic import BaseModel

from simpleval.evaluation.metrics.models.litellm_structured_output.base.base_metric import LiteLLMMetric
from simpleval.evaluation.metrics.parsers.output_parsing import litellm_structured_output_parser
from simpleval.evaluation.metrics.prompts import get_json_schema_format_suffix
from simpleval.evaluation.metrics.prompts.faithfulness import CORE_PROMPT, POSSIBLE_RESPONSES

FAITHFULNESS_POSSIBLE_RESPONSES = POSSIBLE_RESPONSES


class FaithfulnessStructuredResponse(BaseModel):
    reasoning: str
    answer: Literal['none is faithful', 'some is faithful', 'approximately half is faithful', 'most is faithful', 'all is faithful']


class FaithfulnessMetric(LiteLLMMetric):
    """
    This metric evaluates the completeness of a prediction based on the given prompt.
    It checks whether the prediction contains all necessary information that can be inferred from the prompt.
    The evaluation is done on a 5-point Likert scale and normalized in the output.
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
        return FaithfulnessStructuredResponse
