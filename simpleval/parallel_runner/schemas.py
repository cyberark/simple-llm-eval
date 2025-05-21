from pydantic import BaseModel


class TaskParams:
    def __init__(self, task_name: str, payload: BaseModel):
        self.task_name = task_name
        self.payload = payload


class TaskResult:
    def __init__(self, task_name: str, result: BaseModel):
        self.task_name = task_name
        self.result = result
