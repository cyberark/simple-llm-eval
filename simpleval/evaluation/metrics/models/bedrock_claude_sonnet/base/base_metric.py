from abc import abstractmethod

from simpleval.evaluation.metrics.base_metric import EvaluationMetric


class BaseBedrockSonnetMetric(EvaluationMetric):
    @property
    @abstractmethod
    def prefill(self) -> str:
        """
        The prefix for the claude prefill
        See https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/prefill-claudes-response
        """
