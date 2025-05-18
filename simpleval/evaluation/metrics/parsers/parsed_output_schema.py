from pydantic import BaseModel


class JudgeParsedOutput(BaseModel):
    reasonings: str
    answer: str
