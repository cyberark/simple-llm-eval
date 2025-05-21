"""
CLI Command to run the eval process
"""

import logging
import time

from colorama import Fore

from simpleval.commands.reporting.eval.eval_report import ResultsManager
from simpleval.consts import LOGGER_NAME
from simpleval.evaluation.eval_runner import run_eval
from simpleval.evaluation.llm_task_runner import run_llm_tasks
from simpleval.evaluation.utils import (
    get_all_eval_results,
    get_all_llm_task_results,
    get_eval_config,
    get_eval_errors_file,
    get_eval_ground_truth,
    get_eval_name,
    get_eval_result_file,
    get_llm_task_errors_file,
    get_llm_task_results_file,
    get_testcase_folder,
)
from simpleval.exceptions import NoWorkToDo, TerminationError
from simpleval.utilities.files import delete_file
from simpleval.validations import validate_eval_input


def run_command(eval_dir: str, config_file: str, testcase: str, overwrite_results: bool, report_format: str):
    logger = logging.getLogger(LOGGER_NAME)
    logger.info(f'{Fore.CYAN}Running evaluation, {eval_dir=}, {testcase=}, {overwrite_results=}{Fore.RESET}')

    validate_input_data(eval_dir=eval_dir, config_file=config_file)
    start_time_llm_tasks = time.time()

    _clean_error_files(eval_set_dir=eval_dir, testcase=testcase)
    if overwrite_results:
        _clean_results(eval_set_dir=eval_dir, testcase=testcase)
    else:
        _prompt_and_exit_on_full_results(eval_dir=eval_dir, config_file=config_file, testcase=testcase)

    _, llm_run_errors = run_llm_tasks(eval_dir=eval_dir, config_file=config_file, testcase=testcase)

    end_time_llm_tasks = time.time()
    elapsed_time_llm_tasks = end_time_llm_tasks - start_time_llm_tasks

    start_time_runeval = time.time()
    eval_results, eval_errors = run_eval(eval_dir=eval_dir, config_file=config_file, testcase=testcase)
    end_time_runeval = time.time()
    elapsed_time_runeval = end_time_runeval - start_time_runeval

    print_exec_time(elapsed_time_llm_tasks, elapsed_time_runeval)

    _handle_errors(eval_dir=eval_dir, testcase=testcase, llm_task_errors=llm_run_errors, eval_errors=eval_errors)

    results_manager = ResultsManager()
    results_manager.display_results(
        name=get_eval_name(eval_dir=eval_dir, config_file=config_file),
        testcase=testcase,
        eval_results=eval_results,
        llm_tasks_errors_count=len(llm_run_errors),
        eval_errors_count=len(eval_errors),
        output_format=report_format,
    )

    return len(llm_run_errors), len(eval_errors)


def validate_input_data(eval_dir: str, config_file: str):
    logger = logging.getLogger(LOGGER_NAME)

    try:
        logger.info(f'{Fore.YELLOW}Validating input data{Fore.RESET}')
        validate_eval_input(eval_dir=eval_dir, config_file=config_file)
        logger.info(f'{Fore.GREEN}Input validated successfully{Fore.RESET}\n')
    except FileNotFoundError as ex:
        raise TerminationError(f'File not found: {ex}') from ex
    except ValueError as ex:
        error = f'Validation error: {ex}\neval_dir={eval_dir}'
        if hasattr(ex, 'doc'):
            error += f'\ndoc: {ex.doc}'
        raise TerminationError(error) from ex
    except Exception as ex:
        raise TerminationError(f'Error occurred: {ex}') from ex


def _clean_error_files(eval_set_dir: str, testcase: str):
    logger = logging.getLogger(LOGGER_NAME)
    logger.info('Overwriting existing error files')
    delete_file(get_llm_task_errors_file(eval_set_dir=eval_set_dir, testcase=testcase))
    delete_file(get_eval_errors_file(eval_set_dir=eval_set_dir, testcase=testcase))


def _clean_results(eval_set_dir: str, testcase: str):
    logger = logging.getLogger(LOGGER_NAME)
    logger.info('Overwriting existing results')
    delete_file(get_llm_task_results_file(eval_set_dir=eval_set_dir, testcase=testcase))
    delete_file(get_eval_result_file(eval_set_dir=eval_set_dir, testcase=testcase))


def _prompt_and_exit_on_full_results(eval_dir: str, config_file: str, testcase: str):
    logger = logging.getLogger(LOGGER_NAME)

    ground_truth = get_eval_ground_truth(eval_dir)
    testcase_dir = get_testcase_folder(eval_set_dir=eval_dir, testcase=testcase)

    llm_task_results = get_all_llm_task_results(eval_set_dir=eval_dir, testcase=testcase)
    if not llm_task_results:
        logger.debug(f'prompt_user_on_full_results: LLM task results file not found in {testcase_dir}, no need to prompt user')
        return

    try:
        eval_results = get_all_eval_results(eval_set_dir=eval_dir, testcase=testcase)
    except FileNotFoundError:
        logger.debug(f'prompt_user_on_full_results: Eval results file not found in {testcase_dir}, no need to prompt user')
        return

    missing_llm_tasks = len(ground_truth) - len(llm_task_results)
    if missing_llm_tasks > 0:
        logger.debug(f'prompt_user_on_full_results: {missing_llm_tasks} llm task(s) not found for ground truth')
        return

    eval_config = get_eval_config(eval_dir=eval_dir, config_file=config_file)
    # Expecting len(ground_truth) for each metric results
    missing_eval_results = len(ground_truth) * len(eval_config.eval_metrics) - len(eval_results)
    if missing_eval_results > 0:
        logger.error(f'prompt_user_on_full_results: {missing_eval_results} eval results not found for ground truth')
        return

    logger.error(f'{Fore.YELLOW}Skipping execution.')
    logger.error('All llm tasks and evaluation results already exist, your options are:\n')
    logger.error('  -> Open an existing html report (see ./results dir)')
    logger.error('  -> To Generate a report run:')
    logger.error(f'     "simpleval reports eval -e {eval_dir} -t {testcase}"')
    logger.error('  -> To run all tests, OVERWRITING all existing results run: ')
    logger.error(f'     "simpleval run -e {eval_dir} -t {testcase} -o"{Fore.RESET}')

    raise NoWorkToDo()


def _handle_errors(eval_dir: str, testcase: str, llm_task_errors: list, eval_errors: list):
    logger = logging.getLogger(LOGGER_NAME)

    if llm_task_errors:
        logger.error(f'{Fore.RED}Errors occurred during llm tasks run. {len(llm_task_errors)} error(s) found. Terminating evaluation.')
        with open(get_llm_task_errors_file(eval_set_dir=eval_dir, testcase=testcase), 'w', encoding='utf-8') as file:
            file.writelines(f'{error}\n{"-" * 120}\n' for error in llm_task_errors)

    if eval_errors:
        logger.error(f'{Fore.RED}Errors occurred during evaluation. {len(eval_errors)} error(s) found. Terminating evaluation.')
        logger.error(f'{Fore.RED}Run with --verbose/-v for more details')
        logger.error(f'{Fore.CYAN}If temporary failures, run again without overwriting (no -o) to run only the failures{Fore.RESET}')

        with open(get_eval_errors_file(eval_set_dir=eval_dir, testcase=testcase), 'w', encoding='utf-8') as file:
            file.writelines(f'{error}\n{"-" * 120}\n' for error in eval_errors)


def print_exec_time(elapsed_time_testcases: float, elapsed_time_runeval: float):
    print()
    print(f'{Fore.CYAN}LLM tasks execution time: {elapsed_time_testcases:.2f} seconds{Fore.RESET}')
    print(f'{Fore.CYAN}Evaluation execution time: {elapsed_time_runeval:.2f} seconds{Fore.RESET}')
    print(f'{Fore.CYAN}Total execution time: {elapsed_time_testcases + elapsed_time_runeval:.2f} seconds{Fore.RESET}')
    print()
