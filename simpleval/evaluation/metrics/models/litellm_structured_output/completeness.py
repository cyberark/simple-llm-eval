from typing import Callable, List, Literal, Type

from pydantic import BaseModel

from simpleval.evaluation.metrics.models.litellm_structured_output.base.base_metric import LiteLLMMetric
from simpleval.evaluation.metrics.parsers.output_parsing import litellm_structured_output_parser

COMPLETENESS_POSSIBLE_RESPONSES = ['Not at all', 'Not generally', 'Neutral/Mixed', 'Generally yes', 'Yes']


class CompletenessStructuredResponse(BaseModel):
    reasoning: str
    answer: Literal['Not at all', 'Not generally', 'Neutral/Mixed', 'Generally yes', 'Yes']


class CompletenessMetric(LiteLLMMetric):
    """
    Completeness - Measures if the model's response answers every question from the prompt.
    For this metric, if you supplied a ground response it is considered.
    Responses are graded on a 5-point Likert scale, and then normalized in the output and the job's report card.
    The {prompt} will contain the prompt sent to the generator from your dataset,
    and the {prediction} is the generator model's responses.
    The {ground_truth} is used when you supply a ground truth response in your prompt dataset.
    """

    def __init__(self):
        super().__init__()

    @property
    def eval_prompt(self) -> str:
        return """
You are a helpful agent that can assess LLM response according to the given rubrics.

					You are given a question, a candidate response from LLM and a reference response. Your task is to check if the candidate response contain the necessary amount of information and details for answering the question.

					When evaluating the completeness of the response, consider the following rubrics:

					1. Compare the candidate response and the reference response.
					- Identify any crucial information or key points that are present in the reference response but missing from the candidate response.
					- Focus on the main ideas and concepts that directly address the question, rather than minor details.
					- If a specific number of items or examples is requested, check that the candidate response provides the same number as the reference response.

					2. Does the candidate response provide sufficient detail and information for the task, compared to the reference response? For example,
					- For summaries, check if the main points covered in the candidate response match the core ideas in the reference response.
					- For step-by-step solutions or instructions, ensure that the candidate response doesn't miss any critical steps present in the reference response.
					- In customer service interactions, verify that all essential information provided in the reference response is also present in the candidate response.
					- For stories, emails, or other written tasks, ensure that the candidate response includes the key elements and main ideas as the reference response.
					- In rewriting or editing tasks, check that critical information has not been removed from the reference response.
					- For multiple-choice questions, if the reference response selects "all of the above" or a combination of options, the candidate response should do the same.

					3. Consider the implicit assumptions and requirements for the task, based on the reference response.
					- Different audiences or lengths may require different levels of detail in summaries, as demonstrated by the reference response. Focus on whether the candidate response meets the core requirements.

					Please rate the completeness of the candidate response based on the following scale:

					- Not at all: None of the necessary information and detail is present.
					- Not generally: Less than half of the necessary information and detail is present.
					- Neutral/Mixed: About half of the necessary information and detail is present, or it's unclear what the right amount of information is.
					- Generally yes: Most of the necessary information and detail is present.
					- Yes: All necessary information and detail is present.


					Here is the actual task:
					Question: {prompt}
					Reference response: {ground_truth}
					Candidate response: {prediction}

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
        return COMPLETENESS_POSSIBLE_RESPONSES

    @property
    def parser(self) -> Callable:
        """
        The parser that converts the model's output into a structured format.
        """
        return litellm_structured_output_parser

    @property
    def output_model(self) -> Type[BaseModel]:
        return CompletenessStructuredResponse
