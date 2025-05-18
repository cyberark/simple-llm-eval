from typing import Callable, List, Literal, Type

from pydantic import BaseModel

from simpleval.evaluation.metrics.models.litellm_structured_output.base.base_metric import LiteLLMMetric
from simpleval.evaluation.metrics.parsers.output_parsing import litellm_structured_output_parser

FOLLOWING_INSTRUCTIONS_POSSIBLE_RESPONSES = ['No', 'Not applicable', 'Yes']


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
        return """
You are a helpful agent that can assess LLM response according to the given rubrics.

					You are given a question and a response from LLM. Your task is to determine whether the model's output respects all explicit parts of the instructions provided in the input, regardless of the overall quality or correctness of the response.

					The instructions provided in the input can be complex, containing specific, detailed parts. You can think of them as multiple constraints or requirements. Examples of explicit parts of instructions include:

					- Information that the model should use to answer the prompt (e.g., "Based on this text passage, give an overview about [...]")
					- Length of the output (e.g., "Summarize this text in one sentence")
					- Answer options (e.g., "Which of the following is the tallest mountain in Europe: K2, Mount Ararat, ...")
					- Target audience (e.g., "Write an explanation of value added tax for middle schoolers")
					- Genre (e.g., "Write an ad for a laundry service")
					- Style (e.g., "Write an ad for a sports car like it's an obituary.")
					- Type of content requested (e.g., "Write a body for this email based on the following subject line" vs "Write a subject line for this email")
					- And more...

					When evaluating, please limit yourself to considering only the explicit/visible parts of the instructions. The overall quality or correctness of the response is not relevant for this task. What matters is whether all parts of the instruction are addressed and generally respected.

					Additionally, keep in mind the following guidelines:

					- If the model gives a purely evasive response without even a partial answer or a related answer, rate this as "Yes" for following detailed instructions.
					- If the model gives a partially evasive response but does provide a partial answer or a related answer, then judge the partial answer as to whether it follows the detailed instructions.

					You should answer with one of the following options:

					- "Not applicable" if there are no explicit instructions in the input (i.e., the request is completely implicit, or there is no clear request).
					- "Yes" if all explicit requests in the input are satisfied in the output.
					- "No" if any of the explicit requests in the input are not satisfied in the output.


					Here is the actual task:
					Question: {prompt}
					Response: {prediction}

					The output should be a well-formatted JSON instance that conforms to the JSON schema below.

					As an example, for the schema {{"properties": {{"foo": {{"title": "Foo", "description": "a list of strings", "type": "array", "items": {{"type": "string"}}}}}}, "required": ["foo"]}}
					the object {{"foo": ["bar", "baz"]}} is a well-formatted instance of the schema. The object {{"properties": {{"foo": ["bar", "baz"]}}}} is not well-formatted.

					Here is the output JSON schema:
					```
					{{"properties": {{"reasoning": {{"description": "step by step reasoning to derive the final answer", "title": "Reasoning", "type": "string"}}, "answer": {{"description": "answer should be one of `Not applicable`, `No`, `Yes`", "enum": ["Not applicable", "No", "Yes"], "title": "Answer", "type": "string"}}}}, "required": ["reasoning", "answer"]}}
					```

					Do not return any preamble or explanations, return only a pure JSON string surrounded by triple backticks (```).
        """

    @property
    def possible_responses(self) -> List[str]:
        return FOLLOWING_INSTRUCTIONS_POSSIBLE_RESPONSES

    @property
    def parser(self) -> Callable:
        """
        The parser that converts the model's output into a structured format.
        """
        return litellm_structured_output_parser

    @property
    def output_model(self) -> Type[BaseModel]:
        return FollowingInstructionsStructuredResponse
