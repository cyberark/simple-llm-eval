import logging

from simpleval.consts import LOGGER_NAME

# from simpleval.logger import log_bookkeeping_data
from simpleval.testcases.schemas.llm_task_result import LlmTaskResult


# @bedrock_limits_retry - use if using bedrock to call llm
def task_logic(name: str, payload: dict) -> LlmTaskResult:
    """
    Your llm task logic goes here.
    You can (but you don't have to) use the simpleval logger which works with the verbose flag.
    """
    print('NOTE: implement retries on rate limits. for bedrock, use `@bedrock_limits_retry` decorator (simpleval.utilities.retryables)')

    logger = logging.getLogger(LOGGER_NAME)
    logger.debug(f'{__name__}: Running task logic for {name} with payload: {payload}')

    # Implement your logic here - typically call an llm to do your work, using the inputs from payload
    your_prompt_for_the_llm = 'this is what you send to your llm'
    llm_response = 'hi there!'

    # To log token usage, call this with your token count, when verbose is on (-v) it will write it to tokens-bookkeeping.log
    # log_bookkeeping_data(source='llm', model_name=model_id, input_tokens=input_tokens, output_tokens=output_tokens)

    result = LlmTaskResult(
        name=name,
        prompt=your_prompt_for_the_llm,  # This is what you sent to your llm
        prediction=llm_response,  # This is what your llm responded
        payload=payload,
    )

    return result
