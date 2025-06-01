from unittest.mock import MagicMock, patch

import pytest

from simpleval.commands.judge_explorer_command import judge_explorer_command


@patch('builtins.print')
@patch('simpleval.commands.judge_explorer_command.logging.getLogger')
@patch('simpleval.commands.judge_explorer_command.prompt')
@patch('simpleval.commands.judge_explorer_command.JudgeProvider')
def test_judge_explorer_command_with_judges(mock_judge_provider, mock_prompt, mock_get_logger, mock_print):
    # Setup mocks
    mock_logger = MagicMock()
    mock_get_logger.return_value = mock_logger
    mock_judge = MagicMock()
    mock_judge.name = 'TestJudge'
    mock_judge.model_id = 'test-model'
    mock_judge.list_metrics.return_value = ['accuracy', 'f1']
    mock_judge.preliminary_checks_explanation.return_value = 'No auth required.'
    mock_judge.supported_model_ids = ['test-model', 'other-model']

    mock_judge_provider.list_judges.return_value = ['TestJudge']
    mock_judge_provider.get_judge.return_value = mock_judge
    mock_prompt.return_value = {'selected_judge': 'TestJudge'}

    judge_explorer_command()

    # Check logger calls for expected output
    assert mock_logger.info.call_count > 0
    assert any('TestJudge' in str(call) for call in mock_logger.info.call_args_list)
    assert any('test-model' in str(call) for call in mock_logger.info.call_args_list)
    assert any('No auth required.' in str(call) for call in mock_logger.info.call_args_list)

    assert any('- accuracy' in str(call) for call in mock_print.call_args_list)


@patch('simpleval.commands.judge_explorer_command.logging.getLogger')
@patch('simpleval.commands.judge_explorer_command.JudgeProvider')
def test_judge_explorer_command_no_judges(mock_judge_provider, mock_get_logger):
    mock_logger = MagicMock()
    mock_get_logger.return_value = mock_logger
    mock_judge_provider.list_judges.return_value = []

    judge_explorer_command()

    # Should log a warning about no judges
    assert mock_logger.warning.call_count > 0
    assert any('No judges found' in str(call) for call in mock_logger.warning.call_args_list)
