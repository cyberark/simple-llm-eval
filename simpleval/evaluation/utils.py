import json
import os
import re
from pathlib import Path
from typing import List

from colorama import Fore, Style

from simpleval.consts import (
    EMPTY_FOLDER_NAME,
    EVAL_ERROR_FILE_NAME,
    EVAL_RESULTS_FILE,
    EVAL_SETS_FOLDER,
    GROUND_TRUTH_FILE,
    LLM_TASKS_ERROR_FILE_NAME,
    LLM_TASKS_RESULT_FILE,
    TESTCASES_FOLDER,
)
from simpleval.evaluation.judges.base_judge import BaseJudge
from simpleval.evaluation.judges.judge_provider import JudgeProvider
from simpleval.evaluation.schemas.base_eval_case_schema import GroundTruth
from simpleval.evaluation.schemas.eva_task_schema import EvalTask
from simpleval.evaluation.schemas.eval_result_schema import EvalTestResult
from simpleval.evaluation.schemas.eval_task_config_schema import EvalTaskConfig
from simpleval.testcases.schemas.llm_task_result import LlmTaskResult


def get_eval_ground_truth(eval_dir: str) -> List[GroundTruth]:
    ground_truth_path = os.path.join(eval_dir, GROUND_TRUTH_FILE)
    if not os.path.exists(ground_truth_path):
        cwd = os.getcwd()
        raise FileNotFoundError(f'{ground_truth_path} not found, {cwd=}')

    with open(ground_truth_path, 'r', encoding='utf-8') as file:
        eval_cases = file.readlines()

    return [GroundTruth(**json.loads(eval_case)) for eval_case in eval_cases]


def get_eval_config(eval_dir: str, config_file: str, verify_metrics: bool = True) -> EvalTaskConfig:
    config_path = os.path.join(eval_dir, config_file)
    if not os.path.exists(config_path):
        cwd = os.getcwd()
        raise FileNotFoundError(f'Eval config file `{config_path}` not found, {cwd=}')

    with open(config_path, 'r', encoding='utf-8') as file:
        config_data = json.load(file)
        eval_config = EvalTaskConfig(**config_data)

    if verify_metrics:
        judge: BaseJudge = JudgeProvider.get_judge(eval_config.llm_as_a_judge_name)
        available_metrics = judge.list_metrics()

        if len(eval_config.eval_metrics) == 0 or not all(metrics in available_metrics for metrics in eval_config.eval_metrics):
            metrics_dir = os.path.join(judge.get_metrics_dir(), eval_config.llm_as_a_judge_name)
            raise ValueError(
                f'Invalid Metric(s): `{eval_config.eval_metrics}`. Available metrics: {available_metrics}, Metrics dir: {metrics_dir}'
            )

    return eval_config


def get_eval_name(eval_dir: str, config_file: str):
    return get_eval_config(eval_dir=eval_dir, config_file=config_file).name


def highlight_regex(text, pattern, color=Fore.BLUE):
    # Wrap matched pattern with color
    return re.sub(pattern, lambda m: f'{color}{m.group(0)}{Style.RESET_ALL}', text)


def get_empty_eval_set_folder():
    return str(Path(__file__).resolve().parent.parent / EVAL_SETS_FOLDER / EMPTY_FOLDER_NAME)


def get_empty_testcase_folder():
    return str(Path(__file__).resolve().parent.parent / EVAL_SETS_FOLDER / EMPTY_FOLDER_NAME / TESTCASES_FOLDER / EMPTY_FOLDER_NAME)


def get_testcase_folder(eval_set_dir: str, testcase: str):
    return os.path.join(eval_set_dir, TESTCASES_FOLDER, testcase)


def get_llm_task_results_file(eval_set_dir: str, testcase: str):
    return os.path.join(get_testcase_folder(eval_set_dir, testcase), LLM_TASKS_RESULT_FILE)


def get_llm_task_errors_file(eval_set_dir: str, testcase: str):
    return os.path.join(get_testcase_folder(eval_set_dir, testcase), LLM_TASKS_ERROR_FILE_NAME)


def get_all_llm_task_results(eval_set_dir: str, testcase: str, fail_on_missing: bool = False) -> List[LlmTaskResult]:
    """
    Get the results of the llm tasks run, that is the results of the calls to your llm models.

    Args:
        eval_set_dir (str): the eval set dir that contains the testcases/{testcase}/LLM_TASKS_RESULT_FILE
        testcase (str): the testcase folder name
        fail_on_missing (bool): if True, raise FileNotFoundError if the results file is not found

    Returns:
        List[LlmRunResult]: the results of the llm task run
    """
    results_file_path = get_llm_task_results_file(eval_set_dir, testcase)
    if not os.path.exists(results_file_path):
        if fail_on_missing:
            raise FileNotFoundError(f'LLM task results file not found at `{results_file_path}`')
        return []

    with open(results_file_path, 'r', encoding='utf-8') as results_file:
        results = [LlmTaskResult.model_validate_json(line) for line in results_file]

    return results


def get_llm_task_result(eval_set_dir: str, testcase: str, llm_task_name: str) -> LlmTaskResult:
    """
    Get the result of a specific llm task run by name and the folder containing the results.

    Args:
        eval_set_dir (str): the eval set dir that contains the testcases/{testcase}/LLM_TASKS_RESULT_FILE
        testcase (str): the testcase folder name
        llm_task_name (str): the name of the llm task result to get

    Raises:
        ValueError: Test case name not found in results

    Returns:
        LlmRunResult: the result of the llm task run
    """
    all_llm_task_results = get_all_llm_task_results(eval_set_dir, testcase)
    results = {result.name: result for result in all_llm_task_results}
    if llm_task_name not in results:
        raise ValueError(f'Test {llm_task_name} not found in results: {list(results.keys())}')

    return results[llm_task_name]


def is_llm_task_result_found(llm_task_results: List[LlmTaskResult], llm_task_name: str) -> bool:
    """
    Check if the llm_task result exists in the llm tasks results file
    """
    results = {result.name: result for result in llm_task_results}
    return llm_task_name in results


def get_eval_result_file(eval_set_dir: str, testcase: str):
    return os.path.join(get_testcase_folder(eval_set_dir, testcase), EVAL_RESULTS_FILE)


def get_eval_errors_file(eval_set_dir: str, testcase: str):
    return os.path.join(get_testcase_folder(eval_set_dir, testcase), EVAL_ERROR_FILE_NAME)


def get_eval_set_name(eval_set_dir: str) -> str:
    return os.path.basename(eval_set_dir)


def get_all_eval_results(eval_set_dir: str, testcase: str, fail_on_missing: bool = True) -> List[EvalTestResult]:
    """
    Get the eval results from EVAL_RESULTS_FILE in the testcase folder.

    Args:
        eval_set_dir (str): the eval set dir that contains the testcases/{testcase}/EVAL_RESULTS_FILE
        testcase (str): the testcase folder name

    Raises:
        FileNotFoundError: EVAL_RESULTS_FILE not found in folder

    Returns:
        List[EvalResultSchema]: the eval results
    """
    eval_results_file = get_eval_result_file(eval_set_dir, testcase)
    return get_all_eval_results_from_file(eval_results_file=eval_results_file, fail_on_missing=fail_on_missing)


def get_all_eval_results_from_file(eval_results_file: str, fail_on_missing: bool = True) -> List[EvalTestResult]:
    if not os.path.exists(eval_results_file):
        if fail_on_missing:
            raise FileNotFoundError(f'Eval results file not found at {eval_results_file}')
        return []

    with open(eval_results_file, 'r', encoding='utf-8') as results_file:
        results = [EvalTestResult.model_validate_json(line) for line in results_file]

    return results


def get_eval_results_sorted_by_name_metric(eval_set_dir: str, testcase: str) -> List[EvalTestResult]:  # -> list:# -> list:
    """
    Returns the eval results sorted by <testcase name>:<metric>
    This is used later to sort and compare between two different runs.

    Args:
        eval_set_dir (str): the eval set dir that contains the testcases/{testcase}/LLM_TASKS_RESULT_FILE
        testcase (str): the testcase folder name

    Returns:
        List[Dict]: List of dictionaries of <llm-task name>-<metric> to result
    """
    top_level_results: List[EvalTestResult] = get_all_eval_results(eval_set_dir=eval_set_dir, testcase=testcase)
    return _sort_eval_test_results(top_level_results)


def get_eval_results_sorted_by_name_metric_from_file(eval_results_file: str) -> List[EvalTestResult]:  # -> list:# -> list:
    top_level_results: List[EvalTestResult] = get_all_eval_results_from_file(eval_results_file)
    return _sort_eval_test_results(top_level_results)


def _sort_eval_test_results(results: List[EvalTestResult]):
    return sorted(results, key=lambda x: x.name_metric)


def eval_result_found(eval_results: List[EvalTestResult], eval_task: EvalTask) -> bool:
    """
    Check if the eval result exists in the EVAL_RESULTS_FILE
    """

    results_by_name = {result.name_metric: result for result in eval_results}
    return eval_task.name_metric in results_by_name


def get_all_testcases(eval_dir: str) -> List[str]:
    testcases_folder = os.path.join(eval_dir, TESTCASES_FOLDER)
    if not os.path.exists(testcases_folder):
        raise FileNotFoundError(f'testcases folder not found at {testcases_folder}')

    sub_folders = [folder for folder in os.listdir(testcases_folder) if os.path.isdir(os.path.join(testcases_folder, folder))]
    testcase_folders = [folder for folder in sub_folders if not os.path.isfile(os.path.join(folder, EVAL_RESULTS_FILE))]

    return testcase_folders
