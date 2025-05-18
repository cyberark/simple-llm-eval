import os

from colorama import Fore

from simpleval.commands.init_command.base_init import BaseInit
from simpleval.consts import EVAL_CONFIG_FILE
from simpleval.evaluation.schemas.eval_task_config_schema import EvalTaskConfig
from simpleval.evaluation.utils import get_empty_eval_set_folder, get_eval_config


class InitFromTemplate(BaseInit):
    """
    Command to initialize a project from a template.
    """

    def __init__(self, eval_dir: str, testcase: str, post_instructions_start_index: int):
        super().__init__(post_instructions_start_index)
        self.eval_dir = eval_dir
        self.testcase = BaseInit.normalize_testcase_dir_name(testcase)

    def _get_eval_set_dir(self):
        return self.eval_dir

    def _get_testcase_name(self):
        return self.testcase

    def _get_config(self) -> EvalTaskConfig:
        return get_eval_config(
            eval_dir=get_empty_eval_set_folder(),
            config_file=EVAL_CONFIG_FILE,
            verify_metrics=False,
        )

    def _print_specific_instructions(self):
        print(f'{Fore.CYAN}1. Open the new config file: {os.path.join(self.eval_dir, EVAL_CONFIG_FILE)}{Fore.RESET}')
        print()
        print(f'{Fore.CYAN}   1.1. run `simpleval list-models` to list available judge models{Fore.RESET}')
        print()
        print(f'{Fore.CYAN}   1.2. Set `llm_as_a_judge_name=<judge model>`{Fore.RESET}')
        print()
        print(f'{Fore.CYAN}   1.3. You must set `eval_metrics` with the list of llm metrics to run (e.g "correctness"){Fore.RESET}')
        print(f'{Fore.CYAN}     to show available metrics run:{Fore.RESET}')
        print(f'{Fore.CYAN}     `simpleval run -e {self.eval_dir} -t {self.testcase}`{Fore.RESET}')
        print(f'{Fore.CYAN}     To learn more about these metrics, see the docstring in the metric files under:{Fore.RESET}')
        print(f'{Fore.CYAN}     `simpleval/evaluation/metrics/sonnet35` or another llm model{Fore.RESET}')
        print(
            f'{Fore.YELLOW}     NOTE: Not sure? use ["completeness", "correctness"] for non RAG tasks, RAG task? invest the time to learn{Fore.RESET}'
        )
        print()
        print(f'{Fore.CYAN}   1.4. Advanced: `max_concurrent_judge_tasks` and `max_concurrent_llm_tasks` are used to decide{Fore.RESET}')
        print(f'{Fore.CYAN}     how many eval and test tasks to run in parallel, if not sure, leave as the default{Fore.RESET}')

        print()
        print(f'{Fore.CYAN}   1.5. In case you want to override `max_concurrent_judge_tasks` and/or `max_concurrent_llm_tasks`{Fore.RESET}')
        print(f'{Fore.CYAN}     For specific testcases, see the `configuration` section in the docs{Fore.RESET}')
