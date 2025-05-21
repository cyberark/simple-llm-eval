import os
import re

import click
from colorama import Fore

from simpleval.consts import TESTCASES_FOLDER
from simpleval.logger import DEFAULT_LOGLEVEL, VERBOSE_LOGLEVEL, init_logger

EVAL_DIR_HELP = 'Path to the evaluation directory'
CONFIG_FILE_HELP = 'Config file name'
TESTCASE_HELP = 'Testcase dir name: must exist under <eval-dir>/testcases, see simpleval/eval_sets/detect_user_action/testcases for example'
NEW_TESTCASE_HELP = 'Name of testcase to be created under <eval-dir>/testcases, for example: "claude-sonnet3.5", "prompting-techniques2"'
NEW_EVAL_HELP = 'Full or relative path of the new evaluation folder to be created'
TESTCASE_COMPARE_HELP = 'Testcase dir name {id} for comparison, must exist under <eval-dir>/testcases and contain a {file_name} to compare'
TESTCASE_COMPARE_FILE_HELP = 'eval results file to compare (by default it is `eval_results.jsonl`)'
REPORT_FORMAT_HELP = 'The report format'
OVERWRITE_RESULTS_HELP = 'Run all tests and eval again, overwriting existing results'
EVAL_RESULTS_FILE_HELP = 'Path to the eval results file'

EXISTING_FILE_TYPE = click.Path(exists=True, file_okay=True, dir_okay=False, readable=True, writable=True)
EXISTING_FOLDER_TYPE = click.Path(exists=True, file_okay=False, dir_okay=True, readable=True, writable=True)
NEW_FOLDER_TYPE = click.Path(file_okay=False, dir_okay=True, readable=True, writable=True, resolve_path=True)

TESTCASE_ARG_ERROR = 'testcase can only contain `A-Za-z0-9_-`, it should be a dir name that exists under {eval_dir}'


def is_valid_testcase(testcase: str) -> bool:
    pattern = r'^[A-Za-z0-9_-]+$'
    return bool(re.match(pattern, testcase))


class CustomGroup(click.Group):
    def parse_args(self, ctx, args):
        console_log_level = DEFAULT_LOGLEVEL
        if '--verbose' in args or '-v' in args:
            console_log_level = VERBOSE_LOGLEVEL
            args = [arg for arg in args if arg not in ('--verbose', '-v')]

        init_logger(console_log_level)
        super().parse_args(ctx, args)


class InTestcaseParamType(click.ParamType):
    name = 'testcase'

    def convert(self, value, param, ctx):
        eval_dir = ctx.params.get('eval_dir')
        if not eval_dir:
            self.fail('eval_dir is required', param, ctx)

        if not is_valid_testcase(value):
            self.fail(TESTCASE_ARG_ERROR.format(eval_dir=eval_dir), param, ctx)

        expected_testcase_folder = os.path.join(eval_dir, TESTCASES_FOLDER, value)
        if not os.path.isdir(expected_testcase_folder):
            all_testcases = (
                [
                    f
                    for f in os.listdir(os.path.join(eval_dir, TESTCASES_FOLDER))
                    if os.path.isdir(os.path.join(eval_dir, TESTCASES_FOLDER, f))
                ]
                if os.path.isdir(os.path.join(eval_dir, TESTCASES_FOLDER))
                else []
            )

            print(f'{Fore.CYAN}Available testcases: {all_testcases}{Fore.RESET}')
            self.fail(f'{value} must be a dir under {eval_dir}, see available testcases above', param, ctx)

        return value


class InNewTestcaseParamType(click.ParamType):
    name = 'testcase'

    def convert(self, value, param, ctx):
        eval_dir = ctx.params.get('eval_dir')
        if not eval_dir:
            self.fail('eval_dir is required', param, ctx)

        if not is_valid_testcase(value):
            self.fail(TESTCASE_ARG_ERROR.format(eval_dir=eval_dir), param, ctx)

        return value
