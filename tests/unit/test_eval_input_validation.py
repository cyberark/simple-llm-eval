import os

import pytest

from simpleval.consts import EVAL_CONFIG_FILE
from simpleval.validations import validate_eval_input
from tests.unit.utils import get_test_resources_folder


def test_validate_default_eval_input():
    default_testcase = os.path.join(get_test_resources_folder(), 'eval_sets', 'valid')
    validate_eval_input(eval_dir=default_testcase, config_file=EVAL_CONFIG_FILE)


def test_duplicates_eval_input_raises():
    default_testcase = os.path.join(get_test_resources_folder(), 'eval_sets', 'duplicates')

    with pytest.raises(ValueError):
        validate_eval_input(eval_dir=default_testcase, config_file=EVAL_CONFIG_FILE)
