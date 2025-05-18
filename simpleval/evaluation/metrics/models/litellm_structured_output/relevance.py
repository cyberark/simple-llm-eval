from typing import Callable, List, Literal, Type

from pydantic import BaseModel

from simpleval.evaluation.metrics.models.litellm_structured_output.base.base_metric import LiteLLMMetric
from simpleval.evaluation.metrics.parsers.output_parsing import litellm_structured_output_parser

RELEVANCE_POSSIBLE_RESPONSES = ['not at all', 'slightly', 'somewhat', 'mostly', 'completely']


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
        return """
You are a helpful agent that can assess LLM response according to the given rubrics.

You are given a question and a response from LLM. Your task is to assess the relevance of the LLM response to the question, in other words, how focused the LLM response is on the given question.

The output saying "I don't know" or "I can't answer" is relevant. Telling the user that the model is unable to respond to their query, or adding a simple caveat or condition to the response, should be considered relevant. However, the model may say "I don't know" and go on to say something irrelevant. In such a case, relevance should be penalized.

Please rate the relevance of the response based on the following scale:
- not at all: No part of the response is relevant to the question.
- slightly: An overwhelming amount of the response is irrelevant or the relevant information is not a direct answer.
- somewhat: Roughly half of the response is relevant to the question.
- mostly: An overwhelming amount of the response is relevant to the question.
- completely: Every piece of the response is relevant to the question.

Here is the actual task:
Question: {prompt}
Response: {prediction}

The output should be a well-formatted JSON instance that conforms to the JSON schema below.

As an example, for the schema {{"properties": {{"foo": {{"title": "Foo", "description": "a list of strings", "type": "array", "items": {{"type": "string"}}}}}}, "required": ["foo"]}}
the object {{"foo": ["bar", "baz"]}} is a well-formatted instance of the schema. The object {{"properties": {{"foo": ["bar", "baz"]}}}} is not well-formatted.

Here is the output JSON schema:
```
{{"properties": {{"reasoning": {{"description": "step by step reasoning to derive the final answer", "title": "Reasoning", "type": "string"}}, "answer": {{"description": "answer should be one of `not at all`, `slightly`, `somewhat`, `mostly`, `completely`", "enum": ["not at all", "slightly", "somewhat", "mostly", "completely"], "title": "Answer", "type": "string"}}}}, "required": ["reasoning", "answer"]}}
```

Do not return any preamble or explanations, return only a pure JSON string surrounded by triple backticks (```).
        """

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
