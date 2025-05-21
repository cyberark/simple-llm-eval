import random
from typing import Set

from simpleval.evaluation.judges.base_judge import BaseJudge
from simpleval.evaluation.metrics.base_metric import EvaluationMetric


class DummyJudge(BaseJudge):
    """
    Concrete Judge for testing purposes. Does not call any actual llm.
    """

    DEFAULT_MODEL_ID = 'default_test_model_id'

    def __init__(self, model_id: str = None):
        model_id = model_id or self.DEFAULT_MODEL_ID
        super().__init__(model_id=model_id, supported_model_ids=[self.DEFAULT_MODEL_ID, 'test_model_id_2'])

    @property
    def _metrics_model(self) -> Set[str]:
        return 'test_metric'

    def run_preliminary_checks(self):
        """
        Run any preliminary checks before the evaluation starts.
        """

    def preliminary_checks_explanation(self) -> str:
        return 'No preliminary checks needed for DummyJudge.'

    def _model_inference(self, eval_prompt: str, metric: EvaluationMetric) -> str:
        """
        Dummy inference method for testing purposes.
        """

        answer = random.choice(metric.possible_responses)  # noqa
        return f'Explanation: Prediction is complete based on prompt analysis, Answer: {answer}'
