from typing import Callable, List

from simpleval.evaluation.metrics.models.bedrock_claude_sonnet.base.base_metric import BaseBedrockSonnetMetric
from simpleval.evaluation.metrics.parsers.output_parsing import parse_explanation_answer_output
from simpleval.evaluation.metrics.prompts.readability import CORE_PROMPT, POSSIBLE_RESPONSES


class ReadabilityMetric(BaseBedrockSonnetMetric):
    """
    Readability - Looks at the model's responses and evaluates the terminological and linguistic complexity of the response.
    Responses are graded a 5-point lickert scale, and then normalized in the output and the job's report card.
    The {prompt} will contain the prompt sent to the generator from your dataset, and the {prediction} is the generator model's responses.
    """

    def __init__(self):
        super().__init__()

    @property
    def prefill(self) -> str:
        return 'Explanation:'

    @property
    def eval_prompt(self) -> str:
        plain_text_format_suffix = """
Firstly explain your response, followed by your final answer. You should follow the format
Explanation: [Explanation], Answer: [Answer],
where '[Answer]' can be one of the following:
```
unreadable
poor readability
fair readability
good readability
excellent readability
```
        """
        return CORE_PROMPT + plain_text_format_suffix

    @property
    def possible_responses(self) -> List[str]:
        return POSSIBLE_RESPONSES

    @property
    def parser(self) -> Callable:
        """
        The parser that converts the model's output into a structured format.
        """
        return parse_explanation_answer_output
