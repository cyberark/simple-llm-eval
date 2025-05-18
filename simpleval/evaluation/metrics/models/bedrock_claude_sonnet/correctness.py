from typing import Callable, List

from simpleval.evaluation.metrics.models.bedrock_claude_sonnet.base.base_metric import BaseBedrockSonnetMetric
from simpleval.evaluation.metrics.parsers.output_parsing import parse_explanation_answer_output


class CorrectnessMetric(BaseBedrockSonnetMetric):
    """
    Correctness - Measures if the model's response is correct. For this metric, if you supplied a ground truth response, it is considered.
    Responses are graded a 3-point lickert scale, and then normalized in the output and the job's report card.
    The {prompt} will contain the prompt sent to the generator from your dataset, and the {prediction} is the generator model's responses.
    The {ground_truth} is used when you supply a ground truth response in your prompt dataset.
    """

    def __init__(self):
        super().__init__()

    @property
    def prefill(self) -> str:
        return 'Explanation:'

    @property
    def eval_prompt(self) -> str:
        return """
You are a helpful agent that can assess LLM response according to the given rubrics.

					You are given a question, a candidate response from LLM and a reference response. Your task is to check if the candidate response is correct or not.

					A correct candidate response should contain the same semantic information as the reference response.

					Here is the actual task:
					Question: {prompt}
					Reference Response: {ground_truth}
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
