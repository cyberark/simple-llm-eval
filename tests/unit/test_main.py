import inspect
import subprocess

import click

from simpleval import main


def test_all_commands_added_to_main():

    custom_names = {
        'eval-report': 'eval',
        'eval-report-file': 'eval-file',
    }

    commands_from_inspection = [name for name, obj in inspect.getmembers(main) if isinstance(obj, click.core.Command) and name != 'main']
    commands_from_inspection = [name.replace('_', '-') for name in commands_from_inspection]
    commands_from_inspection = [custom_names.get(name, name) for name in commands_from_inspection]

    added_commands_main = list(main.main.commands.keys())
    added_commands_reports = list(main.reports.commands.keys())

    assert commands_from_inspection

    error = 'Not all commands were added to main or reports'
    assert set(commands_from_inspection) == set(added_commands_main + added_commands_reports), error
    assert len(commands_from_inspection) == len(added_commands_main) + len(added_commands_reports)


def test_run_main_without_args():
    result = subprocess.run(['simpleval'], capture_output=True)
    assert result.returncode == 0, 'Main did not return 0 when run without arguments'
