from typing import Callable, List

from simpleval.evaluation.metrics.models.bedrock_claude_sonnet.base.base_metric import BaseBedrockSonnetMetric
from simpleval.evaluation.metrics.parsers.output_parsing import parse_explanation_answer_output
from simpleval.evaluation.metrics.prompts.no_ground_truth_simple import CORE_PROMPT, POSSIBLE_RESPONSES


class NoGroundTruthSimpleMetric(BaseBedrockSonnetMetric):
    """
    When no ground truth is provided in the prompt dataset, the following prompt is used to evaluate the model's response.
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
					correct
					partially correct
					incorrect
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
