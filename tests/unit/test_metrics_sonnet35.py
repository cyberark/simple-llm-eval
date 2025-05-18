from simpleval.evaluation.metrics.models.bedrock_claude_sonnet.coherence import CoherenceMetric
from simpleval.evaluation.metrics.models.bedrock_claude_sonnet.completeness import CompletenessMetric
from simpleval.evaluation.metrics.models.bedrock_claude_sonnet.correctness import CorrectnessMetric
from simpleval.evaluation.metrics.models.bedrock_claude_sonnet.faithfulness import FaithfulnessMetric
from simpleval.evaluation.metrics.models.bedrock_claude_sonnet.following_instructions import FollowingInstructionsMetric
from simpleval.evaluation.metrics.models.bedrock_claude_sonnet.helpfulness import HelpfulnessMetric
from simpleval.evaluation.metrics.models.bedrock_claude_sonnet.no_ground_truth import NoGroundTruthMetric
from simpleval.evaluation.metrics.models.bedrock_claude_sonnet.no_ground_truth_simple import NoGroundTruthSimpleMetric
from simpleval.evaluation.metrics.models.bedrock_claude_sonnet.pro_style_and_tone import ProStyleToneMetric
from simpleval.evaluation.metrics.models.bedrock_claude_sonnet.readability import ReadabilityMetric
from simpleval.evaluation.metrics.models.bedrock_claude_sonnet.relevance import RelevanceMetric


def test_coherence_metric():
    metric = CoherenceMetric()
    in_prompt = 'XYZ123$$!-PROMPT'
    in_prediction = 'XYZ123$$!-PREDICTION'
    prompt = metric.render_eval_prompt(prompt=in_prompt, prediction=in_prediction)
    expected_possible_answers = ['Not at all', 'Not generally', 'Neutral/Mixed', 'Generally yes', 'Yes']

    assert in_prompt in prompt
    assert in_prediction in prompt
    assert metric.possible_responses == expected_possible_answers
    assert metric.prefill == '<response>'


def test_completeness_metric():
    metric = CompletenessMetric()
    in_prompt = 'XYZ123$$!-PROMPT'
    in_prediction = 'XYZ123$$!-PREDICTION'
    in_ground_truth = 'XYZ123$$!-GROUND_TRUTH'

    prompt = metric.render_eval_prompt(prompt=in_prompt, prediction=in_prediction, ground_truth=in_ground_truth)
    expected_possible_answers = ['Not at all', 'Not generally', 'Neutral/Mixed', 'Generally yes', 'Yes']

    assert in_prompt in prompt
    assert in_prediction in prompt
    assert in_ground_truth in prompt
    assert metric.possible_responses == expected_possible_answers
    assert metric.prefill == '<response>'


def test_correctness_metric():
    metric = CorrectnessMetric()
    in_prompt = 'XYZ123$$!-PROMPT'
    in_prediction = 'XYZ123$$!-PREDICTION'
    in_ground_truth = 'XYZ123$$!-GROUND_TRUTH'
    expected_possible_answers = ['incorrect', 'partially correct', 'correct']

    prompt = metric.render_eval_prompt(prompt=in_prompt, prediction=in_prediction, ground_truth=in_ground_truth)

    assert in_prompt in prompt
    assert in_prediction in prompt
    assert in_ground_truth in prompt
    assert metric.possible_responses == expected_possible_answers
    assert metric.prefill == 'Explanation:'


def test_faithfulness_metric():
    metric = FaithfulnessMetric()
    in_prompt = 'XYZ123$$!-PROMPT'
    in_prediction = 'XYZ123$$!-PREDICTION'
    expected_possible_answers = [
        'none is faithful', 'some is faithful', 'approximately half is faithful', 'most is faithful', 'all is faithful'
    ]

    prompt = metric.render_eval_prompt(prompt=in_prompt, prediction=in_prediction)

    assert in_prompt in prompt
    assert in_prediction in prompt
    assert metric.possible_responses == expected_possible_answers
    assert metric.prefill == 'Explanation:'


def test_following_instructions_metric():
    metric = FollowingInstructionsMetric()
    in_prompt = 'XYZ123$$!-PROMPT'
    in_prediction = 'XYZ123$$!-PREDICTION'
    expected_possible_answers = ['No', 'Not applicable', 'Yes']

    prompt = metric.render_eval_prompt(prompt=in_prompt, prediction=in_prediction)

    assert in_prompt in prompt
    assert in_prediction in prompt
    assert metric.possible_responses == expected_possible_answers
    assert metric.prefill == '{"reasoning": '


def test_helpfulness_metric():
    metric = HelpfulnessMetric()
    in_prompt = 'XYZ123$$!-PROMPT'
    in_prediction = 'XYZ123$$!-PREDICTION'
    expected_possible_answers = [
        'not helpful at all', 'very unhelpful', 'somewhat unhelpful', 'neither helpful nor unhelpful', 'somewhat helpful', 'very helpful',
        'above and beyond'
    ]

    prompt = metric.render_eval_prompt(prompt=in_prompt, prediction=in_prediction)

    assert in_prompt in prompt
    assert in_prediction in prompt
    assert metric.possible_responses == expected_possible_answers
    assert metric.prefill == 'Explanation:'


def test_no_ground_truth_simple_metric():
    metric = NoGroundTruthSimpleMetric()
    in_prompt = 'XYZ123$$!-PROMPT'
    in_prediction = 'XYZ123$$!-PREDICTION'
    expected_possible_answers = ['incorrect', 'partially correct', 'correct']

    prompt = metric.render_eval_prompt(prompt=in_prompt, prediction=in_prediction)

    assert in_prompt in prompt
    assert in_prediction in prompt
    assert metric.possible_responses == expected_possible_answers
    assert metric.prefill == 'Explanation:'


def test_no_ground_truth_metric():
    metric = NoGroundTruthMetric()
    in_prompt = 'XYZ123$$!-PROMPT'
    in_prediction = 'XYZ123$$!-PREDICTION'
    expected_possible_answers = ['Not at all', 'Not generally', 'Neutral/Mixed', 'Generally yes', 'Yes']

    prompt = metric.render_eval_prompt(prompt=in_prompt, prediction=in_prediction)

    assert in_prompt in prompt
    assert in_prediction in prompt
    assert metric.possible_responses == expected_possible_answers
    assert metric.prefill == '{"reasoning": '


def test_pro_style_and_tone_metric():
    metric = ProStyleToneMetric()
    in_prompt = 'XYZ123$$!-PROMPT'
    in_prediction = 'XYZ123$$!-PREDICTION'
    expected_possible_answers = ['not at all', 'not generally', 'neutral/mixed', 'generally yes', 'completely yes']

    prompt = metric.render_eval_prompt(prompt=in_prompt, prediction=in_prediction)

    assert in_prompt in prompt
    assert in_prediction in prompt
    assert metric.possible_responses == expected_possible_answers
    assert metric.prefill == 'Explanation:'


def test_readability_metric():
    metric = ReadabilityMetric()
    in_prompt = 'XYZ123$$!-PROMPT'
    in_prediction = 'XYZ123$$!-PREDICTION'
    expected_possible_answers = ['unreadable', 'poor readability', 'fair readability', 'good readability', 'excellent readability']

    prompt = metric.render_eval_prompt(prompt=in_prompt, prediction=in_prediction)

    assert in_prompt in prompt
    assert in_prediction in prompt
    assert metric.possible_responses == expected_possible_answers
    assert metric.prefill == 'Explanation:'


def test_relevance_metric():
    metric = RelevanceMetric()
    in_prompt = 'XYZ123$$!-PROMPT'
    in_prediction = 'XYZ123$$!-PREDICTION'
    expected_possible_answers = ['not at all', 'slightly', 'somewhat', 'mostly', 'completely']

    prompt = metric.render_eval_prompt(prompt=in_prompt, prediction=in_prediction)

    assert in_prompt in prompt
    assert in_prediction in prompt
    assert metric.possible_responses == expected_possible_answers
    assert metric.prefill == 'Explanation:'
