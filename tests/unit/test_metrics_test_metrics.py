from simpleval.evaluation.metrics.models.test_metric.completeness import CompletenessMetric
from simpleval.evaluation.metrics.models.test_metric.dummy import DummyMetric


def test_coherence_metric():
    metric = CompletenessMetric()
    in_prompt = 'XYZ123$$!-PROMPT'
    in_prediction = 'XYZ123$$!-PREDICTION'
    prompt = metric.render_eval_prompt(prompt=in_prompt, prediction=in_prediction)
    expected_possible_answers = [str(i) for i in range(1, 11)]

    assert in_prompt in prompt
    assert in_prediction in prompt
    assert metric.possible_responses == expected_possible_answers


def test_dummy_metric():
    metric = DummyMetric()
    in_prompt = 'XYZ123$$!-PROMPT'
    in_prediction = 'XYZ123$$!-PREDICTION'
    prompt = metric.render_eval_prompt(prompt=in_prompt, prediction=in_prediction)
    expected_possible_answers = [str(i) for i in range(1, 11)]

    assert in_prompt in prompt
    assert in_prediction in prompt
    assert metric.possible_responses == expected_possible_answers
