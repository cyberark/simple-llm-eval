import html
import json
import logging
import os
import webbrowser
from datetime import datetime

from simpleval.commands.reporting.compare.common import CompareArgs
from simpleval.consts import LOGGER_NAME, RESULTS_FOLDER

EVAL_SET_NAME_PLACEHOLDER = 'EVAL-SET-PLACEHOLDER'
AGGREGATE_DATA_LEFT_SIDE_PLACEHOLDER = '"AGGREGATE_DATA_LEFT_SIDE_PLACEHOLDER"'
AGGREGATE_DATA_RIGHT_SIDE_PLACEHOLDER = '"AGGREGATE_DATA_RIGHT_SIDE_PLACEHOLDER"'
DATA_ITEMS_PLACEHOLDER = '"DATA_ITEMS_PLACEHOLDER"'


def _compare_results_html2(eval_set: str, left_side: CompareArgs, right_side: CompareArgs):
    template_path = os.path.join(os.path.dirname(__file__), 'compare_report_template.html')
    with open(template_path, 'r', encoding='utf-8') as file:
        compare_report_template = file.read()

    _validate_compare_html_template(compare_report_template)

    html_content = _populate_template(eval_set=eval_set, template=compare_report_template, left_side=left_side, right_side=right_side)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    folder = RESULTS_FOLDER
    file_name = f'comparison_report_{left_side.name}_vs_{right_side.name}_{timestamp}.html'.replace(':', '_')
    file_path = os.path.join(folder, file_name)
    os.makedirs(folder, exist_ok=True)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    logging.getLogger(LOGGER_NAME).info(f'Report saved to {file_path}')
    full_path = os.path.abspath(file_path)
    webbrowser.open(f'file://{full_path}')
    return file_path


def _validate_compare_html_template(template: str):
    if DATA_ITEMS_PLACEHOLDER not in template:
        raise ValueError('HTML Report: Compare template does not contain data items placeholder')

    if AGGREGATE_DATA_LEFT_SIDE_PLACEHOLDER not in template:
        raise ValueError('HTML Report: Compare template does not contain left side aggregate data placeholders')

    if AGGREGATE_DATA_RIGHT_SIDE_PLACEHOLDER not in template:
        raise ValueError('HTML Report: Compare template does not contain right side aggregate data placeholders')


def _populate_template(eval_set: str, template: str, left_side: CompareArgs, right_side: CompareArgs):
    html_content = template.replace(EVAL_SET_NAME_PLACEHOLDER, eval_set)
    html_content = html_content.replace(AGGREGATE_DATA_LEFT_SIDE_PLACEHOLDER, _get_js_aggregate_scores(left_side))
    html_content = html_content.replace(AGGREGATE_DATA_RIGHT_SIDE_PLACEHOLDER, _get_js_aggregate_scores(right_side))
    html_content = html_content.replace(DATA_ITEMS_PLACEHOLDER, _get_js_data_items_list(left_side, right_side))

    return html_content


def _get_js_aggregate_scores(comparable: CompareArgs) -> str:
    left_testcase = _testcase_name_from_comparable_name(comparable.name)
    comparable_dict = dict(
        testcase=left_testcase,
        metrics=[dict(metric=metric, score=scores.mean) for metric, scores in comparable.mean_scores.metrics.items()],
    )

    comparable_dict['metrics'].append(dict(metric='aggregate mean', score=comparable.mean_scores.aggregate_mean))

    return json.dumps(comparable_dict)


def _get_js_data_items_list(left_side: CompareArgs, right_side: CompareArgs) -> str:
    left_testcase = _testcase_name_from_comparable_name(left_side.name)
    right_testcase = _testcase_name_from_comparable_name(right_side.name)

    data = []
    for left_result, right_result in zip(left_side.sorted_results, right_side.sorted_results):
        rows = [
            {
                'testCaseTest': f'{left_testcase}:{left_result.llm_run_result.name}',
                'promptToLLM': left_result.llm_run_result.prompt,
                'llmResponse': html.escape(left_result.llm_run_result.prediction),
                'expectedLLMResponse': left_result.llm_run_result.expected_prediction,
                'normalizedScore': left_result.normalized_score,
                'evalResult': html.escape(left_result.result),
                'explanation': html.escape(left_result.explanation),
            },
            {
                'testCaseTest': f'{right_testcase}:{right_result.llm_run_result.name}',
                'promptToLLM': right_result.llm_run_result.prompt,
                'llmResponse': html.escape(right_result.llm_run_result.prediction),
                'expectedLLMResponse': right_result.llm_run_result.expected_prediction,
                'normalizedScore': right_result.normalized_score,
                'evalResult': html.escape(right_result.result),
                'explanation': html.escape(right_result.explanation),
            },
        ]
        data.append({'metric': left_result.metric, 'rows': rows})

    return json.dumps(data)


def _testcase_name_from_comparable_name(comparable_name: str):
    return comparable_name.split(':')[1]
