from typing import Callable, List

from simpleval.evaluation.metrics.models.bedrock_claude_sonnet.base.base_metric import BaseBedrockSonnetMetric
from simpleval.evaluation.metrics.parsers.output_parsing import parse_explanation_answer_output


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
        return """
You are given a task and a candidate response. Is this a correct and accurate response to the task?

					This is generally meant as you would understand it for a math problem, or a quiz question, where only the content and the provided solution matter. Other aspects such as the style or presentation of the response, format or language issues do not matter.

					Task: {prompt}
					Candidate Response: {prediction}

					Firstly explain your response, followed by your final answer. You should follow the format
					Explanation: [Explanation], Answer: [Answer],
					where '[Answer]' can be one of the following:
					```
					correct
					partially correct
					incorrect
					```
        """

    @property
    def possible_responses(self) -> List[str]:
        return ['incorrect', 'partially correct', 'correct']

    @property
    def parser(self) -> Callable:
        """
        The parser that converts the model's output into a structured format.
        """
        return parse_explanation_answer_output
