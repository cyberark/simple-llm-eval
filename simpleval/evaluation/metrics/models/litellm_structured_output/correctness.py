from typing import Callable, List, Literal, Type

from pydantic import BaseModel

from simpleval.evaluation.metrics.models.litellm_structured_output.base.base_metric import LiteLLMMetric
from simpleval.evaluation.metrics.parsers.output_parsing import litellm_structured_output_parser

CORRECTNESS_POSSIBLE_RESPONSES = ['incorrect', 'partially correct', 'correct']


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
        return """
You are a helpful agent that can assess LLM response according to the given rubrics.

					You are given a question, a candidate response from LLM and a reference response. Your task is to check if the candidate response is correct or not.

					A correct candidate response should contain the same semantic information as the reference response.

					Here is the actual task:
					Question: {prompt}
					Reference Response: {ground_truth}
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
        return CORRECTNESS_POSSIBLE_RESPONSES

    @property
    def parser(self) -> Callable:
        """
        The parser that converts the model's output into a structured format.
        """
        return litellm_structured_output_parser

    @property
    def output_model(self) -> Type[BaseModel]:
        return CorrectnessStructuredResponse
