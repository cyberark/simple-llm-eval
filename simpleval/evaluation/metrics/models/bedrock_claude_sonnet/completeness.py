from typing import Callable, List

from simpleval.evaluation.metrics.models.bedrock_claude_sonnet.base.base_metric import BaseBedrockSonnetMetric
from simpleval.evaluation.metrics.parsers.xml_output_parsing import parse_xml_response


class CompletenessMetric(BaseBedrockSonnetMetric):
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
    def prefill(self) -> str:
        return '<response>'

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

					The output should be formatted as a XML file.
					1. Output should conform to the tags below.
					2. Remember to always open and close all the tags.
					3. Do not invent new tags.

					As an example, for the tags ["foo", "bar", "baz"]:
					1. String "<foo>
					<bar>
					<baz></baz>
					</bar>
					</foo>" is a well-formatted instance of the schema.
					2. String "<foo>
					<bar>
					</foo>" is a badly-formatted instance.
					3. String "<foo>
					<tag>
					</tag>
					</foo>" is a badly-formatted instance.

					Here are the output tags with description:
					```
					<response>
					<reasonings>step by step reasoning to derive the final answer</reasonings>
					<answer>answer should be one of `Not at all`, `Not generally`, `Neutral/Mixed`, `Generally yes`, `Yes`</answer>
					</response>
					```

					Do not return any preamble or explanations, return only a pure XML string surrounded by triple backticks (```).
        """

    @property
    def possible_responses(self) -> List[str]:
        return ['Not at all', 'Not generally', 'Neutral/Mixed', 'Generally yes', 'Yes']

    @property
    def parser(self) -> Callable:
        """
        The parser that converts the model's output into a structured format.
        """
        return parse_xml_response
