import json
import logging
import os

from colorama import Fore
from pydantic import BaseModel, Field

from simpleval.consts import GLOBAL_CONFIG_FILE, LOGGER_NAME


class WaitRandExpRetryConfig(BaseModel):
    """
    All retry decorators use tenacity's wait_random_exponential function. See:
    https://tenacity.readthedocs.io/en/latest/api.html#tenacity.wait.wait_random_exponential
    """

    stop_after_attempt: int = Field(..., ge=1)
    multiplier: float = Field(..., ge=0)
    min: float = Field(..., ge=0)
    max: float = Field(..., ge=0)
    exp_base: int = Field(..., ge=0)


DEFAULT_RETRY_CONFIG = WaitRandExpRetryConfig(
    stop_after_attempt=6,
    multiplier=2,  # Initial window - 2s
    min=10,  # min 10s timeout
    max=60,  # max 30s timeout
    exp_base=2,  # exponential base 2
)


class RetryConfigs(BaseModel):
    judge_model: WaitRandExpRetryConfig = Field(default_factory=lambda: DEFAULT_RETRY_CONFIG)


class GlobalConfigRetries(BaseModel):
    retry_configs: RetryConfigs


def get_global_config_retries() -> RetryConfigs:
    config_file = os.path.join(os.getcwd(), GLOBAL_CONFIG_FILE)
    if os.path.exists(config_file):
        with open(config_file, 'r', encoding='utf-8') as file:
            logger = logging.getLogger(LOGGER_NAME)
            logger.info(f'{Fore.CYAN}Loading retries settings from global config{Fore.RESET}')
            config = GlobalConfigRetries(**json.load(file))
            logger.info(f'{Fore.CYAN}Retries settings: {config}{Fore.RESET}')
            return GlobalConfigRetries(**json.load(file)).retry_configs

    return GlobalConfigRetries(retry_configs=RetryConfigs()).retry_configs
