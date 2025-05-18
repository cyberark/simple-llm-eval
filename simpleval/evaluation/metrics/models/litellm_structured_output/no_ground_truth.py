from typing import Callable, List, Literal, Type

from pydantic import BaseModel

from simpleval.evaluation.metrics.models.litellm_structured_output.base.base_metric import LiteLLMMetric
from simpleval.evaluation.metrics.parsers.output_parsing import litellm_structured_output_parser

NO_GROUND_TRUTH_POSSIBLE_RESPONSES = ['Not at all', 'Not generally', 'Neutral/Mixed', 'Generally yes', 'Yes']


class NoGroundTruthStructuredResponse(BaseModel):
    reasoning: str
    answer: Literal['Not at all', 'Not generally', 'Neutral/Mixed', 'Generally yes', 'Yes']


class NoGroundTruthMetric(LiteLLMMetric):
    """
    When no ground truth is provided in the prompt dataset, the following prompt is used to evaluate the model's response.
    """

    def __init__(self):
        super().__init__()

    @property
    def eval_prompt(self) -> str:
        return """
You are an expert evaluator focusing specifically on assessing the completeness of responses.

					You will be presented with an Input (the original request/question) and an Output (the response to be evaluated). Your task is to determine whether an Output contains all the necessary information and detail to properly answer the Input.

					Rate the Output's completeness using only one of these five options:
					- Not at all: None of the necessary information/detail present; completely unusable
					- Not generally: Less than half of necessary information/detail present
					- Neutral/Mixed: About half of necessary information/detail present, or unclear
					- Generally yes: Most necessary information/detail present
					- Yes: All necessary information and detail present

					Key evaluation principles:
					1. Focus only on whether required information is present, not on:
					- Accuracy of information
					- Additional irrelevant information
					- Writing style or coherence

					2. Consider an Output incomplete if it:
					- Misses any explicitly requested items
					- Fails to address all parts of multi-part requests
					- Provides insufficient detail for the context
					- Misunderstands or ignores the Input

					3. For evasive responses:
					- If fully evasive ("I can't answer that"), rate as "Yes, completely"
					- If partially evasive with some information, evaluate the provided portion
					- If evasive when information was available, rate as incomplete

					4. For numbered requests (e.g., "list 10 items"):
					- Missing items lower the completeness rating
					- Exception: If Output explains why full count isn't possible

					Here is the actual task:
					Input: {prompt}
					Output: {prediction}

					The output should be a well-formatted JSON instance that conforms to the JSON schema below.

					As an example, for the schema {{"properties": {{"foo": {{"title": "Foo", "description": "a list of strings", "type": "array", "items": {{"type": "string"}}}}}}, "required": ["foo"]}}
					the object {{"foo": ["bar", "baz"]}} is a well-formatted instance of the schema. The object {{"properties": {{"foo": ["bar", "baz"]}}}} is not well-formatted.

					Here is the output JSON schema:
					```
					{{"properties": {{"reasoning": {{"description": "step by step reasoning to derive the final answer", "title": "Reasoning", "type": "string"}}, "answer": {{"description": "answer should be one of `Not at all`, `Not generally`, `Neutral/Mixed`, `Generally yes`, `Yes`", "enum": ["Not at all", "Not generally", "Neutral/Mixed", "Generally yes", "Yes"], "title": "Answer", "type": "string"}}}}, "required": ["reasoning", "answer"]}}
					```

					Do not return any preamble or explanations, return only a pure JSON string surrounded by triple backticks (```).
        """

    @property
    def possible_responses(self) -> List[str]:
        return NO_GROUND_TRUTH_POSSIBLE_RESPONSES

    @property
    def parser(self) -> Callable:
        """
        The parser that converts the model's output into a structured format.
        """
        return litellm_structured_output_parser

    @property
    def output_model(self) -> Type[BaseModel]:
        return NoGroundTruthStructuredResponse
