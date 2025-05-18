from typing import Callable, List

from simpleval.evaluation.metrics.models.bedrock_claude_sonnet.base.base_metric import BaseBedrockSonnetMetric
from simpleval.evaluation.metrics.parsers.xml_output_parsing import parse_xml_response


class CoherenceMetric(BaseBedrockSonnetMetric):
    """
    Coherence - Looks logical gaps, inconsistencies, and contradictions in a model's responses to a prompt.
    Responses are graded a 5-point lickert scale, and then normalized in the output and the job's report card.
    The {prompt} will contain the prompt sent to the generator from your dataset, and the {prediction} is the generator model's responses.
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

        You are given a question and a response from LLM. Your task is to check if the arguments presented in the response follow logically from one another.

        When evaluating the logical cohesion of the response, consider the following rubrics:

        1. Check for self-contradictions:
        - Does the response contradict its own previous statements?
        - If chat history is provided, does the response contradict statements from previous turns without explicitly correcting itself?

        2. Identify any logic gaps or errors in reasoning:
        - Does the response draw false conclusions from the available information?
        - Does it make "logical leaps" by skipping steps in an argument?
        - Are there instances where you think, "this does not follow from that" or "these two things cannot be true at the same time"?

        3. Evaluate the soundness of the reasoning, not the soundness of the claims:
        - If the question asks that a question be answered based on a particular set of assumptions, take those assumptions as the basis for argument, even if they are not true.
        - Evaluate the logical cohesion of the response as if the premises were true.

        4. Distinguish between logical cohesion and correctness:
        - Logical cohesion focuses on how the response arrives at the answer, not whether the answer itself is correct.
        - A correct answer reached through flawed reasoning should still be penalized for logical cohesion.

        5. Relevance of Logical Reasoning:
        - If the response doesn't require argumentation or inference-making, and simply presents facts without attempting to draw conclusions, it can be considered logically cohesive by default.
        - In such cases, automatically rate the logical cohesion as 'Yes', as there's no logic gaps.

        Please rate the logical cohesion of the response based on the following scale:

        - Not at all: The response contains too many errors of reasoning to be usable, such as contradicting itself, major gaps in reasoning, or failing to present any reasoning where it is required.
        - Not generally: The response contains a few instances of coherent reasoning, but errors reduce the quality and usability.
        - Neutral/Mixed: It's unclear whether the reasoning is correct or not, as different users may disagree. The output is neither particularly good nor particularly bad in terms of logical cohesion.
        - Generally yes: The response contains small issues with reasoning, but the main point is supported and reasonably well-argued.
        - Yes: There are no issues with logical cohesion at all. The output does not contradict itself, and all reasoning is sound.


        Here is the actual task:
        Question: {prompt}
        Response: {prediction}

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
