# Exit immediately if a command exits with a non-zero status
set -e

# Parse arguments
WITH_COVERAGE=false
COVERAGE_FAIL_UNDER=90
for arg in "$@"; do
    case $arg in
        --with-coverage)
            WITH_COVERAGE=true
            shift # Remove --with-coverage from processing
            ;;
        --with-coverage=*)
            WITH_COVERAGE=true
            COVERAGE_FAIL_UNDER="${arg#*=}"
            shift # Remove --with-coverage=VALUE from processing
            ;;
    esac
done

# Pre commit
echo "Running pre-commit hooks..."
pre-commit run -a --config .config/.pre-commit-config.yaml

# Styling
echo "Running yapf formatter..."
# yapf exclude example; --exclude=.venv
yapf --in-place -vv --style=.config/.yapf_style -r --parallel simpleval
# Use diff to verify correct format in the pipeline
# yapf --diff -vv --style=.config/.yapf_style -r --parallel simpleval

echo "Running flake8 linter..."
flake8 --config .config/.flake8 simpleval

# # Complexity
# # radon exclude example; -e 'deploy.py'
echo "Running radon complexity checks..."
radon cc -n B simpleval
# # xenon exclude example; -e deploy.py,anotherfile.py -i tests,.build

echo "Running xenon complexity checks..."
xenon --max-absolute B --max-modules B --max-average B  simpleval

# # bandit security checks
# # bandit exclude example; -x ./.venv,./.dist
echo "Running bandit security checks..."
bandit -r simpleval -lll

# # Linter
echo "Running pylint linter..."
pylint --recursive=y simpleval --rcfile .config/.pylintrc

echo "Running npm audit..."
npm audit

if [ "$WITH_COVERAGE" = true ]; then
    echo "Running coverage checks with fail-under=$COVERAGE_FAIL_UNDER..."

    pytest tests/unit tests/integration -v --durations=0 --junitxml reports/codecov-test-results.xml --html=reports/codecov-test-report.html --self-contained-html --cov=. --cov-report html:reports/codecov --cov-report xml:reports/coverage.xml --cov-config=.config/.coveragerc
    coverage report --fail-under=$COVERAGE_FAIL_UNDER --precision=2 --rcfile=.config/.coveragerc
fi
