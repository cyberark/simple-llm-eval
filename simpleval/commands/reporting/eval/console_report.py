# pylint: disable=too-many-arguments

import textwrap
from typing import List

from colorama import Fore

from simpleval.commands.reporting.utils import print_table
from simpleval.consts import EVAL_ERROR_FILE_NAME, LLM_TASKS_ERROR_FILE_NAME
from simpleval.evaluation.schemas.eval_result_schema import EvalTestResult

NARROW_COLUMN_WIDTH = 10
WIDE_COLUMN_WIDTH = 20


def _print_to_console(
    name: str,
    testcase,
    eval_results: List[EvalTestResult],
    metric_means: dict,
    aggregate_mean: float,
    llm_task_errors_count: int,
    eval_errors_count: int,
    yellow_threshold: float,
    red_threshold: float,
):
    if not eval_results:
        raise ValueError('No eval results to print when printing console report.')

    headers = [
        '#',
        'LLM Task:Metric',
        'Prompt To LLM',
        'LLM Response',
        'Expected LLM Response',
        'Eval Result',
        'Score',
        'Std dev',
        'Eval Explanation',
    ]
    table = []

    for idx, eval_result in enumerate(eval_results, 1):
        color = _get_color_by_score(score=eval_result.normalized_score, yellow_threshold=yellow_threshold, red_threshold=red_threshold)
        std_dev = metric_means[eval_result.metric].std_dev if eval_result.metric in metric_means else 'N/A'
        table.append(
            [
                f'{color}{idx}{Fore.RESET}',  # None
                f'{color}{textwrap.fill(eval_result.name_metric, width=NARROW_COLUMN_WIDTH)}{Fore.RESET}',
                f'{color}{textwrap.fill(eval_result.llm_run_result.prompt, width=NARROW_COLUMN_WIDTH)}{Fore.RESET}',
                f'{color}{textwrap.fill(eval_result.llm_run_result.prediction, width=NARROW_COLUMN_WIDTH)}{Fore.RESET}'
                f'{color}{textwrap.fill(eval_result.llm_run_result.expected_prediction, width=NARROW_COLUMN_WIDTH)}{Fore.RESET}',
                f'{color}{textwrap.fill(eval_result.result, width=WIDE_COLUMN_WIDTH)}{Fore.RESET}',
                f'{color}{eval_result.normalized_score:.3}{Fore.RESET}',
                f'{color}{std_dev}{Fore.RESET}',
                f'{color}{textwrap.fill(eval_result.explanation, width=WIDE_COLUMN_WIDTH)}{Fore.RESET}',
            ]
        )

    print(f'\n{name} - Evaluation Results, Testcase: {testcase}\n')
    print_table(table=table, headers=headers)

    print('\nScores\n')
    for metric, scores in metric_means.items():
        color = _get_color_by_score(scores.mean, yellow_threshold=yellow_threshold, red_threshold=red_threshold)
        print(f'{color}{metric}: {scores.mean} (std dev: {scores.std_dev}){Fore.RESET}')
    color = _get_color_by_score(aggregate_mean, yellow_threshold=yellow_threshold, red_threshold=red_threshold)
    print(f'{color}Aggregate mean: {aggregate_mean}{Fore.RESET}')

    if llm_task_errors_count > 0 or eval_errors_count > 0:
        print(f'\n{Fore.RED}Testcase errors: {llm_task_errors_count}, Eval errors: {eval_errors_count}.{Fore.RESET}')
        print(f'{Fore.RED}Run again to retry only errors or see {testcase}/{EVAL_ERROR_FILE_NAME}, {LLM_TASKS_ERROR_FILE_NAME}{Fore.RESET}')


def _get_color_by_score(score: float, yellow_threshold: float, red_threshold: float):
    if score < red_threshold:
        return Fore.RED
    if score < yellow_threshold:
        return Fore.YELLOW
    return Fore.GREEN
