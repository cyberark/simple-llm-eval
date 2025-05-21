import json
import logging
import os
from abc import ABC, abstractmethod

from colorama import Fore

from simpleval.consts import EVAL_CONFIG_FILE, GROUND_TRUTH_FILE, LLM_TASKS_RESULT_FILE, LOGGER_NAME, TESTCASES_FOLDER
from simpleval.evaluation.llm_task_runner import PLUGIN_FILE_NAME, PLUGIN_FUNCTION_NAME
from simpleval.evaluation.schemas.eval_task_config_schema import EvalTaskConfig
from simpleval.evaluation.utils import get_empty_eval_set_folder, get_empty_testcase_folder
from simpleval.exceptions import TerminationError


class BaseInit(ABC):
    def __init__(self, post_instructions_start_index: int):
        """
        Args:
            post_instructions_start_index (int):  Numbered list starting index for common instructions text.
        """
        self.post_instructions_start_index = post_instructions_start_index

    def run_init_command(self):
        logger = logging.getLogger(LOGGER_NAME)

        empty_eval_set_folder = get_empty_eval_set_folder()
        empty_testcase_folder = get_empty_testcase_folder()

        eval_dir = self._get_eval_set_dir()
        testcase = self._get_testcase_name()

        new_eval_set_folder = eval_dir
        if os.path.exists(new_eval_set_folder):
            raise TerminationError(f'{Fore.RED}Folder already exists: {new_eval_set_folder}, please choose another name{Fore.RESET}')

        new_config = self._get_config()
        new_config.name = os.path.basename(eval_dir)

        print(f'{Fore.CYAN}Creating a new skeleton evaluation in {eval_dir}{Fore.RESET}')
        print()
        os.makedirs(new_eval_set_folder)
        new_testcases_folder = os.path.join(eval_dir, TESTCASES_FOLDER, testcase)
        os.makedirs(new_testcases_folder)

        rc = 0
        rc += os.system(f'cp {os.path.join(empty_eval_set_folder, EVAL_CONFIG_FILE)} {new_eval_set_folder}')  # noqa
        rc += os.system(f'cp {os.path.join(empty_eval_set_folder, GROUND_TRUTH_FILE)} {new_eval_set_folder}')  # noqa
        rc += os.system(f'cp {os.path.join(empty_eval_set_folder, "README.md")} {new_eval_set_folder}')  # noqa

        rc += os.system(f'cp {os.path.join(empty_testcase_folder, "__init__.py")} {new_testcases_folder}')  # noqa
        rc += os.system(f'cp {os.path.join(empty_testcase_folder, PLUGIN_FILE_NAME)} {new_testcases_folder}')  # noqa

        if rc != 0:
            raise TerminationError(f'{Fore.RED}Error occurred during creating new evaluation{Fore.RESET}')

        with open(os.path.join(new_eval_set_folder, EVAL_CONFIG_FILE), 'w', encoding='utf-8') as file:
            json.dump(new_config.model_dump(exclude_none=True), file, indent=4)

        logger.info(f'{Fore.GREEN}New evaluation `{new_config.name}` created successfully in {eval_dir}{Fore.RESET}')

        self._print_common_instructions_pre()
        self._print_specific_instructions()
        self._print_common_instructions_post(
            new_eval_set_folder=new_eval_set_folder, new_testcases_folder=new_testcases_folder, testcase=testcase
        )

    @staticmethod
    def normalize_testcase_dir_name(testcase: str) -> str:
        """
        Normalize the testcase directory name.
        This is used to create the directory for the new testcase.
        """
        testcase = testcase.replace('-', '_')
        testcase = ''.join(c for c in testcase if c.isalnum() or c == '_')
        return testcase

    @abstractmethod
    def _get_eval_set_dir(self) -> str:
        """
        Return the directory for the new evaluation set.
        This can be an absolute or relative path.
        """

    @abstractmethod
    def _get_testcase_name(self) -> str:
        """
        Return the name of the new testcase.
        """

    @abstractmethod
    def _get_config(self) -> EvalTaskConfig:
        """
        Return the configuration for the new evaluation set.
        """
        pass

    @abstractmethod
    def _print_specific_instructions(self):
        """
        Print instructions for the user for the specific init type.
        """

    def _print_common_instructions_pre(self):
        print(f'{Fore.CYAN}Now it`s your turn, perform the following steps:{Fore.RESET}')
        print()

    def _print_common_instructions_post(self, new_eval_set_folder: str, new_testcases_folder: str, testcase: str):
        idx = self.post_instructions_start_index

        print()
        print(f'{Fore.CYAN}{idx}. Populate the ground truth file: {os.path.join(new_eval_set_folder, GROUND_TRUTH_FILE)}{Fore.RESET}')
        idx += 1
        print(f'{Fore.CYAN}   This is a jsonl file - each line a valid json representing a test to run{Fore.RESET}')
        print(f'{Fore.CYAN}   set `name`, `description` (optional) and `expected_result`{Fore.RESET}')
        print(
            f'{Fore.CYAN}   payload is whatever you want to pass to the testcase logic (the code you`ll write in `task_handler.py`) as json{Fore.RESET}'
        )
        print(f'{Fore.CYAN}   e.g. path to image files to use during llm inference{Fore.RESET}')
        print(f'{Fore.YELLOW}   NOTE: Names are unique{Fore.RESET}')
        print()
        print(f'{Fore.CYAN}{idx}. Optionally update the README.md to describe the evaluation{Fore.RESET}')
        idx += 1
        print()
        print(f'{Fore.CYAN}{idx}. Implement the testcase logic{Fore.RESET}')
        idx += 1
        print(f'{Fore.CYAN}   Open {os.path.join(new_testcases_folder, testcase, PLUGIN_FILE_NAME)}{Fore.RESET}')
        print(f'{Fore.CYAN}   Implement the `{PLUGIN_FUNCTION_NAME}` function{Fore.RESET}')
        print(f'{Fore.CYAN}   This is a typical implementation:{Fore.RESET}')
        print(f'{Fore.CYAN}   - Call an llm using the input from payload{Fore.RESET}')
        print(f'{Fore.CYAN}   - Set `prompt` with the prompt you used to call the llm{Fore.RESET}')
        print(f'{Fore.CYAN}   - Set `prediction` with the result from your llm call (the llm model prediction){Fore.RESET}')
        print(f'{Fore.CYAN}   - Set name and payload from your input args as is - this is used by the framework as metadata{Fore.RESET}')
        print(f'{Fore.YELLOW}   NOTE: If it recommended to implement retries on rate limit errors{Fore.RESET}')
        print(f'{Fore.YELLOW}         With bedrock, add @bedrock_limits_retry decorator to your `{PLUGIN_FUNCTION_NAME}`{Fore.RESET}')
        print(f'{Fore.CYAN}     See `configuration` in the docs to set different concurrency per testcase{Fore.RESET}')

        print()
        print(f'{Fore.CYAN}{idx}. You are ready to run the evaluation with:{Fore.RESET}')
        print(f'{Fore.CYAN}   `simpleval run -e {new_eval_set_folder} -t {new_testcases_folder}`{Fore.RESET}')
        print(f'{Fore.YELLOW}   NOTE: {LLM_TASKS_RESULT_FILE} is created in the testcase folder on first run{Fore.RESET}')
        print(f'{Fore.YELLOW}         if results exist from previous run you will be prompted on how to proceed{Fore.RESET}')
        print(f'{Fore.YELLOW}         you can also pass -o/--overwrite to overwrite all existing results{Fore.RESET}')
        print()

        bordered_text = 'Follow the instructions above to get started with your new eval set'
        border_wide = len(bordered_text) + 3
        print(f'{Fore.YELLOW}  {"=" * border_wide}')
        print(f'{Fore.YELLOW}  |{" " * (border_wide - 1)}|')
        print(f'{Fore.YELLOW}  | {bordered_text} |')
        print(f'{Fore.YELLOW}  |{" " * (border_wide - 1)}|')
        print(f'{Fore.YELLOW}  {"=" * border_wide}{Fore.RESET}')
