import logging
from typing import List

from simpleval.commands.reporting.eval.console_report import _print_to_console
from simpleval.commands.reporting.eval.html2.html2_report import _generate_html_report2
from simpleval.consts import LOGGER_NAME, ReportFormat
from simpleval.evaluation.metrics.calc import MeanScores, calc_scores
from simpleval.evaluation.schemas.eval_result_schema import EvalTestResult


class ResultsManager:
    def __init__(self, red_threshold: float = 0.3, yellow_threshold: float = 0.7):
        self.red_threshold = red_threshold
        self.yellow_threshold = yellow_threshold
        self.logger = logging.getLogger(LOGGER_NAME)

    def display_results(
        self,
        name: str,
        testcase: str,
        eval_results: List[EvalTestResult],
        llm_tasks_errors_count: int,
        eval_errors_count: int,
        output_format: str = ReportFormat.HTML,
    ):
        # Sort eval_results by "<test_name>-<metric>"
        eval_results.sort(key=lambda x: x.name_metric)

        mean_scores: MeanScores = calc_scores(eval_results)

        html_report_file = ''
        if output_format == ReportFormat.HTML:
            html_report_file = _generate_html_report2(
                name=name,
                testcase=testcase,
                eval_results=eval_results,
                mean_scores=mean_scores,
                llm_task_errors_count=llm_tasks_errors_count,
                eval_errors_count=eval_errors_count,
            )
        elif output_format == ReportFormat.CONSOLE:
            _print_to_console(
                name=name,
                testcase=testcase,
                eval_results=eval_results,
                metric_means=mean_scores.metrics,
                aggregate_mean=mean_scores.aggregate_mean,
                llm_task_errors_count=llm_tasks_errors_count,
                eval_errors_count=eval_errors_count,
                yellow_threshold=self.yellow_threshold,
                red_threshold=self.red_threshold,
            )
        else:
            self.logger.error(f'Unsupported output format: {output_format}')

        return html_report_file
