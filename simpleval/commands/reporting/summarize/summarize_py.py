import logging
import os
from typing import List

import matplotlib
from matplotlib import pyplot as plt

from simpleval.consts import LOGGER_NAME
from simpleval.evaluation.metrics.calc import MeanScores


def plot_scores_py(testcases: List[str], scores: List[MeanScores], primary_metric: str):

    logger = logging.getLogger(LOGGER_NAME)

    if primary_metric:
        logger.info(f'Sorting by metric: {primary_metric}')
        sorted_indices = sorted(range(len(testcases)), key=lambda i: scores[i].metrics[primary_metric].mean, reverse=False)
        testcases = [testcases[i] for i in sorted_indices]
        scores = [scores[i] for i in sorted_indices]

    metrics = scores[0].metrics.keys()  # Assuming all scores have the same metrics
    num_metrics = len(metrics)

    logger = logging.getLogger(LOGGER_NAME)
    logger.debug(f'Metrics: {metrics}')

    fig, axes = plt.subplots((num_metrics + 3) // 4, 4, figsize=(20, 12), sharey=True)
    axes = axes.flatten()  # Flatten axes for easy iteration

    _plot_metric_bars(axes, metrics, scores, testcases)

    # Remove any unused subplots
    for j in range(num_metrics, len(axes)):
        fig.delaxes(axes[j])

    fig.suptitle('Evaluation Metrics by Testcase', fontsize=16)
    plt.tight_layout()

    matplotlib.rcParams['savefig.directory'] = os.getcwd()
    plt.show()


def _plot_metric_bars(axes, metrics, scores, testcases):
    for i, metric in enumerate(metrics):
        metric_scores = [score.metrics[metric].mean for score in scores]
        axes[i].barh(testcases, metric_scores, color=plt.cm.tab10.colors)
        axes[i].set_title(metric, fontsize=10)
        axes[i].set_xlim(0, 1)
        axes[i].grid(axis='x', linestyle='--', alpha=0.6)
        if i % 4 == 0:
            axes[i].set_ylabel('Testcases')  # Set ylabel for the first column
        axes[i].set_xlabel('Scores', fontsize=8)
