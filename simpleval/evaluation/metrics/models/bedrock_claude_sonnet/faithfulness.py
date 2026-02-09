from typing import Callable, List

from simpleval.evaluation.metrics.models.bedrock_claude_sonnet.base.base_metric import BaseBedrockSonnetMetric
from simpleval.evaluation.metrics.parsers.output_parsing import parse_explanation_answer_output
from simpleval.evaluation.metrics.prompts.faithfulness import CORE_PROMPT, POSSIBLE_RESPONSES


class FaithfulnessMetric(BaseBedrockSonnetMetric):
    """
    This metric evaluates the completeness of a prediction based on the given prompt.
    It checks whether the prediction contains all necessary information that can be inferred from the prompt.
    The evaluation is done on a 5-point Likert scale and normalized in the output.
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
					none is faithful
					some is faithful
					approximately half is faithful
					most is faithful
					all is faithful
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
