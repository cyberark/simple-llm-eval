import logging

from colorama import Fore

from simpleval.consts import LOGGER_NAME
from simpleval.evaluation.judges.judge_provider import JudgeProvider
from simpleval.utilities.console import print_list


def list_models_command():
    print_list(
        title='Available llm as a judge models',
        items=JudgeProvider.list_judges(filter_internal=True),
    )
