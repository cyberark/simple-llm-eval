import logging

from simpleval.commands.reporting.summarize.summarize_html import plot_scores_html
from simpleval.consts import LOGGER_NAME
from simpleval.evaluation.metrics.calc import calc_scores
from simpleval.evaluation.utils import get_all_eval_results, get_all_testcases
from simpleval.exceptions import TerminationError


def summarize_command(eval_dir: str, config_file: str, primary_metric: str):
    logger = logging.getLogger(LOGGER_NAME)
    logger.info(f'Summarizing evaluation results in {eval_dir}')
    testcases = get_all_testcases(eval_dir)
    logger.info(f'Found {len(testcases)} testcases: {testcases}')

    scores = [calc_scores(get_all_eval_results(eval_set_dir=eval_dir, testcase=testcase)) for testcase in testcases]

    logger.debug(f'Scores: {scores}')

    _verify_primary_metric(primary_metric, scores)

    plot_scores_html(eval_dir=eval_dir, config_file=config_file, testcases=testcases, scores=scores, primary_metric=primary_metric)


def _verify_primary_metric(primary_metric: str, scores: list):
    if primary_metric and primary_metric not in scores[0].metrics:
        raise TerminationError(f'Invalid metric to sort by: {primary_metric}')
