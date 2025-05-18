from math import isclose
from statistics import mean, stdev

from simpleval.evaluation.metrics.calc import MeanScores, Scores, calc_scores
from simpleval.evaluation.schemas.eval_result_schema import EvalTestResult
from simpleval.testcases.schemas.llm_task_result import LlmTaskResult

dummy_args = {'explanation': 'foo', 'result': 'foo', 'llm_run_result': LlmTaskResult(name='foo', prompt='bar', prediction='foo')}


def test_calc_scores_single_metric():
    scores = [0.8, 0.9]
    eval_results = [
        EvalTestResult(name='foo', metric='accuracy', normalized_score=scores[0], **dummy_args),
        EvalTestResult(name='foo', metric='accuracy', normalized_score=scores[1], **dummy_args)
    ]

    result = calc_scores(eval_results)
    assert isclose(result.aggregate_mean, round(mean(scores), 2))
    assert isclose(result.aggregate_std_dev, round(stdev(scores), 2))
    assert len(result.metrics) == 1
    assert isclose(result.metrics['accuracy'].mean, round(mean(scores), 2))
    assert isclose(result.metrics['accuracy'].std_dev, round(stdev(scores), 2))


def test_calc_scores_multiple_metrics():
    scores_accuracy = [0.8, 0.9]
    scores_precision = [0.7, 0.6]
    eval_results = [
        EvalTestResult(name='foo', metric='accuracy', normalized_score=scores_accuracy[0], **dummy_args),
        EvalTestResult(name='foo', metric='precision', normalized_score=scores_precision[0], **dummy_args),
        EvalTestResult(name='foo', metric='accuracy', normalized_score=scores_accuracy[1], **dummy_args),
        EvalTestResult(name='foo', metric='precision', normalized_score=scores_precision[1], **dummy_args)
    ]

    result = calc_scores(eval_results)
    assert isclose(result.aggregate_mean, round(mean(scores_accuracy + scores_precision), 2))
    assert isclose(result.aggregate_std_dev, round(stdev(scores_accuracy + scores_precision), 2))
    assert len(result.metrics) == 2
    assert isclose(result.metrics['accuracy'].mean, round(mean(scores_accuracy), 2))
    assert isclose(result.metrics['accuracy'].std_dev, round(stdev(scores_accuracy), 2))
    assert isclose(result.metrics['precision'].mean, round(mean(scores_precision), 2))
    assert isclose(result.metrics['precision'].std_dev, round(stdev(scores_precision), 2))


def test_calc_scores_empty():
    eval_results = []
    result = calc_scores(eval_results)
    assert result == MeanScores(metrics={}, aggregate_mean=0, aggregate_std_dev=0)


def test_calc_scores_one_score_same_metric():
    scores = [0.8]
    eval_results = [
        EvalTestResult(name='foo', metric='accuracy', normalized_score=scores[0], **dummy_args),
    ]
    result = calc_scores(eval_results)
    assert isclose(result.aggregate_mean, round(mean(scores), 2))
    assert isclose(result.aggregate_std_dev, 0)  # std dev needs at least 2 samples
    assert len(result.metrics) == 1
    assert isclose(result.metrics['accuracy'].mean, round(mean(scores), 2))
    assert isclose(result.metrics['accuracy'].std_dev, 0)  # std dev needs at least 2 samples


def test_calc_scores_multiple_testcases_same_metric():
    scores = [0.8, 0.9, 0.85]
    eval_results = [
        EvalTestResult(name='foo', metric='accuracy', normalized_score=scores[0], **dummy_args),
        EvalTestResult(name='bar', metric='accuracy', normalized_score=scores[1], **dummy_args),
        EvalTestResult(name='baz', metric='accuracy', normalized_score=scores[2], **dummy_args)
    ]
    result = calc_scores(eval_results)
    assert isclose(result.aggregate_mean, round(mean(scores), 2))
    assert isclose(result.aggregate_std_dev, round(stdev(scores), 2))
    assert len(result.metrics) == 1
    assert isclose(result.metrics['accuracy'].mean, round(mean(scores), 2))
    assert isclose(result.metrics['accuracy'].std_dev, round(stdev(scores), 2))
