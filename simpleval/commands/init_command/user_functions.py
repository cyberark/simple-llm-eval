import logging
import os
from typing import List

from colorama import Fore
from InquirerPy import prompt

from simpleval.commands.init_command.base_init import BaseInit
from simpleval.commands.init_command.consts import (
    DEFAULT_CONCURRENT_JUDGE_TASKS,
    DEFAULT_CONCURRENT_LLM_TASKS,
    PICK_YOUR_OWN_METRICS,
    RECOMMENDED_START_METRICS,
    RECOMMENDED_START_METRICS_MENU_VALUE,
)
from simpleval.consts import LOGGER_NAME
from simpleval.evaluation.judges.base_judge import BaseJudge
from simpleval.evaluation.judges.judge_provider import JudgeProvider
from simpleval.evaluation.schemas.eval_task_config_schema import EvalTaskConfig
from simpleval.exceptions import TerminationError

RECOMMENDED_INDICATION = '(recommended)'


def get_eval_dir_from_user() -> str:
    """
    Prompts the user for a directory name and returns the full path.

    Returns:
        str: The full path of the new evaluation folder.
    """

    logger = logging.getLogger(LOGGER_NAME)

    eval_dir_set = False
    while not eval_dir_set:
        logger.info(f'{Fore.CYAN}Enter the name of the new evaluation folder - relative or absolute path that does not exist.{Fore.RESET}')
        logger.info(f'{Fore.CYAN}The folder name should describe the evaluation you are going to perform.{Fore.RESET}')
        logger.info(f'{Fore.CYAN}For example: {Fore.YELLOW}my_eval{Fore.CYAN} or {Fore.YELLOW}{_example_dir()}{Fore.RESET}')

        eval_dir = input(f'{Fore.CYAN}\nEnter eval folder (enter to stop): {Fore.RESET}')
        if not eval_dir:
            raise TerminationError(f'{Fore.RED}No folder name provided, exiting...{Fore.RESET}')

        eval_dir = os.path.abspath(os.path.expanduser(eval_dir))

        if os.path.exists(eval_dir):
            print(f'{Fore.RED}Folder already exists: {eval_dir}, please choose another name{Fore.RESET}')
        else:
            eval_dir_set = True

    return eval_dir


def get_testcase_name_from_user() -> str:
    """
    Prompts the user for a testcase name and returns it.

    Returns:
        str: The name of the testcase.
    """
    logger = logging.getLogger(LOGGER_NAME)

    logger.info('')
    logger.info(f'{Fore.CYAN}Enter the name of your first testcase.{Fore.RESET}')
    logger.info(f'{Fore.CYAN}This should reflect the conditions that you want to run.{Fore.RESET}')
    logger.info(f'{Fore.CYAN}This can be: using different model, different set of prompts, etc.{Fore.RESET}')
    logger.info(f'{Fore.CYAN}For example: {Fore.YELLOW}sonnet37{Fore.CYAN}, {Fore.YELLOW}prompt_v1`{Fore.RESET}')

    testcase_name = ''
    while not testcase_name:
        testcase_name = input(f'{Fore.CYAN}\nEnter testcase name: {Fore.RESET}')
        testcase_name = BaseInit.normalize_testcase_dir_name(testcase_name)

    return testcase_name


def pick_judge() -> str:
    judge_names = JudgeProvider.list_judges(filter_internal=True)
    questions = [{'type': 'list', 'name': 'selected_judge', 'message': 'Select a judge:', 'choices': judge_names}]
    answers = prompt(questions)
    return answers['selected_judge']


def run_preliminary_checks(judge: BaseJudge):
    logger = logging.getLogger(LOGGER_NAME)

    try:
        judge.run_preliminary_checks()
    except Exception as e:
        logger.error(f'{Fore.RED}Error occurred during judge preliminary checks\n{e}{Fore.RESET}')
        logger.info(f'{Fore.YELLOW}{judge.preliminary_checks_explanation()}{Fore.RESET}')
        ans = input(f'{Fore.CYAN}\nDo you want to ignore and continue (y/n)? {Fore.RESET}')
        if ans.lower() != 'y':
            raise TerminationError(f'{Fore.YELLOW}Exiting...{Fore.RESET}')
        else:
            logger.info(f'{Fore.YELLOW}\nContinuing with errors - fix this later before you run{Fore.RESET}')

    logger.debug(f'Selected judge: {judge.name}, passed preliminary checks')


def get_judge_from_user() -> BaseJudge:
    judge = pick_judge()
    judge = JudgeProvider.get_judge(judge)

    run_preliminary_checks(judge)
    return judge


def get_model_id_from_user(judge: BaseJudge) -> str:
    models_to_select = list(judge.supported_model_ids)
    if judge.model_id in models_to_select:
        models_to_select.remove(judge.model_id)

    models_to_select.insert(0, f'{judge.model_id} {RECOMMENDED_INDICATION}')

    questions = [
        {
            'type': 'list',
            'name': 'selected_model',
            'message': f'Select a model (default: {judge.model_id}):',
            'choices': models_to_select,
        }
    ]

    answers = prompt(questions)
    selected_model = answers['selected_model'].replace(RECOMMENDED_INDICATION, '').strip()

    return selected_model


def get_metrics_from_user(metrics: List[str]) -> List[str]:
    logger = logging.getLogger(LOGGER_NAME)
    logger.info(f'{Fore.CYAN}To learn more about each metric run {Fore.YELLOW}`simpleval metrics-explorer`{Fore.RESET}')

    questions = [
        {
            'type': 'list',
            'name': 'selected_metrics',
            'message': 'Select the recommended metrics to start with, or pick your own:',
            'choices': [RECOMMENDED_START_METRICS_MENU_VALUE, PICK_YOUR_OWN_METRICS],
        }
    ]
    answers = prompt(questions)
    selected_metrics = answers['selected_metrics']
    if selected_metrics == RECOMMENDED_START_METRICS_MENU_VALUE:
        return RECOMMENDED_START_METRICS

    questions = [
        {
            'type': 'checkbox',
            'name': 'selected_metrics',
            'message': 'Select metrics to evaluate (space to select):',
            'choices': metrics,
        }
    ]
    answers = prompt(questions)
    selected_metrics = answers['selected_metrics']

    if not selected_metrics:
        raise TerminationError(f'{Fore.RED}No metrics selected, exiting...{Fore.RESET}')

    return selected_metrics


def get_max_concurrent_from_user(task: str, default: int) -> int:
    from colorama import Fore

    question = f'Enter max concurrent {task} tasks (enter: {default}): '

    while True:
        max_concurrent = input(f'{Fore.CYAN}{question}{Fore.RESET}')
        if not max_concurrent.strip():
            return default
        try:
            value = int(max_concurrent)
            if value <= 0:
                raise ValueError
            return value
        except ValueError:
            print(f'{Fore.RED}Please enter a positive integer or press Enter to use the default.{Fore.RESET}')


def get_concurrency_values() -> tuple[int, int]:
    logger = logging.getLogger(LOGGER_NAME)

    max_concurrent_judge_tasks = DEFAULT_CONCURRENT_JUDGE_TASKS
    max_concurrent_llm_tasks = DEFAULT_CONCURRENT_LLM_TASKS

    logger.info(
        f'{Fore.CYAN}By default you will run {DEFAULT_CONCURRENT_JUDGE_TASKS} judges in parallel{Fore.RESET}, and {DEFAULT_CONCURRENT_LLM_TASKS} LLM tasks in parallel'
    )
    configure_concurrency = input(f'{Fore.CYAN}\nDo you want to configure concurrency (N/y)? {Fore.RESET}')

    if configure_concurrency.lower() == 'y':
        max_concurrent_judge_tasks = get_max_concurrent_from_user(task='judge', default=DEFAULT_CONCURRENT_JUDGE_TASKS)
        max_concurrent_llm_tasks = get_max_concurrent_from_user(task='llm', default=DEFAULT_CONCURRENT_LLM_TASKS)
    else:
        logger.info(f'{Fore.YELLOW}Using default concurrency settings{Fore.RESET}')

    logger.debug(f'Configured concurrency: {max_concurrent_judge_tasks} judges, {max_concurrent_llm_tasks} LLM tasks')
    return max_concurrent_judge_tasks, max_concurrent_llm_tasks


def get_eval_config_from_user() -> EvalTaskConfig:
    """
    Prompts the user for evaluation configuration details and returns an EvalTaskConfig object.

    Returns:
        EvalTaskConfig: The evaluation configuration object.
    """
    logger = logging.getLogger(LOGGER_NAME)

    judge = get_judge_from_user()
    model_id = get_model_id_from_user(judge)
    selected_metrics = get_metrics_from_user(judge.list_metrics())

    max_concurrent_judge_tasks, max_concurrent_llm_tasks = get_concurrency_values()

    eval_config = EvalTaskConfig(
        name='temp_name',
        max_concurrent_judge_tasks=max_concurrent_judge_tasks,
        max_concurrent_llm_tasks=max_concurrent_llm_tasks,
        llm_as_a_judge_name=judge.name,
        llm_as_a_judge_model_id=model_id,
        eval_metrics=selected_metrics,
    )

    logger.debug(f'Created eval config: {eval_config}')

    return eval_config


def _example_dir() -> str:
    """
    Returns the path to the example directory - os dependent.
    """
    if os.name == 'nt':
        return 'C:\\evals\\my_eval'
    return '/home/user/my_eval'
