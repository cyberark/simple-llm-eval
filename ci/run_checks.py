#!/usr/bin/env python3
import argparse
import subprocess
import sys

COVERAGE_FAIL_UNDER = 90


def run_command(cmd, description=None):
    if description:
        print(description)
    try:
        subprocess.run(cmd, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {cmd}")
        sys.exit(e.returncode)

def main():
    parser = argparse.ArgumentParser(description="Run pre-pull-request checks.")
    parser.add_argument('--with-coverage', action='store_true', default=False, help='Run coverage checks.')
    args = parser.parse_args()


    # Pre commit
    run_command(
        cmd="pre-commit run -a --config .config/.pre-commit-config.yaml",
        description="Running pre-commit hooks..."
    )

    # Styling
    # Use diff to verify correct format in the pipeline
    # yapf --diff -vv --style=.config/.yapf_style -r --parallel simpleval
    run_command(
        cmd="yapf --in-place -vv --style=.config/.yapf_style -r --parallel simpleval",
        description="Running yapf formatter..."
    )

    run_command(
        cmd="flake8 --config .config/.flake8 simpleval",
        description="Running flake8 linter..."
    )

    # Complexity
    run_command(
        cmd="radon cc -n B simpleval",
        description="Running radon complexity checks..."
    )

    run_command(
        cmd="xenon --max-absolute B --max-modules B --max-average B simpleval",
        description="Running xenon complexity checks..."
    )

    # Security
    run_command(
        cmd="bandit -r simpleval -lll",
        description="Running bandit security checks..."
    )

    # Linter
    run_command(
        cmd="pylint --recursive=y simpleval --rcfile .config/.pylintrc",
        description="Running pylint linter..."
    )

    if args.with_coverage:
        print(f"Running coverage checks with fail-under={COVERAGE_FAIL_UNDER}...")
        run_command(
            cmd="pytest tests/unit tests/integration -v --durations=0 --junitxml reports/codecov-test-results.xml "
                "--html=reports/codecov-test-report.html --self-contained-html --cov=. --cov-report html:reports/codecov "
                "--cov-report xml:reports/coverage.xml --cov-config=.config/.coveragerc",
            description="Running pytest with coverage..."
        )
        run_command(
            cmd=f"coverage report --fail-under={COVERAGE_FAIL_UNDER} --precision=2 --rcfile=.config/.coveragerc",
            description="Checking coverage threshold..."
        )

if __name__ == "__main__":
    main()
