from typing import Callable, List

from simpleval.evaluation.metrics.models.bedrock_claude_sonnet.base.base_metric import BaseBedrockSonnetMetric
from simpleval.evaluation.metrics.parsers.output_parsing import parse_explanation_answer_output
from simpleval.evaluation.metrics.prompts.helpfulness import CORE_PROMPT, POSSIBLE_RESPONSES


class HelpfulnessMetric(BaseBedrockSonnetMetric):
    """
    Helpfullness - Looks at how helpful the generator model's responses are in the context of several factors.
    These factors include X, Y, and Z. Responses are graded a 7-point lickert scale,
    and then normalized in the output and the job's report card.
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
above and beyond
very helpful
somewhat helpful
neither helpful nor unhelpful
somewhat unhelpful
very unhelpful
not helpful at all
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
