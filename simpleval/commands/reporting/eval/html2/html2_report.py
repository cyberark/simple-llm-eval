import html
import json
import logging
import os
from typing import List

from simpleval.commands.reporting.eval.html_common import save_html_report
from simpleval.consts import LOGGER_NAME
from simpleval.evaluation.metrics.calc import MeanScores
from simpleval.evaluation.schemas.eval_result_schema import EvalTestResult

EVAL_TESTCASE_TITLE_PLACEHOLDER = '"EVAL_TESTCASE_TITLE_PLACEHOLDER"'
DATA_ITEMS_PLACEHOLDER = '"DATA_ITEMS_PLACEHOLDER"'
AGGREGATE_METRIC_PLACEHOLDER = '"AGGREGATE_DATA_PLACEHOLDER"'
LLM_ERRORS_PLACEHOLDER = 'llmErrors: 0'
EVAL_ERRORS_PLACEHOLDER = 'evalErrors: 0'
ERRORS_BANNER_PLACEHOLDER = 'bg-yellow-500 text-yellow-900 p-4 mb-4 rounded-md'
HIDDEN = 'hidden'
HIDDEN_ERRORS_BANNER = f'{ERRORS_BANNER_PLACEHOLDER} ${{"{HIDDEN}"}}'


def _generate_html_report2(
    name: str,
    testcase: str,
    eval_results: List[EvalTestResult],
    mean_scores: MeanScores,
    llm_task_errors_count: int,
    eval_errors_count: int,
) -> str:
    template_path = os.path.join(os.path.dirname(__file__), 'llm_eval_report_template.html')
    with open(template_path, 'r', encoding='utf-8') as file:
        llm_eval_report_template = file.read()

    _validate_eval_html_template(llm_eval_report_template)

    html_content = llm_eval_report_template.replace(EVAL_TESTCASE_TITLE_PLACEHOLDER, f'"{name}: {testcase}"')

    html_content = html_content.replace(DATA_ITEMS_PLACEHOLDER, _get_js_results_list(eval_results))

    aggregate_scores = _get_js_aggregate_scores(mean_scores=mean_scores)
    html_content = html_content.replace(AGGREGATE_METRIC_PLACEHOLDER, aggregate_scores)

    html_content = html_content.replace(LLM_ERRORS_PLACEHOLDER, f'llmErrors:{llm_task_errors_count}')
    html_content = html_content.replace(EVAL_ERRORS_PLACEHOLDER, f'evalErrors:{eval_errors_count}')

    if llm_task_errors_count != 0 or eval_errors_count != 0:
        html_content = html_content.replace(HIDDEN_ERRORS_BANNER, f'{ERRORS_BANNER_PLACEHOLDER}')

    return save_html_report(name=name, testcase=testcase, html_content=html_content)


def _validate_eval_html_template(llm_eval_report_template: str) -> None:
    if EVAL_TESTCASE_TITLE_PLACEHOLDER not in llm_eval_report_template:
        raise ValueError('HTML Report: Eval template does not contain testcase title placeholder')

    if DATA_ITEMS_PLACEHOLDER not in llm_eval_report_template:
        raise ValueError('HTML Report: Eval template does not contain data items placeholder')

    if AGGREGATE_METRIC_PLACEHOLDER not in llm_eval_report_template:
        raise ValueError('HTML Report: Eval template does not contain aggregate metric placeholder')

    if LLM_ERRORS_PLACEHOLDER not in llm_eval_report_template:
        raise ValueError('HTML Report: Eval template does not contain the llm errors placeholder')

    if EVAL_ERRORS_PLACEHOLDER not in llm_eval_report_template:
        raise ValueError('HTML Report: Eval template does not contain the eval errors placeholder')

    if HIDDEN_ERRORS_BANNER not in llm_eval_report_template:
        raise ValueError('HTML Report: Eval template does not contain hidden errors banner placeholder')


def _escape_quotes(text: str) -> str:
    return text.replace('"', '`')


def _get_js_aggregate_scores(mean_scores: MeanScores) -> str:
    logger = logging.getLogger(LOGGER_NAME)

    metric_means = mean_scores.metrics
    metric_means_values = {metric: {'mean': scores.mean, 'std_dev': scores.std_dev} for metric, scores in metric_means.items()}

    js_aggregate_scores = ''

    for metric, scores in metric_means_values.items():
        metric_name = _escape_quotes(metric.replace(' ', '_'))
        js_aggregate_scores += f'{metric_name}: [{scores["mean"]}, {scores["std_dev"]}],'

    js_aggregate_scores += f'AggregateScore: [{mean_scores.aggregate_mean}, {mean_scores.aggregate_std_dev}],'

    logger.debug(f'JS Aggregate Scores: {js_aggregate_scores}')
    return f'{{{js_aggregate_scores}}}'


def _get_js_results_list(eval_results: List[EvalTestResult]) -> str:
    logger = logging.getLogger(LOGGER_NAME)

    js_results_array = ''
    for i, result in enumerate(eval_results, start=1):
        name_metric = _escape_quotes(result.name_metric)
        prompt = _escape_quotes(result.llm_run_result.prompt)
        llm_response = _escape_quotes(result.llm_run_result.prediction)
        expected_llm_response = _escape_quotes(result.llm_run_result.expected_prediction)
        explanation = _escape_quotes(result.explanation)

        item_dict = dict(
            id=i,
            testName=name_metric,
            promptToLLM=prompt,
            llmResponse=html.escape(llm_response),
            expectedLLMResponse=expected_llm_response,
            evalResult=html.escape(result.result),
            normalizedScore=result.normalized_score,
            scoreExplanation=html.escape(explanation),
        )
        js_results_array += f'{json.dumps(item_dict)},'

    logger.debug(f'JS Results Array: {js_results_array}')
    return f'[{js_results_array}]'
