from unittest.mock import MagicMock, patch

import pytest

from simpleval.commands.litellm_models_explorer_command import get_model_info, litellm_models_explorer_command, \
    supported_models_by_provider


@patch('simpleval.commands.litellm_models_explorer_command.litellm.get_model_info')
def test_get_model_info_success(mock_get_model_info):
    mock_get_model_info.return_value = {'mode': 'chat'}
    result = get_model_info('test_model', 'provider')
    assert result == {'mode': 'chat'}


@patch('simpleval.commands.litellm_models_explorer_command.litellm.get_model_info')
@patch('simpleval.commands.litellm_models_explorer_command.logging.getLogger')
def test_get_model_info_failure(mock_logger, mock_get_model_info):
    mock_logger.return_value = MagicMock()
    mock_get_model_info.side_effect = Exception('Error')
    result = get_model_info('test_model', 'provider')
    assert result == {}


@patch('simpleval.commands.litellm_models_explorer_command.prompt')
@patch('simpleval.commands.litellm_models_explorer_command.supported_models_by_provider')
@patch('simpleval.commands.litellm_models_explorer_command.logging.getLogger')
def test_litellm_models_explorer_command(mock_logger, mock_supported_models_by_provider, mock_prompt):
    mock_logger.return_value = MagicMock()
    mock_supported_models_by_provider.return_value = {'provider1': [{'model': 'model1'}, {'model': 'model2'}]}
    mock_prompt.return_value = {'selected_provider': 'provider1'}

    litellm_models_explorer_command()

    mock_logger.return_value.info.assert_any_call("Models available for provider 'provider1':")
    mock_logger.return_value.info.assert_any_call('model1')
    mock_logger.return_value.info.assert_any_call('model2')


@patch('simpleval.commands.litellm_models_explorer_command.prompt')
def test_litellm_models_explorer_command_no_exception(mock_prompt):
    mock_prompt.return_value = {'selected_provider': 'openai'}

    try:
        litellm_models_explorer_command()
    except Exception as e:
        pytest.fail(f'litellm_models_explorer_command raised an exception: {e}')
