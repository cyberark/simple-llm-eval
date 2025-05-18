import subprocess

import pytest

from simpleval.commands import list_models_command


def test_list_models_command_cli():
    result = subprocess.run(['simpleval', 'list-models'], capture_output=True, text=True)
    assert result.returncode == 0, f'Command failed with return code {result.returncode} and output: {result.stdout} {result.stderr}'


def test_list_models_command():
    list_models_command.list_models_command()
