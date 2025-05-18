from simpleval.commands.init_command.base_init import BaseInit
from simpleval.commands.init_command.user_functions import get_eval_config_from_user, get_eval_dir_from_user, get_testcase_name_from_user
from simpleval.evaluation.schemas.eval_task_config_schema import EvalTaskConfig


class InitInteractive(BaseInit):
    """
    Initialize an eval set folder interactively from cli.
    """

    def __init__(self, post_instructions_start_index: int):
        super().__init__(post_instructions_start_index)

    def _get_eval_set_dir(self) -> str:
        return get_eval_dir_from_user()

    def _get_testcase_name(self) -> str:
        return get_testcase_name_from_user()

    def _get_config(self) -> EvalTaskConfig:
        return get_eval_config_from_user()

    def _print_specific_instructions(self):
        """
        No specific instructions for interactive mode.
        """
        pass
