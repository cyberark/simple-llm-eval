import logging

from colorama import Fore

from simpleval.commands.reporting.summarize.summarize_html import plot_scores_html
from simpleval.commands.reporting.summarize.summarize_py import plot_scores_py
from simpleval.consts import LOGGER_NAME, SummaryReportType
from simpleval.evaluation.metrics.calc import calc_scores
from simpleval.evaluation.utils import get_all_eval_results, get_all_testcases
from simpleval.exceptions import TerminationError


def summarize_command(eval_dir: str, config_file: str, primary_metric: str, report_format: str):
    logger = logging.getLogger(LOGGER_NAME)
    logger.info(f'Summarizing evaluation results in {eval_dir}')
    testcases = get_all_testcases(eval_dir)
    logger.info(f'Found {len(testcases)} testcases: {testcases}')

    scores = [calc_scores(get_all_eval_results(eval_set_dir=eval_dir, testcase=testcase)) for testcase in testcases]

    logger.debug(f'Scores: {scores}')

    _verify_primary_metric(primary_metric, scores)

    if report_format == SummaryReportType.PY:
        logger.info(f'{Fore.RED}DEPRECATION: python reports will be removed in future versions, use html instead{Fore.RESET}')
        plot_scores_py(testcases=testcases, scores=scores, primary_metric=primary_metric)
    elif report_format == SummaryReportType.HTML:
        plot_scores_html(eval_dir=eval_dir, config_file=config_file, testcases=testcases, scores=scores, primary_metric=primary_metric)
    else:
        raise TerminationError(f'Invalid summary report type: {report_format}')


def _verify_primary_metric(primary_metric: str, scores: list):
    if primary_metric and primary_metric not in scores[0].metrics:
        raise TerminationError(f'Invalid metric to sort by: {primary_metric}')
