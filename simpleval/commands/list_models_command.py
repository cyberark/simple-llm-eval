from simpleval.evaluation.judges.judge_provider import JudgeProvider
from simpleval.utilities.console import print_boxed_message, print_list


def list_models_command():
    print_boxed_message('List Available LLM as a Judge Models')

    print_list(
        title='Available llm as a judge models',
        items=JudgeProvider.list_judges(filter_internal=True),
    )
