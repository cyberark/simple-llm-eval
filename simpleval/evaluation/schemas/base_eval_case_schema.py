from pydantic import BaseModel


class GroundTruth(BaseModel):
    name: str
    description: str
    expected_result: str
    payload: dict
