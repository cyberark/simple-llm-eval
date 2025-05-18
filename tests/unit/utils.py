from pathlib import Path


def get_testcases_folder():
    return Path(__file__).parent.parent.parent / 'simpleval' / Path('testcases')


def get_eval_sets_folder():
    return Path(__file__).parent.parent.parent / 'simpleval' / Path('eval_sets')


def get_test_resources_folder():
    return Path(__file__).parent.parent / 'resources'
