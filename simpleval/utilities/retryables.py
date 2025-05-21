import boto3
import litellm
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_random_exponential

from simpleval.global_config.retries import get_global_config_retries


def _get_retry_config():
    return get_global_config_retries().judge_model


retry_config = _get_retry_config()


def create_retry_with_exceptions(exceptions):
    """
    Creates a retry decorator with specified exception types.

    Args:
        exceptions: A tuple of exception types to retry on

    Returns:
        A configured retry decorator
    """

    return retry(
        retry=retry_if_exception_type(exceptions),
        stop=stop_after_attempt(retry_config.stop_after_attempt),
        wait=wait_random_exponential(
            multiplier=retry_config.multiplier,
            min=retry_config.min,
            max=retry_config.max,
            exp_base=retry_config.exp_base,
        ),
    )


# Random wait with exponentially widening window.
bedrock = boto3.client(service_name='bedrock-runtime', region_name='us-east-1')
BEDROCK_LIMITS_EXCEPTIONS = (bedrock.exceptions.ThrottlingException, bedrock.exceptions.ServiceQuotaExceededException)
bedrock_limits_retry = create_retry_with_exceptions(BEDROCK_LIMITS_EXCEPTIONS)

# https://docs.litellm.ai/docs/exception_mapping
LITELLM_LIMITS_EXCEPTIONS = (litellm.Timeout, litellm.RateLimitError, litellm.ServiceUnavailableError)
litellm_limits_retry = create_retry_with_exceptions(LITELLM_LIMITS_EXCEPTIONS)
