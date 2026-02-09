import copy
import os

from simpleval.commands.init_command.base_init import BaseInit
from simpleval.commands.init_command.user_functions import get_eval_config_from_user, get_eval_dir_from_user, get_testcase_name_from_user
from simpleval.evaluation.schemas.eval_task_config_schema import EvalTaskConfig
from simpleval.exceptions import TerminationError
from colorama import Fore


class InitInteractive(BaseInit):
    """
    Initialize an eval set folder interactively from cli.
    """

    def __init__(self, post_instructions_start_index: int, eval_dir: str | None = None, testcase: str | None = None, config: EvalTaskConfig | None = None):
        self._preset_eval_dir = eval_dir
        self._preset_testcase = testcase
        self._preset_config = config
        super().__init__(post_instructions_start_index)

    def _get_eval_set_dir(self) -> str:
        if self._preset_eval_dir:
            # Validate the preset name doesn't exist
            eval_dir = os.path.abspath(os.path.expanduser(self._preset_eval_dir))
            if os.path.exists(eval_dir):
                raise TerminationError(f'{Fore.RED}Folder already exists: {eval_dir}, please choose another name{Fore.RESET}')
            return eval_dir
        return get_eval_dir_from_user()

    def _get_testcase_name(self) -> str:
        if self._preset_testcase:
            return BaseInit.normalize_testcase_dir_name(self._preset_testcase)
        return get_testcase_name_from_user()

    def _get_config(self) -> EvalTaskConfig:
        if self._preset_config:
            # Create a deep copy so modifying the name doesn't affect the original
            return copy.deepcopy(self._preset_config)
        return get_eval_config_from_user()

    def _print_specific_instructions(self):
        """
        No specific instructions for interactive mode.
        """
        pass
