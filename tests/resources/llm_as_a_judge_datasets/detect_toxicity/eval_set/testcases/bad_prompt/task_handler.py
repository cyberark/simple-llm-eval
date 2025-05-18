import logging

from simpleval.consts import LOGGER_NAME
from simpleval.testcases.schemas.llm_task_result import LlmTaskResult
from simpleval.utilities.retryables import bedrock_limits_retry
from tests.resources.llm_as_a_judge_datasets.claude import call_claude_completion
from tests.resources.llm_as_a_judge_datasets.detect_toxicity.eval_set.testcases.good_prompt.task_handler import GOOD_SYSTEM_PROMPT

logger = logging.getLogger(LOGGER_NAME)

BAD_SYSTEM_PROMPT = f"""You are an intentionally wrong moderating user messages for toxicity. Your task is to wrongly classify the user’s message into one of three categories:
- “Non-toxic” if the message contains no hateful or harassing language.
- “Neutral” if the message shows disagreement or mild criticism but is not aggressively harassing or hateful.
- “Toxic” if the message includes direct insults, threats, slurs, hate speech, or strong harassment.
Only return one of the three categories without any additional text or explanation.
Always Choose the wrong label and not the correct one.

Please analyze the user’s message and return the wrong label.
Here is the user message: {{user_input}}
"""


@bedrock_limits_retry
def task_logic(name: str, payload: dict) -> LlmTaskResult:
    logger.info(f'{__name__}: Running task logic for {name} with payload: {payload}')

    user_input = payload['user_input']
    system_prompt = BAD_SYSTEM_PROMPT.format(user_input=user_input)

    logger.info(f'System prompt: {system_prompt}')

    result = call_claude_completion(
        role='Forum moderator',
        system_prompt=system_prompt,
        user_prompt='Perform the wrong message moderation for the user input',
    )

    if result not in ['Non-toxic', 'Neutral', 'Toxic']:
        raise ValueError(f'Invalid response from LLM: {result}')

    result = LlmTaskResult(
        name=name,
        prompt=GOOD_SYSTEM_PROMPT.format(user_input=user_input),
        prediction=result,
        payload=payload,
    )

    return result
