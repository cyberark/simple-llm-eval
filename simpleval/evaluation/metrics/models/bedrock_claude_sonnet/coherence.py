from typing import Callable, List

from simpleval.evaluation.metrics.models.bedrock_claude_sonnet.base.base_metric import BaseBedrockSonnetMetric
from simpleval.evaluation.metrics.parsers.xml_output_parsing import parse_xml_response
from simpleval.evaluation.metrics.prompts.coherence import CORE_PROMPT, POSSIBLE_RESPONSES


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
        xml_format_suffix = """
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
        return CORE_PROMPT + xml_format_suffix

    @property
    def possible_responses(self) -> List[str]:
        return POSSIBLE_RESPONSES

    @property
    def parser(self) -> Callable:
        """
        The parser that converts the model's output into a structured format.
        """
        return parse_xml_response
