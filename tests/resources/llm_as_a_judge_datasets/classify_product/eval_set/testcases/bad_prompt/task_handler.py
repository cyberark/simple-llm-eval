import logging

from simpleval.consts import LOGGER_NAME
from simpleval.testcases.schemas.llm_task_result import LlmTaskResult
from simpleval.utilities.retryables import bedrock_limits_retry
from tests.resources.llm_as_a_judge_datasets.classify_product.eval_set.testcases.good_prompt.task_handler import GOOD_SYSTEM_PROMPT
from tests.resources.llm_as_a_judge_datasets.claude import call_claude_completion

logger = logging.getLogger(LOGGER_NAME)

BAD_SYSTEM_PROMPT = ('You are an intentionally wrong text classification model. '
                     'Given the following user inquiry, classify it into one of these four categories: '
                     "\"Feature Inquiry\", \"Refund/Returns\", \"Positive Testimonial\", \"General Question\".\n"
                     'But then return another label and not the correct one.\n'
                     f'User inquiry: {{user_input}}\n\n'
                     'Return only the wrong label (one of the four categories) without explanation or any additional text.')


@bedrock_limits_retry
def task_logic(name: str, payload: dict) -> LlmTaskResult:
    logger.debug(f'{__name__}: Running task logic for {name} with payload: {payload}')

    user_input = payload['user_input']

    system_prompt = BAD_SYSTEM_PROMPT.format(user_input=user_input)
    llm_result = call_claude_completion(
        role='product classifier',
        system_prompt=system_prompt,
        user_prompt='Perform the product question classification',
    )

    if llm_result not in ['Feature Inquiry', 'Refund/Returns', 'Positive Testimonial', 'General Question']:
        raise ValueError(f'Invalid response from LLM: {llm_result}')

    return LlmTaskResult(
        name=name,
        prompt=GOOD_SYSTEM_PROMPT.format(user_input=user_input),  # send the good prompt here that would have been expected
        prediction=llm_result,
        payload=payload,
    )
