from typing import Counter

from simpleval.consts import GROUND_TRUTH_FILE
from simpleval.evaluation.utils import get_eval_config, get_eval_ground_truth


def validate_eval_input(eval_dir: str, config_file: str):
    eval_cases = get_eval_ground_truth(eval_dir)
    eval_cases_names = [eval_case.name for eval_case in eval_cases]
    duplicate_names = [name for name, freq in Counter(eval_cases_names).items() if freq > 1]
    if duplicate_names:
        raise ValueError(f'Duplicate name(s) found in {GROUND_TRUTH_FILE}: {duplicate_names}')

    get_eval_config(eval_dir=eval_dir, config_file=config_file)
