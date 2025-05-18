from pydantic import BaseModel

from simpleval.evaluation.schemas.utils import get_name_metric_id
from simpleval.testcases.schemas.llm_task_result import LlmTaskResult


class EvalTestResult(BaseModel):
    metric: str
    result: str
    explanation: str
    normalized_score: float
    llm_run_result: LlmTaskResult

    @property
    def name_metric(self) -> str:
        return get_name_metric_id(self.llm_run_result.name, self.metric)
