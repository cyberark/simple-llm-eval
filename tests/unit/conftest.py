import os

from simpleval.commands.run_command import run_command
from simpleval.consts import EVAL_CONFIG_FILE, EVAL_ERROR_FILE_NAME, LLM_TASKS_ERROR_FILE_NAME, ReportFormat
from tests.unit.test_testcases import TEST_EVAL_SET_VALID_FOLDER, TEST_FOO_TESTCASE_NAME


# Test
def pytest_configure():
    try:
        # os.environ['LOG_LEVEL'] = 'DEBUG'

        print('Running test setup during conftest (look here for errors if your tests are not running)')
        run_command(
            eval_dir=TEST_EVAL_SET_VALID_FOLDER,
            config_file=EVAL_CONFIG_FILE,
            testcase=TEST_FOO_TESTCASE_NAME,
            report_format=ReportFormat.CONSOLE,
            overwrite_results=True,
        )
    finally:
        llm_error_file = os.path.join(TEST_EVAL_SET_VALID_FOLDER, 'testcases', TEST_FOO_TESTCASE_NAME, LLM_TASKS_ERROR_FILE_NAME)
        eval_error_file_name = os.path.join(TEST_EVAL_SET_VALID_FOLDER, 'testcases', TEST_FOO_TESTCASE_NAME, EVAL_ERROR_FILE_NAME)

        if os.path.exists(llm_error_file):
            with open(llm_error_file, 'r', encoding='utf-8') as f:
                llm_errors = f.read()
            print(f'Error found during llm task run: {llm_error_file}, set LOG_LEVEL=DEBUG to see more details')

        if os.path.exists(eval_error_file_name):
            with open(eval_error_file_name, 'r', encoding='utf-8') as f:
                eval_errors = f.read()
            print(f'Error found during eval run: {eval_error_file_name}, set LOG_LEVEL=DEBUG to see more details')
            print(eval_errors)
