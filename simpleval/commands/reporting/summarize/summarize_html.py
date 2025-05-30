import json
import logging
import os
import webbrowser
from datetime import datetime
from typing import Dict, List

from simpleval.consts import LOGGER_NAME, RESULTS_FOLDER
from simpleval.evaluation.metrics.calc import MeanScores
from simpleval.evaluation.utils import get_eval_name

DATASETS_PLACEHOLDER = '"DATASETS_PLACEHOLDER"'


def plot_scores_html(eval_dir: str, config_file: str, testcases: List[str], scores: List[MeanScores], primary_metric: str):
    logger = logging.getLogger(LOGGER_NAME)
    eval_name = get_eval_name(eval_dir=eval_dir, config_file=config_file)

    testcase_to_score = {testcase: score for testcase, score in zip(testcases, scores)}
    logger.debug(f'Scores: {scores}')

    metrics = scores[0].metrics.keys()

    datasets = [{metric_name: []} for metric_name in metrics]
    logger.debug(f'Datasets: {datasets}')

    for dataset in datasets:
        metric_name = list(dataset.keys())[0]
        for testcase in testcases:
            testcase_score_item = {
                metric_name: testcase_to_score[testcase].metrics[metric_name].mean,
                'testcase': testcase,
            }
            dataset[metric_name].append(testcase_score_item)

        dataset[metric_name].sort(key=lambda x: x[metric_name], reverse=True)

    logger.debug(f'Datasets before primary_metric: {datasets}, {primary_metric=}')

    if primary_metric:
        primary_metric_index = _get_dataset_index_by_metric(primary_metric, datasets)
        primary_dataset = datasets.pop(primary_metric_index)
        datasets.insert(0, primary_dataset)

    logger.debug(f'Datasets after primary_metric: {datasets}, {primary_metric=}')

    return _write_summary_report(eval_name=eval_name, datasets=datasets)


def _get_dataset_index_by_metric(metric: str, datasets: List[Dict]):
    for i, dataset in enumerate(datasets):
        if metric in dataset:
            return i


def _write_summary_report(eval_name: str, datasets: Dict):
    logger = logging.getLogger(LOGGER_NAME)

    template_path = os.path.join(os.path.dirname(__file__), 'llm_summary_report_template.html')
    with open(template_path, 'r', encoding='utf-8') as file:
        report_template = file.read()

    _validate_summary_html_template(report_template)

    html_content = _populate_template(template=report_template, datasets=datasets)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    folder = RESULTS_FOLDER
    file_name = f'summary_report_{eval_name}_{timestamp}.html'.replace(':', '_')
    file_path = os.path.join(folder, file_name)
    os.makedirs(folder, exist_ok=True)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    logger.info(f'Report saved to {file_path}')
    full_path = os.path.abspath(file_path)
    webbrowser.open(f'file://{full_path}')
    return file_path


def _validate_summary_html_template(report_template: str):
    if DATASETS_PLACEHOLDER not in report_template:
        raise ValueError('HTML Summary Report: template does not contain datasets placeholder')


def _populate_template(template: str, datasets: Dict):
    html_content = template.replace(DATASETS_PLACEHOLDER, json.dumps(datasets))
    return html_content
