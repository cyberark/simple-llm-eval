import os

import click
import pytest
from click import Context
from click.testing import CliRunner

from simpleval.cli_args import CustomGroup, InNewTestcaseParamType, InTestcaseParamType, is_valid_testcase
from simpleval.consts import TESTCASES_FOLDER


def test_is_valid_testcase():
    assert is_valid_testcase('valid_testcase123')
    assert not is_valid_testcase('invalid testcase!')
    assert not is_valid_testcase('invalid/testcase')
    assert not is_valid_testcase('invalid\\testcase')
    assert not is_valid_testcase('invalid*testcase')


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def eval_dir(tmp_path):
    eval_dir = tmp_path / 'eval_dir'
    eval_dir.mkdir()
    return eval_dir


@pytest.fixture
def testcase_dir(eval_dir):
    testcase_dir = eval_dir / TESTCASES_FOLDER / 'testcase1'
    testcase_dir.mkdir(parents=True)
    return testcase_dir


def test_in_testcase_param_type_valid(runner, eval_dir, testcase_dir):
    param = InTestcaseParamType()
    ctx = Context(CustomGroup('test'))
    ctx.params['eval_dir'] = str(eval_dir)
    result = param.convert('testcase1', None, ctx)
    assert result == 'testcase1'


def test_in_testcase_param_type_invalid(runner, eval_dir):
    param = InTestcaseParamType()
    ctx = Context(CustomGroup('test'))
    ctx.params['eval_dir'] = str(eval_dir)
    with pytest.raises(click.BadParameter):
        param.convert('invalid testcase!', None, ctx)


def test_in_testcase_param_type_nonexistent_folder(runner, eval_dir):
    param = InTestcaseParamType()
    ctx = Context(CustomGroup('test'))
    ctx.params['eval_dir'] = str(eval_dir)
    with pytest.raises(click.BadParameter):
        param.convert('nonexistent_testcase', None, ctx)


def test_in_new_testcase_param_type_valid(runner, eval_dir):
    param = InNewTestcaseParamType()
    ctx = Context(CustomGroup('test'))
    ctx.params['eval_dir'] = str(eval_dir)
    result = param.convert('new_testcase', None, ctx)
    assert result == 'new_testcase'


def test_in_new_testcase_param_type_invalid(runner, eval_dir):
    param = InNewTestcaseParamType()
    ctx = Context(CustomGroup('test'))
    ctx.params['eval_dir'] = str(eval_dir)
    with pytest.raises(click.BadParameter):
        param.convert('invalid testcase!', None, ctx)
