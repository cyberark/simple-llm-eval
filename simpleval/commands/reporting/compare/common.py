from typing import List

from pydantic import BaseModel

from simpleval.evaluation.metrics.calc import MeanScores
from simpleval.evaluation.schemas.eval_result_schema import EvalTestResult


class CompareArgs(BaseModel):
    name: str
    mean_scores: MeanScores
    sorted_results: List[EvalTestResult]


def _generate_summary_table(left_side: CompareArgs, right_side: CompareArgs):
    headers = ['metric', f'score ({left_side.name})', f'score ({right_side.name})']
    table = []

    for metric, score in left_side.mean_scores.metrics.items():
        table.append([metric, score.mean, right_side.mean_scores.metrics[metric].mean])

    table.append(['Aggregate mean', left_side.mean_scores.aggregate_mean, right_side.mean_scores.aggregate_mean])

    return headers, table


def _generate_details_table(left_side: CompareArgs, right_side: CompareArgs):
    table = []
    headers = ['llm-task:metric', 'eval-set:testcase:test', 'score', 'expected result', 'actual llm result']
    for left_result, right_result in zip(left_side.sorted_results, right_side.sorted_results):
        _validate_metrics(left_result, right_result)

        table.append([left_result.metric, '', '', '', ''])

        left_test_detailed_name = f'{left_side.name}:{left_result.llm_run_result.name}'
        right_test_detailed_name = f'{right_side.name}:{right_result.llm_run_result.name}'

        left_score = left_result.normalized_score
        right_score = right_result.normalized_score

        left_expected_result = left_result.llm_run_result.expected_prediction
        right_expected_result = right_result.llm_run_result.expected_prediction

        left_actual_result = left_result.llm_run_result.prediction
        right_actual_result = right_result.llm_run_result.prediction

        table.append(['', left_test_detailed_name, left_score, left_expected_result, left_actual_result])
        table.append(['', right_test_detailed_name, right_score, right_expected_result, right_actual_result])

    return headers, table


def _get_llm_details_for_detailed_table2(result):
    return {
        'prompt': result.llm_run_result.prompt,
        'prediction': result.llm_run_result.prediction,
        'expected_prediction': result.llm_run_result.expected_prediction,
    }


def _get_eval_result_for_detailed_table2(result):
    return {'eval_result': result.result, 'result_explanation': result.explanation}


def _generate_details_table2(left_side, right_side):
    table = []
    headers = ['Metric', 'Eval set:testcase:test', 'Prompt To LLM', 'LLM Response', 'Expected Response', 'Score', 'Eval Result']
    for left_result, right_result in zip(left_side.sorted_results, right_side.sorted_results):
        _validate_metrics(left_result, right_result)

        table.append([left_result.metric, '', '', '', '', '', ''])

        left_test_detailed_name = f'{left_side.name}:{left_result.llm_run_result.name}'
        right_test_detailed_name = f'{right_side.name}:{right_result.llm_run_result.name}'

        left_score = left_result.normalized_score
        right_score = right_result.normalized_score

        left_llm_details = _get_llm_details_for_detailed_table2(left_result)
        left_eval_result = _get_eval_result_for_detailed_table2(left_result)

        right_llm_details = _get_llm_details_for_detailed_table2(right_result)
        right_eval_result = _get_eval_result_for_detailed_table2(right_result)

        table.append(
            [
                '',
                left_test_detailed_name,
                left_llm_details['prompt'],
                left_llm_details['prediction'],
                left_llm_details['expected_prediction'],
                left_score,
                left_eval_result,
            ]
        )
        table.append(
            [
                '',
                right_test_detailed_name,
                right_llm_details['prompt'],
                right_llm_details['prediction'],
                right_llm_details['expected_prediction'],
                right_score,
                right_eval_result,
            ]
        )

    return headers, table


def _validate_metrics(left_result: EvalTestResult, right_result: EvalTestResult):
    if left_result.metric != right_result.metric:
        raise ValueError(f'Eval result name-metric are different. {left_result.metric=} vs {right_result.metric=}')

    if not left_result.name_metric.endswith(left_result.metric) or not right_result.name_metric.endswith(right_result.metric):
        raise ValueError(
            f'Inconsistent metrics during comparison. Metric: {left_result.metric}, {left_result.name_metric=}, {right_result.name_metric=}'
        )

    if left_result.name_metric != right_result.name_metric:
        raise ValueError(f'Eval result name-metric are different. {left_result.name_metric=} vs {right_result.name_metric=}')


def is_float(value):
    try:
        float(value)
        return True
    except ValueError:
        return False
