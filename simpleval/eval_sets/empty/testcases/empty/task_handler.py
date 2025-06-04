import logging

from simpleval.consts import LOGGER_NAME

# from simpleval.logger import log_bookkeeping_data
from simpleval.testcases.schemas.llm_task_result import LlmTaskResult


# Recommended to implement retry here, see built-in @litellm_limits_retry, @bedrock_limits_retry as reference.
def task_logic(name: str, payload: dict) -> LlmTaskResult:
    """
    Your llm task logic goes here.
    You can (but you don't have to) use the simpleval logger which works with the verbose flag.
    """
    print('NOTE: implement retries on rate limits. see simpleval.utilities.retryables for built-in decorators')

    logger = logging.getLogger(LOGGER_NAME)
    logger.debug(f'{__name__}: Running task logic for {name} with payload: {payload}')

    # Implement your logic here - typically call an llm to do your work, using the inputs from payload
    # The user prompt is also returned in LlmTaskResult since the judge will use it when making judgement.
    user_prompt_to_llm = 'Hi LLM, please respond to this prompt, replace with your own prompt'
    # llm_response = call_an_llm_here(user_prompt=user_prompt_to_llm)
    llm_response = 'This is the response from the LLM'  # The llm response is returned in LlmTaskResult

    # To log token usage, call this with your token count, when verbose is on (-v) it will write it to tokens-bookkeeping.log
    # log_bookkeeping_data(source='llm', model_name=model_id, input_tokens=input_tokens, output_tokens=output_tokens)

    result = LlmTaskResult(
        name=name,
        prompt=user_prompt_to_llm,  # This is what you sent to your llm
        prediction=llm_response,  # This is what your llm responded
        payload=payload,
    )

    return result
