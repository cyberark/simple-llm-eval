from typing import Callable, List

from simpleval.evaluation.metrics.models.bedrock_claude_sonnet.base.base_metric import BaseBedrockSonnetMetric
from simpleval.evaluation.metrics.parsers.output_parsing import parse_explanation_answer_output


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
        return """
You are given a task in some context (Input), and a candidate answer. Is the candidate answer faithful to the task description and context?

					A response is unfaithful only when (1) it clearly contradicts the context, or (2) the task implies that the response must be based on the context, like in a summarization task. If the task does not ask to respond based on the context, the model is allowed to use its own knowledge to provide a response, even if its claims are not verifiable.

					Task: {prompt}

					Candidate Response: {prediction}

					Evaluate how much of the information in the answer is faithful to the available context.

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

    @property
    def possible_responses(self) -> List[str]:
        return ['none is faithful', 'some is faithful', 'approximately half is faithful', 'most is faithful', 'all is faithful']

    @property
    def parser(self) -> Callable:
        """
        The parser that converts the model's output into a structured format.
        """
        return parse_explanation_answer_output
