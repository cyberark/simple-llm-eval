from abc import abstractmethod

from pydantic import BaseModel

from simpleval.evaluation.metrics.base_metric import EvaluationMetric


class StructuredResponse(BaseModel):
    """
    This is general structured response model for the LiteLLM metric.
    It does not enforce the values of answer which is done on each metric output model (call metric.output_model to get it).
    It is used during the general metric parsing step, at which point the metric specific model parsing was already done
    see litellm_structured_output_parser.
    """

    reasoning: str
    answer: str


class LiteLLMMetric(EvaluationMetric):
    @property
    @abstractmethod
    def output_model(self) -> BaseModel:
        """
        The pydantic model for the structured output.
        """
