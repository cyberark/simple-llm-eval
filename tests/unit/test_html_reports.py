import os
from typing import Counter
from unittest.mock import MagicMock, patch

from bs4 import BeautifulSoup

from simpleval.commands.reporting.compare.common import CompareArgs
from simpleval.commands.reporting.compare.compare_html import _compare_results_html
from simpleval.commands.reporting.eval.eval_report import ResultsManager
from simpleval.evaluation.metrics.calc import MeanScores, Scores
from simpleval.evaluation.schemas.eval_result_schema import EvalTestResult
from simpleval.testcases.schemas.llm_task_result import LlmTaskResult


@patch('webbrowser.open', MagicMock())
def test_eval_html_report():
    # Setup test data
    eval_results = []
    for i in range(1, 11):
        llm_task_result = LlmTaskResult(name=f'test_name_{i}', prompt=f'Test prompt {i}', prediction=f'Test prediction {i}',
                                        expected_prediction=f'Expected prediction {i}')

        eval_result = EvalTestResult(metric=f'test_metric_{i}', result=f'Result {i}', explanation=f'Test explanation {i}',
                                     normalized_score=float(f'0.{i}'), llm_run_result=llm_task_result)
        eval_results.append(eval_result)

    # Create ResultsManager instance
    results_manager = ResultsManager()

    # Call display_results for HTML
    llm_tasks_errors_count = 56
    eval_errors_count = 24
    result_file = results_manager.display_results(name='test_eval', testcase='test_case', eval_results=eval_results,
                                                  llm_tasks_errors_count=llm_tasks_errors_count, eval_errors_count=eval_errors_count,
                                                  output_format='html')

    # Read and parse the HTML file
    with open(result_file, 'r', encoding='utf-8') as file:
        html_content = file.read()
    soup = BeautifulSoup(html_content, 'html.parser')

    # Perform assertions
    assert soup.title.string == 'test_eval'
    assert soup.h1.string == 'Evaluation Report: test_eval'
    assert soup.h2.string == 'Testcase: test_case'
    rows = soup.find_all('tr')
    assert len(rows) == 11  # 1 header row + 10 data rows

    for i in range(1, 11):
        cells = rows[i].find_all('td')

        # index
        assert cells[0].string == str(i)

        # test name (name-metric)
        assert cells[1].string == f'{eval_results[i - 1].llm_run_result.name}:{eval_results[i - 1].metric}'

        # prompt to llm
        prompt_popup_id = f'prompt-popup-{i}'
        popup_div = soup.find('div', id=prompt_popup_id)
        assert popup_div is not None
        popup_content = popup_div.find('div', class_='popup-content')
        prompt_text = popup_content.find('p').text
        assert f'Prompt To LLM:{eval_results[i - 1].llm_run_result.prompt}' in prompt_text

        # llm response
        assert cells[3].string == eval_results[i - 1].llm_run_result.prediction

        # expected llm response
        assert cells[4].string == eval_results[i - 1].llm_run_result.expected_prediction

        # eval result
        assert cells[5].string == eval_results[i - 1].result

        # normalized score
        score_popup_id = f'popup-{i}'
        tooltip_div = cells[6].find('div', class_='tooltip')
        assert tooltip_div.contents[0].strip() == str(eval_results[i - 1].normalized_score)

        # explanation
        popup_div = soup.find('div', id=score_popup_id)
        assert popup_div is not None
        popup_content = popup_div.find('div', class_='popup-content')
        explanation_text = popup_content.find('p').text
        assert eval_results[i - 1].explanation in explanation_text

    # Check for ids duplicates
    all_ids = [tag['id'] for tag in soup.find_all(attrs={'id': True})]
    assert all_ids
    id_counts = Counter(all_ids)
    duplicates = [id for id, count in id_counts.items() if count > 1]
    assert not duplicates

    # Clean up
    os.remove(result_file)


@patch('webbrowser.open', MagicMock())
def test_compare_html_report():
    # Setup test data
    left_side = CompareArgs(
        name='left_side_name',
        mean_scores=MeanScores(aggregate_mean=0.31, aggregate_std_dev=0.1, metrics={
            'Accuracy': Scores(mean=0.81, std_dev=0.21),
            'Precision': Scores(mean=0.71, std_dev=0.11),
        }), sorted_results=[
            EvalTestResult(
                metric='Accuracy', result='Oy!', explanation='Explanation 1', normalized_score=0.8,
                llm_run_result=LlmTaskResult(name='Test 1', prompt='Prompt 1', prediction='Prediction 1',
                                             expected_prediction='Expected 1')),
            EvalTestResult(
                metric='Precision', result='Vey!', explanation='Explanation 2', normalized_score=0.75,
                llm_run_result=LlmTaskResult(name='Test 2', prompt='Prompt 2', prediction='Prediction 2', expected_prediction='Expected 2'))
        ])
    right_side = CompareArgs(
        name='right_side_name',
        mean_scores=MeanScores(aggregate_mean=0.32, aggregate_std_dev=0.2, metrics={
            'Accuracy': Scores(mean=0.82, std_dev=0.22),
            'Precision': Scores(mean=0.72, std_dev=0.12),
        }), sorted_results=[
            EvalTestResult(
                metric='Accuracy', result='0.85', explanation='Explanation 1', normalized_score=0.85,
                llm_run_result=LlmTaskResult(name='Test 1', prompt='Prompt 1', prediction='Prediction 1',
                                             expected_prediction='Expected 1')),
            EvalTestResult(
                metric='Precision', result='0.78', explanation='Explanation 2', normalized_score=0.78,
                llm_run_result=LlmTaskResult(name='Test 2', prompt='Prompt 2', prediction='Prediction 2', expected_prediction='Expected 2'))
        ])

    # Call _compare_results_html
    result_file = _compare_results_html(left_side, right_side)

    # Read and parse the HTML file
    with open(result_file, 'r', encoding='utf-8') as file:
        html_content = file.read()
    soup = BeautifulSoup(html_content, 'html.parser')

    # Perform assertions
    assert soup.title.string == 'Comparison Report'
    assert soup.h1.string == 'Comparison Report'
    assert soup.h2.string == 'Summary'

    summary_rows = soup.find_all('table')[0].find_all('tr')
    assert len(summary_rows) == 4  # 1 header row + 3 data rows

    # Test values in the summary table

    assert summary_rows[1].find_all('td')[0].string == 'Accuracy'
    assert summary_rows[1].find_all('td')[1].string == '0.81'
    assert summary_rows[1].find_all('td')[2].string == '0.82'
    assert summary_rows[2].find_all('td')[0].string == 'Precision'
    assert summary_rows[2].find_all('td')[1].string == '0.71'
    assert summary_rows[2].find_all('td')[2].string == '0.72'
    assert summary_rows[3].find_all('td')[0].string == 'Aggregate mean'
    assert summary_rows[3].find_all('td')[1].string == '0.31'
    assert summary_rows[3].find_all('td')[2].string == '0.32'

    details_rows = soup.find_all('table')[1].find_all('tr')
    assert len(details_rows) == len(left_side.sorted_results) * 3 + 1  # 1 header row + 3 rows for each metric

    # Test values in the details table
    for i in range(len(left_side.sorted_results)):
        metric = left_side.sorted_results[i].metric
        llm_task_name_left = left_side.sorted_results[i].llm_run_result.name
        llm_task_name_right = right_side.sorted_results[i].llm_run_result.name

        # Metric row
        assert details_rows[i * 3 + 1].find_all('td')[0].string == metric

        # Verify content of "Eval set:testcase:test" column for left side
        eval_set_content_left = details_rows[i * 3 + 2].find_all('td')[1].string
        assert eval_set_content_left == f'{left_side.name}:{llm_task_name_left}'

        # Verify content of "Eval set:testcase:test" column for right side
        eval_set_content_right = details_rows[i * 3 + 3].find_all('td')[1].string
        assert eval_set_content_right == f'{right_side.name}:{llm_task_name_right}'

        # Verify scores for left and right sides
        score_content_left = details_rows[i * 3 + 2].find_all('td')[5].string
        assert float(score_content_left) == left_side.sorted_results[i].normalized_score

        score_content_right = details_rows[i * 3 + 3].find_all('td')[5].string
        assert float(score_content_right) == right_side.sorted_results[i].normalized_score

    # Check for ids duplicates
    all_ids = [tag['id'] for tag in soup.find_all(attrs={'id': True})]
    assert all_ids
    id_counts = Counter(all_ids)
    duplicates = [id for id, count in id_counts.items() if count > 1]
    assert not duplicates

    # Clean up
    os.remove(result_file)
