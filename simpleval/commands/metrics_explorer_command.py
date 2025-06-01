from colorama import Fore
from InquirerPy import prompt

from simpleval.evaluation.judges.judge_provider import JudgeProvider
from simpleval.utilities.console import print_boxed_message, print_list


def select_item(items, prompt_message, add_quit=False):
    choices = [{'name': item, 'value': item} for item in items]
    if add_quit:
        choices.append({'name': '->quit', 'value': None})

    questions = [
        {
            'type': 'list',
            'name': 'selected_item',
            'message': prompt_message,
            'choices': choices,
            'default': items[0] if items else None,  # Set the first item as the default
        }
    ]

    answers = prompt(questions)
    return answers['selected_item']


def metrics_explorer_command():
    print_boxed_message('Welcome to the metrics explorer')

    judges = JudgeProvider.list_judges()
    judge_model = select_item(judges, 'Select a judge-model to explore metrics: ')

    print()
    print(f'Selected model: {Fore.YELLOW}{judge_model}{Fore.RESET}')
    list_metrics(judge_model)


def list_metrics(judge_model: str):
    cont = 'y'
    while cont == 'y':
        print()
        judge = JudgeProvider.get_judge(judge_model)
        metrics = judge.list_metrics()
        print(f'{Fore.BLUE}Available metrics for {judge_model}:{Fore.RESET}')
        print()

        selected_metric = select_item(metrics, 'Select a metric to explore: ', f'Enter a number between 1 and {len(metrics)}')
        if selected_metric is None:
            return

        print_boxed_message(f'Selected metric: {selected_metric}')

        print(f'{Fore.BLUE}{selected_metric} description:{Fore.RESET}')
        metric = judge.get_metric(selected_metric)
        print(f'{Fore.WHITE}{metric.__doc__}{Fore.RESET}')
        print_list(
            title='    Possible responses',
            items=metric.possible_responses,
            title_color=Fore.WHITE,
            items_color=Fore.WHITE,
            tab_size=6,
        )

        print()
        cont = input(f'{Fore.MAGENTA}Continue? (y/N): {Fore.RESET}').strip().lower()
