from typing import Optional

from pydantic import BaseModel


class LlmTaskResult(BaseModel):
    """
    Represents the result of an llm task run.

    Attributes:
        name (str): The name of the testcase.
        prompt (str): The prompt sent to the generator from your dataset.
        prediction (str): The generator model's responses.
        payload (dict): Additional data related to the testcase run.
    """

    name: str
    prompt: str
    prediction: str
    expected_prediction: Optional[str] = None
    payload: dict = {}
