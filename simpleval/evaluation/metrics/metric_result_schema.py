from pydantic import BaseModel


class MetricResult(BaseModel):
    normalized_score: float
    result: str
    explanation: str
