import logging

from simpleval.consts import LOGGER_NAME
from simpleval.testcases.schemas.llm_task_result import LlmTaskResult
from simpleval.utilities.retryables import bedrock_limits_retry
from tests.resources.llm_as_a_judge_datasets.claude import call_claude_completion

logger = logging.getLogger(LOGGER_NAME)

GOOD_SYSTEM_PROMPT = ('You are a text classification model. '
                      'Given the following user inquiry, classify it into one of these four categories: '
                      "\"Feature Inquiry\", \"Refund/Returns\", \"Positive Testimonial\", \"General Question\".\n"
                      'Return only the label (one of the four categories) without explanation or any additional text.'
                      "Never say \"I apologize, but I don't have a specific user inquiry\", always return one of the four categories."
                      f'Here is the user inquiry: {{user_input}}\n\n')


@bedrock_limits_retry
def task_logic(name: str, payload: dict) -> LlmTaskResult:
    logger.debug(f'{__name__}: Running task logic for {name} with payload: {payload}')

    user_input = payload['user_input']
    system_prompt = GOOD_SYSTEM_PROMPT.format(user_input=user_input)

    result = call_claude_completion(
        role='product classifier',
        system_prompt=system_prompt,
        user_prompt='Perform the product question classification',
    )

    if result not in ['Feature Inquiry', 'Refund/Returns', 'Positive Testimonial', 'General Question']:
        raise ValueError(f'Invalid response from LLM: {result}')

    result = LlmTaskResult(
        name=name,
        prompt=system_prompt,
        prediction=result,  # This is what your llm responded
        payload=payload,
    )

    return result
