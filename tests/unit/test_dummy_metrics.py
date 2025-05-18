from simpleval.evaluation.judges.judge_provider import JudgeProvider
from simpleval.evaluation.metrics.models.test_metric.dummy import DummyMetric


def test_completeness_metric():
    judge = JudgeProvider.get_judge('dummy_judge')
    metric = judge.get_metric('completeness')
    assert metric.possible_responses == [str(i) for i in range(1, 11)]

    result = judge.evaluate(metric_name='completeness', prompt='prompt', prediction='prediction')
    assert result.result
    assert 0 <= result.normalized_score <= 1


def test_dummy_metric():
    judge = JudgeProvider.get_judge('dummy_judge')
    metric = judge.get_metric('dummy')

    assert metric.possible_responses == [str(i) for i in range(1, 11)]

    result = judge.evaluate(metric_name='dummy', prompt='prompt', prediction='prediction')
    assert result.result
    assert 0 <= result.normalized_score <= 1
