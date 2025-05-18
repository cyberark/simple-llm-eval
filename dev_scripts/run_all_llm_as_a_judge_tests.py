from dotenv import load_dotenv

load_dotenv()

import argparse
import os
import time
from pathlib import Path

from colorama import Fore
from InquirerPy import prompt

from simpleval.commands.run_command import run_command
from simpleval.evaluation.judges.judge_provider import JudgeProvider
from simpleval.exceptions import NoWorkToDo
from simpleval.logger import DEFAULT_LOGLEVEL, VERBOSE_LOGLEVEL, init_logger


def run_tests_with_retry(eval_set_dir: str, config_file: str, testcase: str, overwrite_results: bool, judge: str):
    """Run tests with retry logic, continuing as long as total errors decrease."""
    print(f'Running test for {eval_set_dir.parent.parent.name}/{testcase}...')

    total_errors = float('inf')  # Start with infinity to ensure first run happens
    prev_total_errors = float('inf')
    retry_count = 0

    while True:
        if retry_count > 0:
            sleep_time_sec = 20
            print(f'{Fore.YELLOW}Waiting for {sleep_time_sec} seconds before retrying to help with rate limits...{Fore.RESET}')
            time.sleep(sleep_time_sec)

        retry_count += 1
        print(f'Run #{retry_count}...')

        try:
            llm_errors, eval_errors = run_command(
                eval_dir=eval_set_dir,
                config_file=config_file,
                testcase=testcase,
                overwrite_results=overwrite_results,
                report_format='console',
            )
            total_errors = llm_errors + eval_errors
            print(f'Results: {llm_errors=}, {eval_errors=}')
        except NoWorkToDo:
            print(f'{Fore.YELLOW}No work to do. Skipping this test case.{Fore.RESET}')
            llm_errors, eval_errors = 0, 0
            return llm_errors, eval_errors
        except Exception as e:
            print(f'{Fore.RED}Error during test run: {e}{Fore.RESET}')
            llm_errors = eval_errors = total_errors = float('inf')

        print(f'Total errors: {total_errors}')

        if total_errors == 0:
            print(f'{Fore.GREEN}Success! No errors found.{Fore.RESET}')
            break

        if total_errors >= prev_total_errors:
            print(f'{Fore.RED}No improvement in error count. Stopping retries.{Fore.RESET}')
            break

        print(f'{Fore.YELLOW}Error count decreased from {prev_total_errors} to {total_errors}. Retrying...{Fore.RESET}')
        prev_total_errors = total_errors

    if retry_count > 1:
        print(f'Finished retrying after {retry_count} attempts. Final error count: {total_errors}')

    return llm_errors, eval_errors


def main():
    parser = argparse.ArgumentParser(description='Script to process configuration and overwrite options.')
    parser.add_argument('--config-file', '-c', type=str, default='', help='Path to the eval set configuration file.')
    parser.add_argument('--do-not-overwrite-eval-results', '-d', action='store_true',
                        help='Do not overwrite eval results, continue from with existing eval results.')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose output.')

    args = parser.parse_args()

    print(f'{args.config_file=}')
    print(f'{args.do_not_overwrite_eval_results=}')

    if args.verbose:
        print(f'{Fore.GREEN}Verbose mode enabled.{Fore.RESET}')
        os.environ['LOG_LEVEL'] = 'DEBUG'

    log_level = DEFAULT_LOGLEVEL if not args.verbose else VERBOSE_LOGLEVEL
    init_logger(log_level)

    print('This script runs the LLM as a judge tests for all datasets and test cases for a given configuration file.')
    print('Use the config file to set the judge model that you want to use for testing.')
    print('By default, the script will keep the llm task results - there is no reason to run those again, since we are testing the judge')
    print('By default the scrip will delete the eval results and run them again. It will retry until it is successful in running all tests')
    print('If for some reason retrying wasnt enough, you can use --do-not-overwrite-eval-results to keep the existing eval results')

    if not args.config_file:
        judges = JudgeProvider.list_judges(filter_internal=True)
        questions = [{'type': 'list', 'name': 'judge', 'message': 'Select a judge:', 'choices': judges}]
        answers = prompt(questions)
        selected_judge = answers['judge']
        args.config_file = f'config_{selected_judge}.json'

    llm_as_a_judge_tests_root = Path('tests/resources/llm_as_a_judge_datasets')
    datasets = ['classify_product', 'detect_toxicity', 'spam_detection']
    testcases = ['good_prompt', 'bad_prompt']

    total_errors = 0

    for dataset in datasets:
        for testcase in testcases:
            print(f'Running tests for {dataset}/{testcase}...')

            eval_set_dir = Path(llm_as_a_judge_tests_root, dataset, 'eval_set')
            eval_results_file = Path(eval_set_dir, 'testcases', testcase, 'eval_results.jsonl')

            if not args.do_not_overwrite_eval_results:
                print(f'Deleting existing eval results for {dataset}/{testcase}')
                if eval_results_file.exists():
                    eval_results_file.unlink()

            llm_errors, eval_errors = run_tests_with_retry(eval_set_dir=eval_set_dir, config_file=args.config_file, testcase=testcase,
                                                           overwrite_results=False, judge=selected_judge)
            total_errors += llm_errors + eval_errors

            print(f'Finished running tests for {dataset}/{testcase}. {llm_errors=}, {eval_errors=}')

            judge_eval_results_file = Path(eval_set_dir, 'testcases', testcase, f'eval_results_{selected_judge}.jsonl')
            print(f'Copying eval results to judge-specific file: {judge_eval_results_file}')
            if eval_results_file.exists():
                judge_eval_results_file.write_text(eval_results_file.read_text())
            else:
                total_errors += 1
                print(f'{Fore.RED}Eval results file does not exist: {eval_results_file}{Fore.RESET}')

    if total_errors > 0:
        print(f'{Fore.RED}Errors were found during the tests even after retries. Please check the logs for details.{Fore.RESET}')
        print(f'{Fore.RED}Error logs can be found in: {eval_set_dir}/testcases/<testcase>{Fore.RESET}')
        print(
            f'{Fore.RED}To run only failed tests: `python dev_utils/run_all_llm_as_a_judge_tests.py -d` and select the same judge{Fore.RESET}'
        )


if __name__ == '__main__':
    main()
