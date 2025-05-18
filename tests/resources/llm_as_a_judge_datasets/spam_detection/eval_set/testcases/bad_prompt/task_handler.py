import logging

from simpleval.consts import LOGGER_NAME
from simpleval.testcases.schemas.llm_task_result import LlmTaskResult
from simpleval.utilities.retryables import bedrock_limits_retry
from tests.resources.llm_as_a_judge_datasets.claude import call_claude_completion
from tests.resources.llm_as_a_judge_datasets.spam_detection.eval_set.testcases.good_prompt.task_handler import GOOD_SYSTEM_PROMPT

logger = logging.getLogger(LOGGER_NAME)

BAD_SYSTEM_PROMPT = f"""You are an You are an intentionally wrong email filter.
Read the user input carefully and decide whether it is ‘Spam’ or ‘Not Spam’ based on the content and return the opposite.
Content is considered spam if it contains deceptive offers, unrealistic claims, suspicious links,
or other characteristics typical of junk or unsolicited emails. Otherwise, classify it as ‘Not Spam.’

Only return one of the two categories ‘Spam’ or ‘Not Spam’ without any additional text or explanation.
Analyze the email message and return the opposite appropriate label.

Here is the email message: {{user_input}}"""


@bedrock_limits_retry
def task_logic(name: str, payload: dict) -> LlmTaskResult:
    logger.debug(f'{__name__}: Running task logic for {name} with payload: {payload}')

    user_input = payload['user_input']
    system_prompt = BAD_SYSTEM_PROMPT.format(user_input=user_input)

    result = call_claude_completion(
        role='email filter',
        system_prompt=system_prompt,
        user_prompt='Perform the email spam detection',
    )

    if result not in ['Spam', 'Not Spam']:
        raise ValueError(f'Invalid response from LLM: {result}')

    result = LlmTaskResult(
        name=name,
        prompt=GOOD_SYSTEM_PROMPT.format(user_input=user_input),
        prediction=result,
        payload=payload,
    )

    return result
