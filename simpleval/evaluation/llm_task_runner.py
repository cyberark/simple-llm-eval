import importlib.util
import json
import logging
import os
from typing import List

from colorama import Fore

from simpleval.consts import LOGGER_NAME
from simpleval.evaluation.schemas.base_eval_case_schema import GroundTruth
from simpleval.evaluation.utils import (
    get_all_llm_task_results,
    get_eval_config,
    get_eval_ground_truth,
    get_llm_task_results_file,
    get_testcase_folder,
    is_llm_task_result_found,
)
from simpleval.parallel_runner.parallel_runner import BaseRunner
from simpleval.parallel_runner.schemas import TaskParams, TaskResult
from simpleval.testcases.schemas.llm_task_result import LlmTaskResult

PLUGIN_FILE_NAME = 'task_handler.py'
PLUGIN_FUNCTION_NAME = 'task_logic'


def run_llm_tasks(eval_dir: str, config_file: str, testcase: str):
    logger = logging.getLogger(LOGGER_NAME)

    logger.info(f'Running testcase: {eval_dir}:{testcase}, {config_file=}')

    all_eval_cases = get_eval_ground_truth(eval_dir)
    eval_config = get_eval_config(eval_dir=eval_dir, config_file=config_file)
    logger.debug(f'Eval config: {eval_config}')

    existing_llm_run_results = get_all_llm_task_results(eval_set_dir=eval_dir, testcase=testcase)
    llm_tasks_to_run = filter_existing_results(existing_testcase_results=existing_llm_run_results, eval_cases=all_eval_cases)
    if not llm_tasks_to_run:
        logger.debug('All llm tasks already ran')
        return existing_llm_run_results, []

    plugin_function = _load_plugin(get_testcase_folder(eval_set_dir=eval_dir, testcase=testcase))

    max_concurrent_llm_tasks = eval_config.effective_max_concurrent_llm_tasks(testcase)
    logger.info(f'Max concurrent llm tasks: {max_concurrent_llm_tasks}')

    runner = LlmTaskRunner(max_concurrent_llm_tasks)
    tasks_to_run = [TaskParams(task_name=eval_case.name, payload=eval_case) for eval_case in llm_tasks_to_run]
    results, errors = runner.run_tasks(
        tasks=tasks_to_run,
        task_function=lambda test_case, _: _run_llm_task(test_case, plugin_function),
        task_config=None,
    )

    for error in errors:
        logger.error(f'Error running test case: {error}')

    # Combine existing results with new results for writing to file
    results.extend(existing_llm_run_results)
    write_llm_task_results_file(eval_set_dir=eval_dir, testcase=testcase, results=results)

    return results, errors


def filter_existing_results(existing_testcase_results: List[LlmTaskResult], eval_cases: List[GroundTruth]) -> List[GroundTruth]:
    logger = logging.getLogger(LOGGER_NAME)

    if not existing_testcase_results:
        return eval_cases

    logger.debug(f'filter_existing_results: {existing_testcase_results=}, {eval_cases=}')

    eval_cases_to_run = [
        llm_task for llm_task in eval_cases if not is_llm_task_result_found(existing_testcase_results, llm_task_name=llm_task.name)
    ]

    filtered_results_count = len(eval_cases) - len(eval_cases_to_run)
    if filtered_results_count > 0:
        logger.info(f'{Fore.YELLOW}Filtered out {filtered_results_count} results that were already found in the results file.{Fore.RESET}')

    logger.debug(f'filter_existing_results: {eval_cases_to_run=}, {len(eval_cases_to_run)=}')

    return eval_cases_to_run


def write_llm_task_results_file(eval_set_dir: str, testcase: str, results: List[LlmTaskResult]):
    results_file_path = get_llm_task_results_file(eval_set_dir=eval_set_dir, testcase=testcase)
    with open(results_file_path, 'w', encoding='utf-8') as results_file:
        for result in results:
            results_file.write(json.dumps(result.model_dump()) + '\n')


def _load_plugin(test_dataset_dir: str):
    try:
        plugin_path = os.path.join(test_dataset_dir, PLUGIN_FILE_NAME)
        if not os.path.exists(plugin_path):
            raise FileNotFoundError(f'PLUGIN ERROR: {plugin_path} not found')

        spec = importlib.util.spec_from_file_location('plugin_module', plugin_path)
        plugin_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(plugin_module)

        if not hasattr(plugin_module, PLUGIN_FUNCTION_NAME):
            raise AttributeError(f'PLUGIN ERROR: Plugin does not have required function {PLUGIN_FUNCTION_NAME}')

        return getattr(plugin_module, PLUGIN_FUNCTION_NAME)
    except Exception as e:
        raise RuntimeError(f'PLUGIN ERROR: Unknown error loading plugin: {plugin_path=}, {str(e)}, {e}, {plugin_path=}') from e


def _run_llm_task(ground_truth: GroundTruth, plugin_function):  # -> Any | LlmRunResult:  # -> Any | TestcaseRunResult:
    logger = logging.getLogger(LOGGER_NAME)
    logger.info(f'Running llm task: {ground_truth.name}')

    result: LlmTaskResult = plugin_function(ground_truth.name, ground_truth.payload)
    if ground_truth.expected_result:
        result.expected_prediction = ground_truth.expected_result

    return TaskResult(task_name=result.name, result=result)


class LlmTaskRunner(BaseRunner):
    def __init__(self, max_concurrent_tasks: int):
        super().__init__(max_concurrent_tasks)
        self.logger = logging.getLogger(LOGGER_NAME)

    def process_results(self, results: List[LlmTaskResult], errors: List[str]):
        self.logger.debug('')
        self.logger.debug('LLM tasks run results:')
        self.logger.debug('-' * 50)

        for result in results:
            self.logger.debug(f'Test case: {result.name}')
            self.logger.debug(f'LLM task runner result: {result}')
            self.logger.debug('=' * 50)

        if errors:
            self.logger.debug(f'Errors occurred when running llm tasks. {len(errors)} error(s) found.')

        for error in errors:
            self.logger.debug(f'Error running LLM task: {error}')
