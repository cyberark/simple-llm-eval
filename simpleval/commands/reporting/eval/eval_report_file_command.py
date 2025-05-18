from pathlib import Path

from pydantic import ValidationError

from simpleval.commands.reporting.eval.eval_report import ResultsManager
from simpleval.evaluation.utils import get_all_eval_results_from_file
from simpleval.exceptions import TerminationError


def eval_report_file_command(name: str, eval_results_file: str, report_format: str):
    try:
        results = get_all_eval_results_from_file(eval_results_file=eval_results_file, fail_on_missing=False)
        results_manager = ResultsManager()
        results_manager.display_results(
            name=name,
            testcase=str(Path(eval_results_file).stem),
            eval_results=results,
            llm_tasks_errors_count=0,  # When running report only, we don't check for errors
            eval_errors_count=0,
            output_format=report_format,
        )

    except (FileNotFoundError, ValidationError) as ex:
        raise TerminationError(f'Error occurred trying to report results: {ex}') from ex
