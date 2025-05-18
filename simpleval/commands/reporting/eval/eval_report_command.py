from pydantic import ValidationError

from simpleval.commands.reporting.eval.eval_report import ResultsManager
from simpleval.evaluation.utils import get_all_eval_results, get_eval_name
from simpleval.exceptions import TerminationError


def eval_report_command(eval_dir: str, config_file: str, testcase: str, report_format: str):
    try:
        results = get_all_eval_results(eval_set_dir=eval_dir, testcase=testcase)
        results_manager = ResultsManager()
        results_manager.display_results(
            name=get_eval_name(eval_dir=eval_dir, config_file=config_file),
            testcase=testcase,
            eval_results=results,
            llm_tasks_errors_count=0,  # When running report only, we don't check for errors
            eval_errors_count=0,
            output_format=report_format,
        )

    except (FileNotFoundError, ValidationError) as ex:
        raise TerminationError(f'Error occurred trying to report results: {ex}') from ex
