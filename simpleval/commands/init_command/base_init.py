import json
import logging
import os
import shutil
from abc import ABC, abstractmethod
from typing import List, Tuple

from colorama import Fore

from simpleval.consts import EVAL_CONFIG_FILE, GROUND_TRUTH_FILE, LLM_TASKS_RESULT_FILE, LOGGER_NAME, TESTCASES_FOLDER
from simpleval.evaluation.llm_task_runner import PLUGIN_FILE_NAME, PLUGIN_FUNCTION_NAME
from simpleval.evaluation.schemas.eval_task_config_schema import EvalTaskConfig
from simpleval.evaluation.utils import get_empty_eval_set_folder, get_empty_testcase_folder
from simpleval.exceptions import TerminationError
from simpleval.utilities.console import print_boxed_message
from simpleval.utilities.files import is_subpath


class BaseInit(ABC):
    def __init__(self, post_instructions_start_index: int, names: Tuple[str, ...] = ()):
        """
        Args:
            post_instructions_start_index (int):  Numbered list starting index for common instructions text.
            names: Optional tuple of evaluation set names provided via CLI.
        """
        self.post_instructions_start_index = post_instructions_start_index
        self.names = names

        print_boxed_message('Create a New Evaluation-Set')

    def run_init_command(self):
        logger = logging.getLogger(LOGGER_NAME)

        empty_eval_set_folder = get_empty_eval_set_folder()
        empty_testcase_folder = get_empty_testcase_folder()

        # Get eval directories - either from CLI names or interactively
        eval_dirs = self._get_eval_dirs()

        # Validate that none of the folders already exist
        for eval_dir in eval_dirs:
            if os.path.exists(eval_dir):
                raise TerminationError(f'{Fore.RED}Folder already exists: {eval_dir}, please choose another name{Fore.RESET}')

        # Get testcase name and config once (reused for all eval sets)
        testcase = self._get_testcase_name()
        new_config = self._get_config()

        # Create each evaluation set
        created_eval_sets: List[Tuple[str, str]] = []  # List of (eval_folder, testcase_folder)
        for eval_dir in eval_dirs:
            new_eval_set_folder = eval_dir

            # Clone config and set name for this specific eval set
            config_for_eval = new_config.model_copy()
            config_for_eval.name = os.path.basename(eval_dir)

            print(f'{Fore.CYAN}Creating a new skeleton evaluation in {eval_dir}{Fore.RESET}')
            print()
            os.makedirs(new_eval_set_folder)
            new_testcases_folder = os.path.join(eval_dir, TESTCASES_FOLDER, testcase)
            os.makedirs(new_testcases_folder)

            try:
                shutil.copy(os.path.join(empty_eval_set_folder, EVAL_CONFIG_FILE), new_eval_set_folder)
                shutil.copy(os.path.join(empty_eval_set_folder, GROUND_TRUTH_FILE), new_eval_set_folder)
                shutil.copy(os.path.join(empty_eval_set_folder, 'README.md'), new_eval_set_folder)

                shutil.copy(os.path.join(empty_testcase_folder, '__init__.py'), new_testcases_folder)
                shutil.copy(os.path.join(empty_testcase_folder, PLUGIN_FILE_NAME), new_testcases_folder)
            except Exception as e:
                raise TerminationError(f'{Fore.RED}Error occurred creating the new evaluation: {e}{Fore.RESET}')

            with open(os.path.join(new_eval_set_folder, EVAL_CONFIG_FILE), 'w', encoding='utf-8') as file:
                json.dump(config_for_eval.model_dump(exclude_none=True), file, indent=4)

            logger.info(f'{Fore.GREEN}New evaluation `{config_for_eval.name}` created successfully in {eval_dir}{Fore.RESET}')
            created_eval_sets.append((new_eval_set_folder, new_testcases_folder))

        # Print instructions (use the last created eval set for examples)
        last_eval_folder, last_testcase_folder = created_eval_sets[-1]
        self._print_common_instructions_pre()
        self._print_specific_instructions()
        self._print_common_instructions_post(
            new_eval_set_folder=last_eval_folder, new_testcases_folder=last_testcase_folder, testcase=testcase
        )

    def _get_eval_dirs(self) -> List[str]:
        """
        Return list of evaluation directories.
        If names were provided via CLI, convert them to absolute paths.
        Otherwise, call the abstract method to get directory interactively.
        """
        if self.names:
            # Names provided via CLI - convert to absolute paths
            return [os.path.abspath(os.path.expanduser(name)) for name in self.names]
        else:
            # Get single directory interactively
            return [self._get_eval_set_dir()]

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
        print()
        print(f'{Fore.CYAN}Now it`s your turn, perform the following steps:{Fore.RESET}')

    def _print_common_instructions_post(self, new_eval_set_folder: str, new_testcases_folder: str, testcase: str):
        idx = self.post_instructions_start_index

        if is_subpath(new_eval_set_folder, os.getcwd()):
            eval_set_folder_to_show = os.path.relpath(new_eval_set_folder, os.getcwd())
        else:
            eval_set_folder_to_show = new_eval_set_folder

        print()
        print(
            f'{Fore.CYAN}{idx}. Populate the ground truth file: {Fore.YELLOW}{os.path.join(new_eval_set_folder, GROUND_TRUTH_FILE)}{Fore.RESET}'
        )
        idx += 1
        print(f'{Fore.CYAN}   This is a jsonl file - each line a valid json representing a test to run{Fore.RESET}')
        print(
            f'{Fore.CYAN}   set {Fore.YELLOW}`name`{Fore.RESET}, {Fore.YELLOW}`description`{Fore.CYAN} (optional) and {Fore.YELLOW}`expected_result`{Fore.RESET}'
        )
        print(
            f'{Fore.CYAN}   {Fore.YELLOW}`payload`{Fore.CYAN} is whatever you want to pass to the testcase logic (the code you`ll write in {Fore.YELLOW}`task_handler.py`{Fore.CYAN}) as json{Fore.RESET}'
        )
        print(f'{Fore.CYAN}   e.g. path to image files to use during llm inference{Fore.RESET}')
        print(f'{Fore.YELLOW}   NOTE: `name` is unique{Fore.RESET}')
        print()
        print(f'{Fore.CYAN}{idx}. Optionally update the README.md to describe the evaluation{Fore.RESET}')
        idx += 1
        print()
        print(f'{Fore.CYAN}{idx}. Implement the testcase logic{Fore.RESET}')
        idx += 1
        print(f'{Fore.CYAN}   Open {Fore.YELLOW}{os.path.join(new_testcases_folder, PLUGIN_FILE_NAME)}{Fore.RESET}')
        print(f'{Fore.CYAN}   Implement the {Fore.YELLOW}`{PLUGIN_FUNCTION_NAME}`{Fore.CYAN} function{Fore.RESET}')
        print(f'{Fore.CYAN}   This is a typical implementation:{Fore.RESET}')
        print(f'{Fore.CYAN}   - Call an llm using the input from payload{Fore.RESET}')
        print(f'{Fore.CYAN}   - When returning LlmTaskResult: ')
        print(f'{Fore.CYAN}      - Set {Fore.YELLOW}`prompt`{Fore.CYAN} with the prompt you called the llm with{Fore.RESET}')
        print(
            f'{Fore.CYAN}      - Set {Fore.YELLOW}`prediction`{Fore.CYAN} with the result from your llm call (the llm model prediction){Fore.RESET}'
        )
        print(
            f'{Fore.CYAN}      - Set {Fore.YELLOW}`name`{Fore.CYAN} and {Fore.YELLOW}`payload`{Fore.CYAN} from your input args as is - this is used by the framework as metadata{Fore.RESET}'
        )
        print()
        print(
            f'{Fore.YELLOW}   NOTE: If it recommended to implement retries on rate limit errors on the call to {Fore.YELLOW}`{PLUGIN_FUNCTION_NAME}`{Fore.RESET}'
        )
        print(
            f'{Fore.YELLOW}         Check out the built-in retry decorators in  {Fore.YELLOW}`simpleval/utilities/retryables.py`{Fore.RESET}'
        )
        print()
        print(
            f'{Fore.CYAN}See https://cyberark.github.io/simple-llm-eval/latest/users/configuration/ on how to set different concurrency per testcase{Fore.RESET}'
        )

        print()
        print(f'{Fore.CYAN}{idx}. You are ready to run the evaluation with:{Fore.RESET}')
        print(f'{Fore.YELLOW}   `simpleval run -e {eval_set_folder_to_show} -t {testcase}`{Fore.RESET}')
        print()
        print(f'{Fore.YELLOW}   NOTE: {LLM_TASKS_RESULT_FILE} is created in the testcase folder on first run{Fore.RESET}')
        print(f'{Fore.YELLOW}         if results exist from previous run you will be prompted on how to proceed{Fore.RESET}')
        print(f'{Fore.YELLOW}         you can also pass -o/--overwrite to overwrite all existing results{Fore.RESET}')
        print()

        print_boxed_message('Follow the instructions above to get started with your new eval set')
