import json

from colorama import Fore

from run_commands import run_cmd


def get_pr_info(pr_number: str, field: str):
    result = run_cmd(['gh', 'pr', 'view', pr_number, '--json', field])
    try:
        data = json.loads(result.stdout)
        return data.get(field)
    except json.JSONDecodeError as e:
        raise RuntimeError(f'{Fore.RED}Failed to parse JSON output: {e}{Fore.RESET}')


def get_release_view(field: str):
    result = run_cmd(['gh', 'release', 'view', '--json', field])
    try:
        data = json.loads(result.stdout)
        return data.get(field)
    except json.JSONDecodeError as e:
        raise RuntimeError(f'{Fore.RED}Failed to parse JSON output: {e}{Fore.RESET}')
