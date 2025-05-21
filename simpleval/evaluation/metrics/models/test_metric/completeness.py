from typing import Callable, List

from simpleval.evaluation.metrics.base_metric import EvaluationMetric
from simpleval.evaluation.metrics.parsers.output_parsing import parse_explanation_answer_output


class CompletenessMetric(EvaluationMetric):
    def __init__(self):
        super().__init__()

    @property
    def eval_prompt(self) -> str:
        return (
            'Evaluate whether the prediction: "{prediction}" is complete with respect to the prompt: "{prompt}". '
            'Rate on a scale of 1 to 10, where 1 is very incomplete and 10 is fully complete. '
            'Explain your reasoning.'
        )

    @property
    def possible_responses(self) -> List[str]:
        return [str(i) for i in range(1, 11)]

    @property
    def parser(self) -> Callable:
        """
        The parser that converts the model's output into a structured format.
        """
        return parse_explanation_answer_output
