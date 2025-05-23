#!/usr/bin/env python3
import argparse
import hashlib
from pathlib import Path
import shutil
import subprocess
import sys

from colorama import Fore


COVERAGE_FAIL_UNDER = 90


def run_command(cmd, description=None):
    if description:
        print(f'{Fore.CYAN}{description}{Fore.RESET}')
    try:
        subprocess.run(cmd, shell=True, check=True)
        print()
    except subprocess.CalledProcessError as e:
        print(f'{Fore.RED}Command failed, if fixes attempted, run again: {cmd}{Fore.RESET}')
        sys.exit(e.returncode)

def update_requirements_txt():
    ci_path = Path(__file__).parent
    requirements_temp_path = ci_path / 'requirements-temp.txt'

    simpleval_path = ci_path.parent
    requirements_path = simpleval_path / 'requirements.txt'

    cmd = 'uv export --format requirements-txt > {requirements_path}'

    run_command(
        cmd=cmd.format(requirements_path=requirements_temp_path),
        description='Updating requirements-temp.txt...'
    )

    hash_req_temp = hashlib.sha256(open(requirements_temp_path, 'rb').read()).hexdigest()
    hash_req = hashlib.sha256(open(requirements_path, 'rb').read()).hexdigest()

    if hash_req_temp != hash_req:
        print(f'{Fore.CYAN}Updating requirements.txt...{Fore.RESET}')
        shutil.copyfile(requirements_temp_path, requirements_path)
        print(f'{Fore.RED}Command failed: requirements.txt updated, stopping, run again to verify.{Fore.RESET}')
        sys.exit(1)
    else:
        print(f'{Fore.GREEN}requirements.txt is up to date{Fore.RESET}')



def main():
    parser = argparse.ArgumentParser(description='Run pre-pull-request checks.')
    parser.add_argument('--with-coverage', action='store_true', default=False, help='Run coverage checks.')
    args = parser.parse_args()


    # Pre commit
    run_command(
        cmd='pre-commit run -a --config .config/.pre-commit-config.yaml',
        description='Running pre-commit hooks...'
    )

    # Complexity
    run_command(
        cmd='radon cc -n B simpleval',
        description='Running radon complexity checks...'
    )

    run_command(
        cmd='xenon --max-absolute B --max-modules B --max-average B simpleval',
        description='Running xenon complexity checks...'
    )

    update_requirements_txt()

    if args.with_coverage:
        print(f'{Fore.CYAN}Running coverage checks with fail-under={COVERAGE_FAIL_UNDER}...{Fore.RESET}')
        run_command(
            cmd='pytest tests/unit tests/integration -v --durations=0 --junitxml reports/codecov-test-results.xml '
                '--html=reports/codecov-test-report.html --self-contained-html --cov=. --cov-report html:reports/codecov '
                '--cov-report xml:reports/coverage.xml --cov-config=.config/.coveragerc',
            description='Running pytest with coverage...'
        )
        run_command(
            cmd=f'coverage report --fail-under={COVERAGE_FAIL_UNDER} --precision=2 --rcfile=.config/.coveragerc',
            description='Checking coverage threshold...'
        )

if __name__ == '__main__':
    main()
