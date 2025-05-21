from simpleval.testcases.schemas.llm_task_result import LlmTaskResult

DUMMY_TASK_PROMPT = 'What does the user say?'


def task_logic(name: str, payload: dict) -> LlmTaskResult:
    # Example logic for the plugin
    result = LlmTaskResult(
        name=name,
        prompt=f'What did the user do in the os? frames: {payload.get("frames", [])}, mouse input: {payload.get("mouse_input", [])}',
        prediction='The user clicked some buttons',
        payload=payload,
    )

    return result
