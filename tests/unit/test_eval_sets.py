import json
import os

import pytest

from simpleval.consts import EVAL_CONFIG_FILE
from simpleval.evaluation.schemas.base_eval_case_schema import GroundTruth
from simpleval.evaluation.schemas.eval_task_config_schema import EvalTaskConfig
from simpleval.evaluation.utils import get_eval_config, get_eval_ground_truth
from tests.unit.utils import get_eval_sets_folder


@pytest.mark.parametrize('eval_dir', [f'{get_eval_sets_folder()}/detect_user_action', f'{get_eval_sets_folder()}/dummy_task'])
def test_verify_eval_set(eval_dir):
    result = get_eval_ground_truth(eval_dir)
    assert len(result) > 0
    assert isinstance(result[0], GroundTruth)

    config = get_eval_config(eval_dir=eval_dir, config_file=EVAL_CONFIG_FILE)
    assert isinstance(result[0], GroundTruth)


def test_verify_empty_eval_set():
    eval_dir = f'{get_eval_sets_folder()}/empty'
    result = get_eval_ground_truth(eval_dir)
    assert len(result) > 0
    assert isinstance(result[0], GroundTruth)

    with open(os.path.join(eval_dir, EVAL_CONFIG_FILE), 'r', encoding='utf-8') as file:
        config_data = json.load(file)
        eval_config = EvalTaskConfig(**config_data)
