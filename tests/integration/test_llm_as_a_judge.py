import json
import math
import sys
from pathlib import Path

import pytest

from simpleval.evaluation.judges.base_judge import BaseJudge
from simpleval.evaluation.judges.models.anthropic.judge import AnthropicJudge
from simpleval.evaluation.judges.models.azure.judge import AzureJudge
from simpleval.evaluation.judges.models.bedrock_claude_sonnet.judge import BedrockClaudeSonnetJudge
from simpleval.evaluation.judges.models.gemini.judge import GeminiJudge
from simpleval.evaluation.judges.models.open_ai.judge import OpenAIJudge
from simpleval.evaluation.judges.models.vertex_ai.judge import VertexAIJudge
from simpleval.evaluation.metrics.base_metric import EvaluationMetric
from simpleval.evaluation.metrics.normalizers import get_score_interval
from simpleval.evaluation.schemas.eval_result_schema import EvalTestResult

LLM_AS_A_JUDGE_GOLDEN_SET_ROOT = 'tests/resources/llm_as_a_judge_test_eval_results_golden_set'
LLM_AS_A_JUDGE_DATASETS_ROOT = 'tests/resources/llm_as_a_judge_datasets'
DATASETS = ['classify_product', 'detect_toxicity', 'spam_detection']
TESTCASES = ['good_prompt', 'bad_prompt']
EVAL_RESULTS_FILE_TEMPLATE = 'eval_results_{judge_name}.jsonl'

TEST_RESULT_SUMMARY_FILE = 'llm_as_a_judge_test_results_{judge_name}.json'

STRICT_SCORE_COMPARISON = False

GLOBAL_METRIC_FAIL_THRESHOLD = 0.1
DEFAULT_METRIC_FAIL_THRESHOLD = 0.1
METRIC_TESTCASE_THRESHOLDS = {
    'readability:bad_prompt': 0.4,
    'pro_style_and_tone:bad_prompt': 0.45,
    'no_ground_truth:bad_prompt': 0.4,
    'coherence:bad_prompt': 0.3,
    'following_instructions:bad_prompt': 0.2,
    'correctness:good_prompt': 0.05,
    'relevance:good_prompt': 0.05,
    'correctness:bad_prompt': 0.05,
    'relevance:bad_prompt': 0.05,
}


def get_eval_result_by_metric(eval_results, name_metric):
    for result in eval_results:
        if result.name_metric == name_metric:
            return result
    return None


@pytest.fixture
def setup():
    # Setup code
    yield
    # Cleanup code


def get_metrics_score_intervals(judge: BaseJudge):
    """
    Get the score intervals for the metrics in the judge.
    """
    score_intervals = {}

    metrics: EvaluationMetric = judge.get_all_metrics()
    for metric in metrics.values():
        score_intervals[metric.name] = get_score_interval(len(metric.possible_responses))
    return score_intervals


def do_scores_deviate(score1: float, score2: float, score_interval: float, strict_comparison: bool):
    """
    Check if the scores deviate more than the score interval.
    """
    if strict_comparison:
        return not math.isclose(score1, score2)
    else:
        return abs(score1 - score2) > score_interval + sys.float_info.epsilon


@pytest.mark.parametrize('judge_type', [
    BedrockClaudeSonnetJudge,
    GeminiJudge,
    OpenAIJudge,
    AzureJudge,
    AnthropicJudge,
    VertexAIJudge,
])
def test_llm_as_a_judge_results(setup, judge_type: BaseJudge):
    # In LLM_AS_A_JUDGE_DATASETS_ROOT, for each dataset in DATASETS, under each testcase:
    # Delete eval_results.jsonl file
    # Run the test case
    # Copy the eval_results.jsonl file to eval_results_<judge_name>.jsonl

    judge = judge_type()
    score_intervals = get_metrics_score_intervals(judge)
    results_file = EVAL_RESULTS_FILE_TEMPLATE.format(judge_name=judge.name)

    differing_results = {}
    tests_count_by_metric_testcase = {}

    for dataset in DATASETS:
        differing_results[dataset] = {}
        for testcase in TESTCASES:
            differing_results[dataset][testcase] = []

            golden_set_eval_results_file = Path(LLM_AS_A_JUDGE_GOLDEN_SET_ROOT, dataset, testcase, results_file)
            eval_results_path = Path(LLM_AS_A_JUDGE_DATASETS_ROOT, dataset, 'eval_set', 'testcases', testcase, results_file)

            with open(golden_set_eval_results_file, 'r') as f:
                golden_set_eval_results = [EvalTestResult(**json.loads(line)) for line in f.readlines()]

            with open(eval_results_path, 'r') as f:
                eval_results = [EvalTestResult(**json.loads(line)) for line in f.readlines()]

            for golden_set_result in golden_set_eval_results:
                metric_testcase = f'{golden_set_result.metric}:{testcase}'
                tests_count_by_metric_testcase[metric_testcase] = tests_count_by_metric_testcase.get(metric_testcase, 0) + 1

                eval_result = get_eval_result_by_metric(eval_results, golden_set_result.name_metric)
                assert eval_result, f'Eval result not found for {golden_set_result.name_metric} in {eval_results_path}'

                score_interval = score_intervals[golden_set_result.metric]

                scores_deviate = do_scores_deviate(
                    score1=golden_set_result.normalized_score,
                    score2=eval_result.normalized_score,
                    score_interval=score_interval,
                    strict_comparison=STRICT_SCORE_COMPARISON,
                )

                if eval_result and scores_deviate:
                    differing_results[dataset][testcase].append({
                        'name_metric': golden_set_result.name_metric,
                        'golden_set_score': golden_set_result.normalized_score,
                        'golden_set_explanation': golden_set_result.explanation,
                        'eval_result_score': eval_result.normalized_score,
                        'eval_result_explanation': eval_result.explanation,
                        'golden_set_file': str(golden_set_eval_results_file),
                        'eval_result_file': str(eval_results_path)
                    })

    # Calculate stats for differing results
    stats = {
        f'{dataset}-{testcase}': len(differing_results[dataset][testcase])                                          \
            for dataset in differing_results
            for testcase in differing_results[dataset]
    }

    # Add count by metric name
    metric_stats = {}
    for dataset in differing_results:
        for testcase in differing_results[dataset]:
            for result in differing_results[dataset][testcase]:
                metric_name = f'{result["name_metric"].split(":")[-1]}:{testcase}'
                metric_stats[metric_name] = metric_stats.get(metric_name, 0) + 1

    # Sort metric_counts by value before adding to stats
    sorted_metric_counts = dict(sorted(metric_stats.items(), key=lambda item: item[1], reverse=True))
    stats['metric_counts'] = {
        metric_name: {
            'diff_count': value,
            'total_tests': tests_count_by_metric_testcase[metric_name],
            'percent': f'{value / tests_count_by_metric_testcase[metric_name] * 100:.2f}'
        } for metric_name, value in sorted_metric_counts.items()
    }

    total_diffs = sum(len(differing_results[dataset][testcase]) for dataset in differing_results for testcase in differing_results[dataset])
    total_tests = sum(tests_count_by_metric_testcase.values())

    total_diff_percent = total_diffs / total_tests
    stats['overall_diff_count'] = {'diff_count': total_diffs, 'total_tests': total_tests, 'percent': f'{total_diff_percent * 100:.2f}'}

    # Prepare final JSON structure
    final_summary = {'stats': stats, 'results': differing_results}

    # Write final summary to file
    summary_file_name = TEST_RESULT_SUMMARY_FILE.format(judge_name=judge.name)
    with open(Path(Path(__file__).parent, summary_file_name), 'w') as f:
        json.dump(final_summary, f, indent=2)

    assert total_diff_percent < GLOBAL_METRIC_FAIL_THRESHOLD, f'Overall difference percentage failed, See {summary_file_name} for details.'

    for metric_name, metric_info in stats['metric_counts'].items():
        diff_count = metric_info['diff_count']
        total_tests = metric_info['total_tests']
        diff_percent = diff_count / total_tests

        assert diff_percent < METRIC_TESTCASE_THRESHOLDS.get(metric_name, DEFAULT_METRIC_FAIL_THRESHOLD), \
            f'Metric {metric_name} difference percentage failed, See {summary_file_name} for details.'
