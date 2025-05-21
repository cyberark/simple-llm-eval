from simpleval.testcases.schemas.llm_task_result import LlmTaskResult

DUMMY_TASK_PROMPT = 'What does the user say?'


def task_logic(name: str, payload: dict) -> LlmTaskResult:
    # Example logic for the plugin
    result = LlmTaskResult(
        name=name,
        prompt=DUMMY_TASK_PROMPT,
        prediction=f'User says: {payload["user_input"]}',
        payload=payload,
    )

    return result
