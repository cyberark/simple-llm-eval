import logging
import os
from pathlib import Path
from typing import List

from colorama import Fore
from pydantic import ValidationError

from simpleval.commands.reporting.compare.common import CompareArgs
from simpleval.commands.reporting.compare.compare_console import _compare_results_console
from simpleval.commands.reporting.compare.compare_html2.compare_html2 import _compare_results_html2
from simpleval.consts import LOGGER_NAME, ReportFormat
from simpleval.evaluation.metrics.calc import MeanScores, calc_scores
from simpleval.evaluation.utils import (
    get_all_eval_results,
    get_all_eval_results_from_file,
    get_eval_results_sorted_by_name_metric,
    get_eval_results_sorted_by_name_metric_from_file,
    get_eval_set_name,
    get_llm_task_results_file,
)
from simpleval.exceptions import TerminationError


def compare_results(eval_set_dir: str, testcase1: str, testcase2: str, report_format: str, ignore_missing_llm_results: bool = False):
    logger = logging.getLogger(LOGGER_NAME)

    try:
        results1 = get_llm_task_results_file(eval_set_dir=eval_set_dir, testcase=testcase1)
        results2 = get_llm_task_results_file(eval_set_dir=eval_set_dir, testcase=testcase2)

        logger.info(f'{Fore.GREEN}Comparing results between:{Fore.RESET}')
        logger.info(f'{Fore.GREEN}1. {results1}{Fore.RESET}')
        logger.info(f'{Fore.GREEN}2. {results2}{Fore.RESET}')

        if not os.path.exists(results1) and not ignore_missing_llm_results:
            raise FileNotFoundError(f'{results1} does not exist.')
        if not os.path.exists(results2) and not ignore_missing_llm_results:
            raise FileNotFoundError(f'{results2} does not exist.')

        mean_scores1: MeanScores = calc_scores(get_all_eval_results(eval_set_dir=eval_set_dir, testcase=testcase1))
        mean_scores2: MeanScores = calc_scores(get_all_eval_results(eval_set_dir=eval_set_dir, testcase=testcase2))

        eval_results1_sorted = get_eval_results_sorted_by_name_metric(eval_set_dir=eval_set_dir, testcase=testcase1)
        eval_results2_sorted = get_eval_results_sorted_by_name_metric(eval_set_dir=eval_set_dir, testcase=testcase2)

        _verify_input(eval_results1_sorted, eval_results2_sorted)

        eval_set_name = get_eval_set_name(eval_set_dir)

        # html compare report requires the testcase name in this format:
        name1 = f'{eval_set_name}:{testcase1}'
        name2 = f'{eval_set_name}:{testcase2}'
        left_side = CompareArgs(name=name1, mean_scores=mean_scores1, sorted_results=eval_results1_sorted)
        right_side = CompareArgs(name=name2, mean_scores=mean_scores2, sorted_results=eval_results2_sorted)

        logger.info(f'{Fore.GREEN}Eval results verified. Comparing...\n{Fore.RESET}')
        _compare_results_report(eval_set=eval_set_name, left_side=left_side, right_side=right_side, output_format=report_format)

    except (FileNotFoundError, ValidationError, ValueError) as ex:
        raise TerminationError(f'Error occurred trying to compare results: {ex}') from ex


def compare_results_files(name: str, eval_results_file1: str, eval_results_file2: str, report_format: str):
    logger = logging.getLogger(LOGGER_NAME)

    try:
        logger.info(f'{Fore.GREEN}Comparing results between:{Fore.RESET}')
        logger.info(f'{Fore.GREEN}1. {eval_results_file1}{Fore.RESET}')
        logger.info(f'{Fore.GREEN}2. {eval_results_file2}{Fore.RESET}')

        mean_scores1: MeanScores = calc_scores(get_all_eval_results_from_file(eval_results_file1))
        mean_scores2: MeanScores = calc_scores(get_all_eval_results_from_file(eval_results_file2))

        eval_results1_sorted = get_eval_results_sorted_by_name_metric_from_file(eval_results_file1)
        eval_results2_sorted = get_eval_results_sorted_by_name_metric_from_file(eval_results_file2)

        _verify_input(eval_results1_sorted, eval_results2_sorted)

        testcase1 = str(Path(eval_results_file1).stem)
        testcase2 = str(Path(eval_results_file2).stem)

        # html compare report requires the testcase name in this format:
        name1 = f'{name}:{testcase1}'
        name2 = f'{name}:{testcase2}'
        left_side = CompareArgs(name=name1, mean_scores=mean_scores1, sorted_results=eval_results1_sorted)
        right_side = CompareArgs(name=name2, mean_scores=mean_scores2, sorted_results=eval_results2_sorted)

        logger.info(f'{Fore.GREEN}Eval results verified. Comparing...\n{Fore.RESET}')
        _compare_results_report(eval_set=name, left_side=left_side, right_side=right_side, output_format=report_format)

    except (FileNotFoundError, ValidationError, ValueError) as ex:
        raise TerminationError(f'Error occurred trying to compare results: {ex}') from ex


def _verify_input(sorted_results1: List, sorted_results2: List):
    if len(sorted_results1) != len(sorted_results2):
        raise ValueError(f'Number of results in the two directories are different: {len(sorted_results1)} vs {len(sorted_results2)}')

    for result1, result2 in zip(sorted_results1, sorted_results2):
        if result1.name_metric != result2.name_metric:
            raise ValueError(f'Eval result name-metric are different. {result1.name_metric=} vs {result2.name_metric=}')


def _compare_results_report(eval_set: str, left_side: CompareArgs, right_side: CompareArgs, output_format: str):
    if output_format == ReportFormat.CONSOLE:
        _compare_results_console(left_side=left_side, right_side=right_side)
    elif output_format == ReportFormat.HTML:
        _compare_results_html2(eval_set=eval_set, left_side=left_side, right_side=right_side)
    else:
        raise ValueError(f'Invalid report format: {output_format}')
