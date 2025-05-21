import json
import logging
from typing import List

from simpleval.consts import LOGGER_NAME
from simpleval.evaluation.judges.base_judge import BaseJudge
from simpleval.evaluation.judges.judge_provider import JudgeProvider
from simpleval.evaluation.metrics.metric_result_schema import MetricResult
from simpleval.evaluation.schemas.eva_task_schema import EvalTask
from simpleval.evaluation.schemas.eval_result_schema import EvalTestResult
from simpleval.evaluation.schemas.eval_task_config_schema import EvalTaskConfig
from simpleval.evaluation.utils import (
    eval_result_found,
    get_all_eval_results,
    get_eval_config,
    get_eval_ground_truth,
    get_eval_result_file,
    get_llm_task_result,
    get_testcase_folder,
    highlight_regex,
)
from simpleval.parallel_runner.parallel_runner import BaseRunner
from simpleval.parallel_runner.schemas import TaskParams, TaskResult


def run_eval(eval_dir: str, config_file: str, testcase: str):
    logger = logging.getLogger(LOGGER_NAME)
    logger.info(f'Running evaluation for {eval_dir}:{testcase}, {config_file=}')

    eval_config = get_eval_config(eval_dir=eval_dir, config_file=config_file)
    logger.debug(f'Eval config: {eval_config}')

    existing_eval_results: List[EvalTestResult] = get_all_eval_results(eval_set_dir=eval_dir, testcase=testcase, fail_on_missing=False)

    all_evals_to_run = _get_all_evals_by_metric_to_run(eval_dir=eval_dir, eval_config=eval_config)
    evals_to_run = filter_existing_eval_results(existing_eval_results, all_evals_to_run=all_evals_to_run)

    if not evals_to_run:
        logger.debug('All evaluations already run')
        return existing_eval_results, []

    tasks_to_run = [TaskParams(task_name=eval_case.name_metric, payload=eval_case) for eval_case in evals_to_run]

    max_concurrent_judge_tasks = eval_config.effective_max_concurrent_judge_tasks(testcase)
    logger.info(f'Max concurrent judge tasks: {max_concurrent_judge_tasks}')

    judge: BaseJudge = JudgeProvider.get_judge(eval_config.llm_as_a_judge_name)
    judge.run_preliminary_checks()

    runner = EvalRunner(max_concurrent_judge_tasks)
    results, errors = runner.run_tasks(
        tasks=tasks_to_run,
        task_function=lambda task, _: _run_llm_as_a_judge(task, eval_dir, testcase, eval_config),
        task_config=None,
    )

    results.extend(existing_eval_results)
    _write_results_to_file(eval_dir, testcase, results)
    return results, errors


def filter_existing_eval_results(existing_eval_results: List[EvalTestResult], all_evals_to_run: List[EvalTask]) -> List[EvalTask]:
    logger = logging.getLogger(LOGGER_NAME)

    if not existing_eval_results:
        return all_evals_to_run

    logger.debug(f'filter_existing_eval_results: {existing_eval_results=}, {all_evals_to_run=}')

    evals_to_run_filtered = [eval_task for eval_task in all_evals_to_run if not eval_result_found(existing_eval_results, eval_task)]
    return evals_to_run_filtered


def _get_all_evals_by_metric_to_run(eval_dir: str, eval_config) -> List[EvalTask]:
    all_eval_cases = get_eval_ground_truth(eval_dir)

    evals_to_run = []
    for eval_case in all_eval_cases:
        for metric in eval_config.eval_metrics:
            evals_to_run.append(EvalTask(metric=metric, ground_truth=eval_case))
    return evals_to_run


def _write_results_to_file(eval_dir: str, testcase: str, results: List[EvalTestResult]):
    eval_results_file_path = get_eval_result_file(eval_set_dir=eval_dir, testcase=testcase)
    with open(eval_results_file_path, 'w', encoding='utf-8') as results_file:
        for result in results:
            results_file.write(json.dumps(result.model_dump()) + '\n')


def _run_llm_as_a_judge(task: EvalTask, eval_dir: str, testcase: str, eval_config: EvalTaskConfig) -> EvalTestResult:
    logger = logging.getLogger(LOGGER_NAME)

    test_name = task.ground_truth.name
    testcase_folder = get_testcase_folder(eval_set_dir=eval_dir, testcase=testcase)
    logger.info(f'Evaluating test case in {testcase_folder}, name: {test_name}, evaluation metric: {task.metric}')

    judge_name = eval_config.llm_as_a_judge_name
    judge_model_id = eval_config.llm_as_a_judge_model_id

    judge: BaseJudge = JudgeProvider.get_judge(judge_name=judge_name, model_id=judge_model_id)

    llm_task_result = get_llm_task_result(eval_set_dir=eval_dir, testcase=testcase, llm_task_name=test_name)
    ground_truth = llm_task_result.expected_prediction

    result: MetricResult = judge.evaluate(
        metric_name=task.metric, prompt=llm_task_result.prompt, prediction=llm_task_result.prediction, ground_truth=ground_truth
    )
    logger.debug(f'Eval result: {result}')

    eval_result = EvalTestResult(
        metric=task.metric,
        result=result.result,
        explanation=result.explanation,
        normalized_score=result.normalized_score,
        llm_run_result=llm_task_result,
    )

    return TaskResult(task_name=eval_result.name_metric, result=eval_result)


class EvalRunner(BaseRunner):
    def __init__(self, max_concurrent_tasks: int):
        super().__init__(max_concurrent_tasks)
        self.logger = logging.getLogger(LOGGER_NAME)

    def process_results(self, results: List[EvalTestResult], errors: List[str]):
        self.logger.debug('')
        self.logger.debug('Evaluation results:')
        self.logger.debug('-' * 50)

        for result in results:
            self.logger.debug(f'Metric test: {result.name_metric}')
            self.logger.debug('Metric test results: ')
            results_string = str(result)
            results_string = highlight_regex(results_string, r"result='.*?'")
            results_string = highlight_regex(results_string, r'normalized_score=\d+(\.\d+)?')
            self.logger.debug(results_string)
            self.logger.debug('=' * 50)

        if errors:
            self.logger.error(f'Errors occurred during evaluation. {len(errors)} error(s) found.')

        for error in errors:
            self.logger.error(f'Error running tests case: {error}')
