import os
import shutil
from unittest.mock import patch

import pytest

from simpleval.commands.init_command.base_init import BaseInit
from simpleval.commands.init_command.consts import RECOMMENDED_START_METRICS, RECOMMENDED_START_METRICS_MENU_VALUE
from simpleval.commands.init_command.init_command import init_command
from simpleval.commands.init_command.init_from_template_command import init_from_template_command
from simpleval.commands.init_command.user_functions import RECOMMENDED_INDICATION
from simpleval.consts import EVAL_CONFIG_FILE
from simpleval.evaluation.utils import get_eval_config
from simpleval.exceptions import TerminationError


@pytest.fixture(scope='function')
def temp_eval_folder():
    folder_name = os.path.join(os.path.dirname(__file__), 'temp', 'test_init_command')
    if os.path.exists(folder_name):
        shutil.rmtree(folder_name)
    os.makedirs(folder_name)

    yield folder_name
    if os.path.exists(folder_name):
        shutil.rmtree(folder_name)


def assert_eval_dir_structure(eval_dir, testcase_dir):
    assert os.path.exists(eval_dir)
    assert os.path.exists(os.path.join(eval_dir, 'testcases'))
    assert os.path.exists(os.path.join(eval_dir, 'testcases', testcase_dir))
    assert os.path.exists(os.path.join(eval_dir, 'config.json'))
    assert os.path.exists(os.path.join(eval_dir, 'ground_truth.jsonl'))
    assert os.path.exists(os.path.join(eval_dir, 'README.md'))
    assert os.path.exists(os.path.join(eval_dir, 'testcases', testcase_dir, '__init__.py'))
    assert os.path.exists(os.path.join(eval_dir, 'testcases', testcase_dir, 'task_handler.py'))


def assert_eval_config_values(eval_dir, expected):
    config = get_eval_config(eval_dir, EVAL_CONFIG_FILE, verify_metrics=False)
    assert config.name == expected['name']
    assert config.max_concurrent_judge_tasks == expected['max_concurrent_judge_tasks']
    assert config.max_concurrent_llm_tasks == expected['max_concurrent_llm_tasks']
    assert config.eval_metrics == expected['eval_metrics']
    assert config.llm_as_a_judge_name == expected['llm_as_a_judge_name']
    assert config.llm_as_a_judge_model_id == expected.get('llm_as_a_judge_model_id')


def test_init_command_from_templates_creates_folders_and_files(temp_eval_folder):
    eval_dir = os.path.join(temp_eval_folder, 'test-eval')
    testcase = 'nova-lite'

    init_from_template_command(eval_dir=eval_dir, testcase=testcase)

    testcase_dir = BaseInit.normalize_testcase_dir_name(testcase)
    assert_eval_dir_structure(eval_dir, testcase_dir)
    # Assert config values
    expected_config = {
        'name': 'test-eval',
        'max_concurrent_judge_tasks': 10,
        'max_concurrent_llm_tasks': 10,
        'eval_metrics': [],
        'llm_as_a_judge_name': 'open_ai',
        'llm_as_a_judge_model_id': None
    }
    assert_eval_config_values(eval_dir, expected_config)


def test_init_command_from_template_raises_error_if_folder_exists(temp_eval_folder):
    eval_dir = os.path.join(temp_eval_folder, 'test-eval')
    testcase = 'nova-lite'

    # Create the folder to simulate it already exists
    os.makedirs(eval_dir)

    with pytest.raises(TerminationError, match=f'Folder already exists: {eval_dir}'):
        init_from_template_command(eval_dir=eval_dir, testcase=testcase)


@patch('builtins.input')
@patch('simpleval.commands.init_command.user_functions.prompt')
def test_init_command_creates_folders_and_files(mock_prompt, mock_input, temp_eval_folder):
    eval_dir = os.path.join(temp_eval_folder, 'test-eval')
    testcase = 'nova-lite'
    continue_with_preliminary_errors_input = 'y'
    configure_concurrency_input = 'y'
    llm_judge_concurrency_input = '5'
    llm_task_concurrency_input = '6'

    # Mock the input function to return eval_dir first and then testcase
    mock_input.side_effect = [
        eval_dir,  # first user input is eval dir
        testcase,  # second user input is testcase
        continue_with_preliminary_errors_input,  # third user input is continue with preliminary errors
        configure_concurrency_input,  # fourth user input is configure concurrency y/n
        llm_judge_concurrency_input,  # fifth user input is llm judge concurrency int value
        llm_task_concurrency_input,  # sixth user input is llm task concurrency int value
    ]
    mock_prompt.side_effect = [
        {
            'selected_judge': 'azure'
        },
        {
            'selected_model': f'gpt-4 {RECOMMENDED_INDICATION}'
        },
        {
            'selected_metrics': RECOMMENDED_START_METRICS_MENU_VALUE
        },
    ]

    # Run the command
    init_command()

    # Assert that the files and directories were created
    testcase_dir = BaseInit.normalize_testcase_dir_name(testcase)
    assert_eval_dir_structure(eval_dir, testcase_dir)
    # Assert config values
    expected_config = {
        'name': 'test-eval',
        'max_concurrent_judge_tasks': 5,
        'max_concurrent_llm_tasks': 6,
        'eval_metrics': RECOMMENDED_START_METRICS,
        'llm_as_a_judge_name': 'azure',
        'llm_as_a_judge_model_id': 'gpt-4'
    }
    assert_eval_config_values(eval_dir, expected_config)


@patch('builtins.input')
@patch('simpleval.commands.init_command.user_functions.prompt')
def test_init_command_stop_due_to_preliminary_errors(mock_prompt, mock_input, temp_eval_folder):
    eval_dir = os.path.join(temp_eval_folder, 'test-eval')
    testcase = 'nova-lite'
    continue_with_preliminary_errors_input = 'n'

    # Mock the input function to return eval_dir first and then testcase
    mock_input.side_effect = [
        eval_dir,  # first user input is eval dir
        testcase,  # second user input is testcase
        continue_with_preliminary_errors_input,  # third user input is continue with preliminary errors
    ]
    mock_prompt.side_effect = [
        {
            'selected_judge': 'azure'
        },
        {
            'selected_model': f'gpt-4 {RECOMMENDED_INDICATION}'
        },
    ]

    with pytest.raises(TerminationError, match='Exiting...'):
        init_command()


@patch('builtins.input')
@patch('simpleval.commands.init_command.user_functions.prompt')
def test_init_command_creates_folders_and_files_with_invalid_int_values(mock_prompt, mock_input, temp_eval_folder):
    eval_dir = os.path.join(temp_eval_folder, 'test-eval')
    testcase = 'nova-lite'
    continue_with_preliminary_errors_input = 'y'
    configure_concurrency_input = 'y'
    first_llm_judge_concurrency_input = 'a'
    second_llm_judge_concurrency_input = '5'
    first_llm_task_concurrency_input = 'b'
    second_llm_task_concurrency_input = '6'

    # Mock the input function to return eval_dir first and then testcase
    mock_input.side_effect = [
        eval_dir,  # first user input is eval dir
        testcase,  # second user input is testcase
        continue_with_preliminary_errors_input,  # third user input is continue with preliminary errors
        configure_concurrency_input,  # fourth user input is configure concurrency y/n
        first_llm_judge_concurrency_input,
        second_llm_judge_concurrency_input,
        first_llm_task_concurrency_input,
        second_llm_task_concurrency_input,
    ]
    mock_prompt.side_effect = [
        {
            'selected_judge': 'azure'
        },
        {
            'selected_model': f'gpt-4 {RECOMMENDED_INDICATION}'
        },
        {
            'selected_metrics': RECOMMENDED_START_METRICS_MENU_VALUE
        },
    ]

    # Run the command
    init_command()

    # Assert that the files and directories were created
    testcase_dir = BaseInit.normalize_testcase_dir_name(testcase)
    assert_eval_dir_structure(eval_dir, testcase_dir)
    # Assert config values
    expected_config = {
        'name': 'test-eval',
        'max_concurrent_judge_tasks': 5,
        'max_concurrent_llm_tasks': 6,
        'eval_metrics': RECOMMENDED_START_METRICS,
        'llm_as_a_judge_name': 'azure',
        'llm_as_a_judge_model_id': 'gpt-4'
    }
    assert_eval_config_values(eval_dir, expected_config)


def test_normalize_testcase_dir_name():
    # Test replacing hyphens with underscores
    assert BaseInit.normalize_testcase_dir_name('test-case') == 'test_case'
    # Test removing special characters
    assert BaseInit.normalize_testcase_dir_name('test@case!') == 'testcase'
    # Test keeping alphanumeric and underscores
    assert BaseInit.normalize_testcase_dir_name('test_case123') == 'test_case123'
    # Test multiple hyphens and special chars
    assert BaseInit.normalize_testcase_dir_name('a-b-c@d#e') == 'a_b_cde'
    # Test only special characters
    assert BaseInit.normalize_testcase_dir_name('!@#$%^&*()') == ''
    # Test empty string
    assert BaseInit.normalize_testcase_dir_name('') == ''
    # Test string with spaces (should be removed)
    assert BaseInit.normalize_testcase_dir_name('test case') == 'testcase'
    # Test string with numbers and underscores
    assert BaseInit.normalize_testcase_dir_name('123_test-456') == '123_test_456'
