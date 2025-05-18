import logging

from colorama import Fore

from simpleval.consts import LOGGER_NAME
from simpleval.evaluation.judges.judge_provider import JudgeProvider


def list_models_command():
    logger = logging.getLogger(LOGGER_NAME)
    logger.info(f'{Fore.GREEN}Available llm as a judge models: {Fore.RESET}')
    logger.info(JudgeProvider.list_judges(filter_internal=True))
    logger.info(Fore.RESET)
