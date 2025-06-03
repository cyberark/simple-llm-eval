import pytest

from simpleval.eval_sets.detect_user_action.testcases.nova_lite1.task_handler import task_logic as detect_user_action_task_logic
from simpleval.eval_sets.dummy_task.testcases.static_results.task_handler import task_logic as dummy_task_logic
from simpleval.eval_sets.empty.testcases.empty.task_handler import task_logic as empty_task_logic
from simpleval.testcases.schemas.llm_task_result import LlmTaskResult


def test_empty_task_logic():
    payload = {'key': 'value'}
    result = empty_task_logic('test_empty', payload)
    assert isinstance(result, LlmTaskResult)
    assert result.name == 'test_empty'
    assert result.prompt == 'Hi LLM, please respond to this prompt, replace with your own prompt'
    assert result.prediction == 'Is is the response from the LLM'
    assert result.payload == payload


def test_dummy_task_logic():
    payload = {'user_input': 'Hello'}
    result = dummy_task_logic('test_dummy', payload)
    assert isinstance(result, LlmTaskResult)
    assert result.name == 'test_dummy'
    assert result.prompt == 'What does the user say?'
    assert result.prediction == 'User says: Hello'
    assert result.payload == payload


def test_detect_user_action_task_logic():
    payload = {'frames': ['frame1', 'frame2'], 'mouse_input': ['click1', 'click2']}
    result = detect_user_action_task_logic('test_detect_user_action', payload)
    assert isinstance(result, LlmTaskResult)
    assert result.name == 'test_detect_user_action'
    assert result.prompt == "What did the user do in the os? frames: ['frame1', 'frame2'], mouse input: ['click1', 'click2']"
    assert result.prediction == 'The user clicked some buttons'
    assert result.payload == payload
