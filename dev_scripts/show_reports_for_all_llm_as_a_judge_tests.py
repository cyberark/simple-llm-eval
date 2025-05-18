import argparse
import os
from pathlib import Path

from colorama import Fore
from InquirerPy import prompt

from simpleval.commands.reporting.eval.eval_report_command import eval_report_command
from simpleval.consts import ReportFormat
from simpleval.evaluation.judges.judge_provider import JudgeProvider


def main():
    parser = argparse.ArgumentParser(description='Script to process configuration and overwrite options.')
    parser.add_argument('--judge', '-j', type=str, default='', help='Judge name to use, if not provided, will prompt for a judge.')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose output.')
    args = parser.parse_args()

    print(f'{args.judge=}')

    if args.verbose:
        print(f'{Fore.GREEN}Verbose mode enabled.{Fore.RESET}')
        os.environ['LOG_LEVEL'] = 'DEBUG'

    if args.judge:
        selected_judge = args.judge
    else:
        judges = JudgeProvider.list_judges(filter_internal=True)
        questions = [{'type': 'list', 'name': 'judge', 'message': 'Select a judge:', 'choices': judges}]
        answers = prompt(questions)
        selected_judge = answers['judge']

    judge_eval_results_file = f'eval_results_{selected_judge}.jsonl'

    llm_as_a_judge_tests_root = Path('tests/resources/llm_as_a_judge_datasets')
    datasets = ['classify_product', 'detect_toxicity', 'spam_detection']
    testcases = ['good_prompt', 'bad_prompt']

    for dataset in datasets:
        for testcase in testcases:
            print(f'Generating run report for {dataset}/{testcase}...')

            eval_set_dir = Path(llm_as_a_judge_tests_root, dataset, 'eval_set')
            judge_eval_results_path = Path(eval_set_dir, 'testcases', testcase, judge_eval_results_file)
            eval_results_path = Path(eval_set_dir, 'testcases', testcase, 'eval_results.jsonl')
            eval_results_path.write_text(judge_eval_results_path.read_text())

            eval_report_command(
                eval_dir=str(eval_set_dir),
                config_file=f'config_{selected_judge}.json',
                testcase=testcase,
                report_format=ReportFormat.HTML2,
            )


if __name__ == '__main__':
    main()
