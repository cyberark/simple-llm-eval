from collections import defaultdict
from statistics import mean, stdev
from typing import Dict, List

from pydantic import BaseModel

from simpleval.evaluation.schemas.eval_result_schema import EvalTestResult


class Scores(BaseModel):
    mean: float
    std_dev: float


class MeanScores(BaseModel):
    metrics: Dict[str, Scores]
    aggregate_mean: float
    aggregate_std_dev: float


def calc_scores(eval_results: List[EvalTestResult]) -> MeanScores:
    """_summary_

    Args:
        eval_results (List[EvalResultSchema]): _description_

    Returns:
        MeanScores: Metric name to mean score dict, total mean score over all metrics
    """

    metric_scores = defaultdict(list)
    total_score = 0
    total_count = 0
    total_scores = []

    for result in eval_results:
        metric_scores[result.metric].append(result.normalized_score)
        total_score += result.normalized_score
        total_count += 1
        total_scores.append(result.normalized_score)

    metrics_means = {}
    for metric, scores in metric_scores.items():
        metrics_means[metric] = Scores(
            mean=round(mean(scores), 2) if len(scores) > 0 else 0,
            std_dev=round(stdev(scores), 2) if len(scores) > 1 else 0,
        )

    aggregate_mean = round(total_score / total_count, 2) if total_count > 0 else 0
    aggregate_std_dev = round(stdev(total_scores), 2) if total_count > 1 else 0

    return MeanScores(metrics=metrics_means, aggregate_mean=aggregate_mean, aggregate_std_dev=aggregate_std_dev)
