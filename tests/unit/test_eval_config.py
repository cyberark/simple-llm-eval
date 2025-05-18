import pytest

from simpleval.evaluation.schemas.eval_task_config_schema import EvalTaskConfig, EvalTaskOverrides


@pytest.mark.parametrize('testcase', [None, 'nonexistent'])
def test_effective_max_concurrent_judge_tasks_no_override(testcase):
    config = EvalTaskConfig(
        name='test',
        max_concurrent_judge_tasks=5,
        max_concurrent_llm_tasks=6,
        eval_metrics=['accuracy'],
        llm_as_a_judge_name='model_a',
    )

    assert config.max_concurrent_judge_tasks == 5
    assert config.max_concurrent_llm_tasks == 6

    assert config.effective_max_concurrent_judge_tasks(testcase) == 5
    assert config.effective_max_concurrent_llm_tasks(testcase) == 6
    assert config.llm_as_a_judge_model_id is None


def test_effective_all_values_override():
    testcase_name = 'testcase1'

    config = EvalTaskConfig(
        name='test',
        max_concurrent_judge_tasks=2,
        max_concurrent_llm_tasks=3,
        eval_metrics=['accuracy'],
        llm_as_a_judge_name='model_a',
        override={testcase_name: EvalTaskOverrides(
            max_concurrent_judge_tasks=22,
            max_concurrent_llm_tasks=33,
        )},
    )
    assert config.effective_max_concurrent_judge_tasks(testcase_name) == 22
    assert config.effective_max_concurrent_llm_tasks(testcase_name) == 33
    assert config.llm_as_a_judge_model_id is None


def test_effective_values_non_existing_testcase():
    testcase_name = 'testcase1'

    config = EvalTaskConfig(
        name='test',
        max_concurrent_judge_tasks=2,
        max_concurrent_llm_tasks=3,
        eval_metrics=['accuracy'],
        llm_as_a_judge_name='model_a',
        override={testcase_name: EvalTaskOverrides(
            max_concurrent_judge_tasks=22,
            max_concurrent_llm_tasks=33,
        )},
    )

    bad_testcase_name = 'nonexistent'
    assert config.effective_max_concurrent_judge_tasks(bad_testcase_name) == 2
    assert config.effective_max_concurrent_llm_tasks(bad_testcase_name) == 3
    assert config.llm_as_a_judge_model_id is None


def test_effective_only_max_concurrent_judge_tasks_override():
    testcase_name = 'testcase1'

    config = EvalTaskConfig(
        name='test',
        max_concurrent_judge_tasks=2,
        max_concurrent_llm_tasks=3,
        eval_metrics=['accuracy'],
        llm_as_a_judge_name='model_a',
        override={testcase_name: EvalTaskOverrides(max_concurrent_judge_tasks=22)},
    )
    assert config.effective_max_concurrent_judge_tasks(testcase_name) == 22
    assert config.effective_max_concurrent_llm_tasks(testcase_name) == 3
    assert config.llm_as_a_judge_model_id is None


def test_effective_only_max_concurrent_llm_tasks_override():
    testcase_name = 'testcase1'

    config = EvalTaskConfig(
        name='test',
        max_concurrent_judge_tasks=2,
        max_concurrent_llm_tasks=3,
        eval_metrics=['accuracy'],
        llm_as_a_judge_name='model_a',
        override={testcase_name: EvalTaskOverrides(max_concurrent_llm_tasks=33)},
    )
    assert config.effective_max_concurrent_judge_tasks(testcase_name) == 2
    assert config.effective_max_concurrent_llm_tasks(testcase_name) == 33
    assert config.llm_as_a_judge_model_id is None


def test_config_override_judge_model_id():
    testcase_name = 'testcase1'
    config = EvalTaskConfig(
        name='test',
        max_concurrent_judge_tasks=2,
        max_concurrent_llm_tasks=3,
        eval_metrics=['accuracy'],
        llm_as_a_judge_name='model_a',
        llm_as_a_judge_model_id='model_b',
    )
    assert config.effective_max_concurrent_judge_tasks(testcase_name) == 2
    assert config.effective_max_concurrent_llm_tasks(testcase_name) == 3
    assert config.llm_as_a_judge_model_id == 'model_b'
