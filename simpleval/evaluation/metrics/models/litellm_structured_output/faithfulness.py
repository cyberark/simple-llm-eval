from typing import Callable, List, Literal, Type

from pydantic import BaseModel

from simpleval.evaluation.metrics.models.litellm_structured_output.base.base_metric import LiteLLMMetric
from simpleval.evaluation.metrics.parsers.output_parsing import litellm_structured_output_parser

FAITHFULNESS_POSSIBLE_RESPONSES = [
    'none is faithful',
    'some is faithful',
    'approximately half is faithful',
    'most is faithful',
    'all is faithful',
]


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
        return """
You are given a task in some context (Input), and a candidate answer. Is the candidate answer faithful to the task description and context?

A response is unfaithful only when (1) it clearly contradicts the context, or (2) the task implies that the response must be based on the context, like in a summarization task. If the task does not ask to respond based on the context, the model is allowed to use its own knowledge to provide a response, even if its claims are not verifiable.

Task: {prompt}

Candidate Response: {prediction}

Evaluate how much of the information in the answer is faithful to the available context.

The output should be a well-formatted JSON instance that conforms to the JSON schema below.

As an example, for the schema {{"properties": {{"foo": {{"title": "Foo", "description": "a list of strings", "type": "array", "items": {{"type": "string"}}}}}}, "required": ["foo"]}}
the object {{"foo": ["bar", "baz"]}} is a well-formatted instance of the schema. The object {{"properties": {{"foo": ["bar", "baz"]}}}} is not well-formatted.

Here is the output JSON schema:
```
{{"properties": {{"reasoning": {{"description": "step by step reasoning to derive the final answer", "title": "Reasoning", "type": "string"}}, "answer": {{"description": "answer should be one of `none is faithful`, `some is faithful`, `approximately half is faithful`, `most is faithful`, `all is faithful`", "enum": ["none is faithful", "some is faithful", "approximately half is faithful", "most is faithful", "all is faithful"], "title": "Answer", "type": "string"}}}}, "required": ["reasoning", "answer"]}}
```

Do not return any preamble or explanations, return only a pure JSON string surrounded by triple backticks (```).
        """

    @property
    def possible_responses(self) -> List[str]:
        return FAITHFULNESS_POSSIBLE_RESPONSES

    @property
    def parser(self) -> Callable:
        """
        The parser that converts the model's output into a structured format.
        """
        return litellm_structured_output_parser

    @property
    def output_model(self) -> Type[BaseModel]:
        return FaithfulnessStructuredResponse
