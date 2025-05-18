from unittest.mock import MagicMock, patch

import pytest

from simpleval.commands.metrics_explorer_command import list_metrics, metrics_explorer_command, select_item


def test_select_item():
    items = ['item1', 'item2', 'item3']
    prompt_message = 'Select an item:'
    with patch('simpleval.commands.metrics_explorer_command.prompt') as mock_prompt:
        mock_prompt.return_value = {'selected_item': 'item2'}
        selected_item = select_item(items, prompt_message)
        assert selected_item == 'item2'


def test_metrics_explorer_command():
    with patch('simpleval.commands.metrics_explorer_command.select_item') as mock_select_item, \
         patch('builtins.input', return_value='n'):

        mock_select_item.side_effect = ['dummy_judge', 'completeness']

        metrics_explorer_command()


def test_list_metrics():
    with patch('simpleval.commands.metrics_explorer_command.JudgeProvider') as mock_judge_provider, \
         patch('simpleval.commands.metrics_explorer_command.select_item') as mock_select_item, \
         patch('builtins.input', side_effect=['y', 'n']):

        mock_judge = MagicMock()
        mock_judge.list_metrics.return_value = ['metric1', 'metric2']
        mock_judge.get_metric.return_value.__doc__ = 'Metric description'
        mock_judge.get_metric.return_value.possible_responses = ['response1', 'response2']

        mock_judge_provider.get_judge.return_value = mock_judge

        mock_select_item.return_value = 'metric1'

        list_metrics('judge1')

        assert mock_judge_provider.get_judge.call_count == 2
        mock_judge_provider.get_judge.assert_any_call('judge1')

        assert mock_judge.list_metrics.call_count == 2
        mock_select_item.call_count == 2

        mock_select_item.assert_any_call(['metric1', 'metric2'], 'Select a metric to explore: ', 'Enter a number between 1 and 2')
