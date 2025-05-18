from typing import Callable, List, Literal, Type

from pydantic import BaseModel

from simpleval.evaluation.metrics.models.litellm_structured_output.base.base_metric import LiteLLMMetric
from simpleval.evaluation.metrics.parsers.output_parsing import litellm_structured_output_parser

NO_GROUND_TRUTH_SIMPLE_POSSIBLE_RESPONSES = ['incorrect', 'partially correct', 'correct']


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
        return """
You are given a task and a candidate response. Is this a correct and accurate response to the task?

					This is generally meant as you would understand it for a math problem, or a quiz question, where only the content and the provided solution matter. Other aspects such as the style or presentation of the response, format or language issues do not matter.

					Task: {prompt}
					Candidate Response: {prediction}

					The output should be a well-formatted JSON instance that conforms to the JSON schema below.

					As an example, for the schema {{"properties": {{"foo": {{"title": "Foo", "description": "a list of strings", "type": "array", "items": {{"type": "string"}}}}}}, "required": ["foo"]}}
					the object {{"foo": ["bar", "baz"]}} is a well-formatted instance of the schema. The object {{"properties": {{"foo": ["bar", "baz"]}}}} is not well-formatted.

					Here is the output JSON schema:
					```
					{{"properties": {{"reasoning": {{"description": "step by step reasoning to derive the final answer", "title": "Reasoning", "type": "string"}}, "answer": {{"description": "answer should be one of `incorrect`, `partially correct`, `correct`", "enum": ["incorrect", "partially correct", "correct"], "title": "Answer", "type": "string"}}}}, "required": ["reasoning", "answer"]}}
					```

					Do not return any preamble or explanations, return only a pure JSON string surrounded by triple backticks (```).
        """

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
