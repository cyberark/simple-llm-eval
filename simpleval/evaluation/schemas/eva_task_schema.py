from pydantic import BaseModel

from simpleval.evaluation.schemas.base_eval_case_schema import GroundTruth
from simpleval.evaluation.schemas.utils import get_name_metric_id


class EvalTask(BaseModel):
    metric: str
    ground_truth: GroundTruth

    @property
    def name_metric(self):
        return get_name_metric_id(self.ground_truth.name, self.metric)
