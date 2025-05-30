#!/usr/bin/env python
import click
import colorama
from colorama import Fore

from simpleval.cli_args import (
    CONFIG_FILE_HELP,
    EVAL_DIR_HELP,
    EVAL_RESULTS_FILE_HELP,
    EXISTING_FILE_TYPE,
    EXISTING_FOLDER_TYPE,
    NEW_EVAL_HELP,
    NEW_FOLDER_TYPE,
    NEW_TESTCASE_HELP,
    OVERWRITE_RESULTS_HELP,
    REPORT_FORMAT_HELP,
    TESTCASE_COMPARE_FILE_HELP,
    TESTCASE_COMPARE_HELP,
    TESTCASE_HELP,
    CustomGroup,
    InNewTestcaseParamType,
    InTestcaseParamType,
)
from simpleval.consts import EVAL_CONFIG_FILE, EVAL_RESULTS_FILE, LLM_TASKS_RESULT_FILE, PACKAGE_NAME, ReportFormat
from simpleval.utilities.error_handler import handle_exceptions


@click.command(help='Run evaluation')
@click.option('--eval-dir', '-e', required=True, type=EXISTING_FOLDER_TYPE, help=EVAL_DIR_HELP)
@click.option('--config-file', '-c', type=str, default=EVAL_CONFIG_FILE, help=CONFIG_FILE_HELP)
@click.option('--testcase', '-t', required=True, type=InTestcaseParamType(), help=TESTCASE_HELP)
@click.option('--overwrite-results', '-o', is_flag=True, default=False, help=OVERWRITE_RESULTS_HELP)
@click.option(
    '--report-format',
    '-r',
    type=click.Choice([ReportFormat.CONSOLE, ReportFormat.HTML], case_sensitive=False),
    default=ReportFormat.HTML,
    help=REPORT_FORMAT_HELP,
)
@handle_exceptions
def run(eval_dir: str, testcase: str, config_file: str, overwrite_results: bool, report_format: str):
    from simpleval.commands.run_command import run_command  # Improve startup time # noqa: I001

    run_command(
        eval_dir=eval_dir, config_file=config_file, testcase=testcase, overwrite_results=overwrite_results, report_format=report_format
    )


@click.command(help='Generate evaluation report')
@click.option('--eval-dir', '-e', required=True, type=EXISTING_FOLDER_TYPE, help=EVAL_DIR_HELP)
@click.option('--config-file', '-c', type=str, default=EVAL_CONFIG_FILE, help=CONFIG_FILE_HELP)
@click.option('--testcase', '-t', required=True, type=InTestcaseParamType(), help=TESTCASE_HELP)
@click.option(
    '--report-format',
    '-r',
    type=click.Choice([ReportFormat.CONSOLE, ReportFormat.HTML], case_sensitive=False),
    default=ReportFormat.HTML,
    help=REPORT_FORMAT_HELP,
)
@handle_exceptions
def eval_report(eval_dir: str, config_file: str, testcase: str, report_format: str):
    from simpleval.commands.reporting.eval.eval_report_command import eval_report_command  # Improve startup time # noqa: I001

    eval_report_command(eval_dir=eval_dir, config_file=config_file, testcase=testcase, report_format=report_format)


@click.command(help='Generate evaluation report from results file')
@click.option('--name', '-n', required=True, type=str, help='Evaluation name')
@click.option('--eval-results-file', '-f', required=True, type=EXISTING_FILE_TYPE, help=EVAL_RESULTS_FILE_HELP)
@click.option(
    '--report-format',
    '-r',
    type=click.Choice([ReportFormat.CONSOLE, ReportFormat.HTML], case_sensitive=False),
    default=ReportFormat.HTML,
    help=REPORT_FORMAT_HELP,
)
@handle_exceptions
def eval_report_file(name: str, eval_results_file: str, report_format: str):
    from simpleval.commands.reporting.eval.eval_report_file_command import eval_report_file_command  # Improve startup time # noqa: I001

    eval_report_file_command(name=name, eval_results_file=eval_results_file, report_format=report_format)


@click.command(help='Interactive creation of a new evaluation set')
@handle_exceptions
def init():
    from simpleval.commands.init_command.init_command import init_command  # Improve startup time # noqa: I001

    init_command()


@click.command(help='Create a new evaluation using default values for a new evaluation (advanced)')
@click.option('--eval-dir', '-e', required=True, type=NEW_FOLDER_TYPE, help=NEW_EVAL_HELP)
@click.option('--testcase', '-t', required=True, type=InNewTestcaseParamType(), help=NEW_TESTCASE_HELP)
@handle_exceptions
def init_from_template(eval_dir, testcase):
    from simpleval.commands.init_command.init_from_template_command import init_from_template_command  # Improve startup time # noqa: I001

    init_from_template_command(eval_dir=eval_dir, testcase=testcase)


@click.command(help='List available llm as a judge models')
@handle_exceptions
def list_models():
    from simpleval.commands.list_models_command import list_models_command  # Improve startup time # noqa: I001

    list_models_command()


@click.command(help='Explore LiteLLM models')
@handle_exceptions
def litellm_models_explorer():
    from simpleval.commands.litellm_models_explorer_command import litellm_models_explorer_command  # Improve startup time # noqa: I001

    litellm_models_explorer_command()


@click.command(help='Explore Judges')
@handle_exceptions
def judge_explorer():
    from simpleval.commands.judge_explorer_command import judge_explorer_command  # Improve startup time # noqa: I001

    judge_explorer_command()


@click.command(help='Compare results of two evaluation runs')
@click.option('--eval-dir', '-e', required=True, type=EXISTING_FOLDER_TYPE, help=EVAL_DIR_HELP)
@click.option(
    '--testcase1', '-t1', required=True, type=InTestcaseParamType(), help=TESTCASE_COMPARE_HELP.format(id=1, file_name=EVAL_RESULTS_FILE)
)
@click.option(
    '--testcase2', '-t2', required=True, type=InTestcaseParamType(), help=TESTCASE_COMPARE_HELP.format(id=2, file_name=EVAL_RESULTS_FILE)
)
@click.option(
    '--report-format',
    '-r',
    type=click.Choice([ReportFormat.CONSOLE, ReportFormat.HTML], case_sensitive=False),
    default=ReportFormat.HTML,
    help=REPORT_FORMAT_HELP,
)
@click.option(
    '--ignore-missing-llm-results', '-i', is_flag=True, default=False, help=f'Ignore missing LLM result files ({LLM_TASKS_RESULT_FILE})'
)
@handle_exceptions
def compare(eval_dir: str, testcase1: str, testcase2: str, report_format: str, ignore_missing_llm_results: bool):
    from simpleval.commands.reporting.compare.compare_command import compare_results  # Improve startup time # noqa: I001

    compare_results(
        eval_set_dir=eval_dir,
        testcase1=testcase1,
        testcase2=testcase2,
        report_format=report_format,
        ignore_missing_llm_results=ignore_missing_llm_results,
    )


@click.command(help='Compare results of two eval results files')
@click.option('--name', '-n', required=True, type=str, help='Evaluation name')
@click.option('--eval-results-file1', '-f1', required=True, type=EXISTING_FILE_TYPE, help=TESTCASE_COMPARE_FILE_HELP)
@click.option('--eval-results-file2', '-f2', required=True, type=EXISTING_FILE_TYPE, help=TESTCASE_COMPARE_FILE_HELP)
@click.option(
    '--report-format',
    '-r',
    type=click.Choice([ReportFormat.CONSOLE, ReportFormat.HTML], case_sensitive=False),
    default=ReportFormat.HTML,
    help=REPORT_FORMAT_HELP,
)
@handle_exceptions
def compare_files(name: str, eval_results_file1: str, eval_results_file2: str, report_format: str):
    from simpleval.commands.reporting.compare.compare_command import compare_results_files  # Improve startup time # noqa: I001

    compare_results_files(
        name=name, eval_results_file1=eval_results_file1, eval_results_file2=eval_results_file2, report_format=report_format
    )


@click.command(help='Metrics Explorer')
@handle_exceptions
def metrics_explorer():
    from simpleval.commands.metrics_explorer_command import metrics_explorer_command  # Improve startup time # noqa: I001

    metrics_explorer_command()


@click.command(help='Summarize All Eval Testcases')
@click.option('--eval-dir', '-e', required=True, type=EXISTING_FOLDER_TYPE, help=EVAL_DIR_HELP)
@click.option('--config-file', '-c', type=str, default=EVAL_CONFIG_FILE, help=CONFIG_FILE_HELP)
@click.option(
    '--primary-metric', '-p', required=False, default='', type=str, help='Your primary metric - To show first (v2) or sort by (v1)'
)
@handle_exceptions
def summarize(eval_dir: str, config_file: str, primary_metric: str):
    from simpleval.commands.reporting.summarize.summarize_command import summarize_command  # Improve startup time # noqa: I001

    summarize_command(eval_dir=eval_dir, config_file=config_file, primary_metric=primary_metric)


@click.version_option(package_name=PACKAGE_NAME)
@click.group(cls=CustomGroup, invoke_without_command=True)
@click.pass_context
def main(ctx):
    colorama.init(autoreset=True)
    if not ctx.invoked_subcommand:
        click.echo('')
        welcome_message = '| Welcome to Simple LLM Eval! Use --help to see available commands. |'
        click.echo(Fore.BLUE + '+' + ('-' * (len(welcome_message) - 2)) + '+' + Fore.RESET)
        click.echo(Fore.BLUE + '| Welcome to Simple LLM Eval! Use --help to see available commands. |' + Fore.RESET)
        click.echo(Fore.BLUE + '+' + ('-' * (len(welcome_message) - 2)) + '+' + Fore.RESET)
        click.echo('')

        click.echo('Available commands:')
        for command in ctx.command.list_commands(ctx):
            cmd = ctx.command.get_command(ctx, command)
            click.echo(f'  - {Fore.CYAN}{command}{Fore.RESET}: {cmd.help}')
        click.echo('')

        click.echo('To get started:')
        click.echo('')
        click.echo(f'1. Create a new evaluation: {Fore.CYAN}`simpleval init`{Fore.RESET}')
        click.echo(f'2. Follow the on-screen instructions or run {Fore.CYAN}`simpleval --help`{Fore.RESET} for command line options')
        click.echo('3. Happy evaluation!')


@click.group(help='Commands related to reporting')
def reports():
    pass


reports.add_command(compare)
reports.add_command(compare_files)
reports.add_command(eval_report, name='eval')
reports.add_command(eval_report_file, name='eval-file')
reports.add_command(summarize)

main.add_command(list_models)
main.add_command(run)
main.add_command(init)
main.add_command(init_from_template)
main.add_command(reports)
main.add_command(metrics_explorer)
main.add_command(litellm_models_explorer)
main.add_command(judge_explorer)

if __name__ == '__main__':
    main()  # pylint: disable=no-value-for-parameter
