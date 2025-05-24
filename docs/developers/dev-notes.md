# Dev Notes 👩‍💻

## Breaking Changes ⛓️‍💥

!!! danger
    Make sure you don't introduce breaking changes unless you have to (in which case up the major version)

    Breaking changes affect the implementation of task_handler.py

    Specifically:

    * The name of the file must be `task_handler.py`
    * The signature of the `task_logic` function must be `task_logic(name: str, payload: dict) -> LlmTaskResult`
    * Handlers are expected to use the `simpleval.utilities.retryables.bedrock_limits_retry` decorator as is.
    * The structure of the `ground_truth.jsonl` file must not change (see `base_eval_case_schema.GroundTruth`).
    * The structure of result files must not change (see `eval_result_schema.EvalTestResult`, `llm_task_result.LlmTaskResult`).

## Pre-requisites 🛠️
* Python 3.11 or higher
* The `uv` package manager
* Only for reporting dev: `npm`

## Getting Started 🚀
* Clone this repo
* Install all dependencies: `uv sync`
* Activate the virtual environment: <br>`source .venv/bin/activate` (Linux/Mac)
<br>or
<br>`.venv\Scripts\activate` (Windows)

## Running all checks 🔍

!!! info "Main checks"
    Run the the `ci/run_checks.py` script
    This will run the following checks:
    
    * pre-commit hooks: formatting and ruff
    * ruff covers linting, formatting, isort and seurity checks
    * radon and xenon for code complexity
    * Code coverage checks - must be above 90%
    * Verify uv.lock and requirements.txt are synced

!!! info "React checks"
      If you made changes to the `reports-frontend` reports, run the `ci/run_checks_react.py` script
      This will run the following steps:

      * npm install, build
      * run the tests
      * npm audit

**The same checks will run in the pipeline as well.**

### Update the pre-commit hooks
Once in a while update the pre-commit hooks to the latest version:

`pre-commit autoupdate --repo https://github.com/pre-commit/pre-commit-hooks --config .config/.pre-commit-config.yaml`

## Building the Package 🏗️
* Build the package using: `uv build`

## Useful uv Commands 🛠️
* Install all dependencies: `uv sync`
* Update one package: `uv add <existing-package-name>`
* Update all packages: `uv lock --upgrade && uv sync`

## Publishing the docs
This project uses mkdocs/mike to publish its docs to GitHub Pages on a release.

Here are some details on how to use mike and mkdocs:

* To test the docs locally, run: `mike serve` or `mkdocs serve`
* The pipeline publishes the docs after a successful merge to main.
* Version support is handled by `mike`, see the `mkdocs.yml` file, see: https://github.com/jimporter/mike/blob/master/README.md
* The docs use the [major].[minor] versioning scheme

### Deploying the docs (performed by the pipeline)
* `mike deploy [version] [alias]`, for example: `mike deploy 0.1 latest`
* `mike set-default latest`, to set the default version to latest
* Test locally with `mike serve`
* To push the changes: `mike deploy --push --update-aliases <version> latest`
* To delete a version: `mike delete [version-or-alias]`

## CLI Dev
The CLI uses the click library, see commands package for examples.

> NOTE: When updating the CLI commands, make sure to run `uv install` to install the dev package so you can run the CLI locally with the latest changes.

## LLM as a Judge 👩‍⚖️

`simpleval` comes with a bunch of judges out of the box: one uses boto3 natively for Bedrock, and all others use Lite LLM to unify the interface for any LLM provider.


It is recommended to use the Lite LLM interface for any new judge you want to implement, as it is more flexible and allows you to use any LLM provider.
See `simpleval/evaluation/judges/models/open_ai/judge.py` for an example of how to implement a judge using Lite LLM, which is super easy.
All Lite LLM-based judges use the same prompts for metrics.

!!! note
    * Lite LLM judges must use models that support structured outputs. Use the `simpleval litellm-models-explorer` to find such models by provider.
    * If you implement a new judge type, make sure you implement a retry decorator (see existing judges for examples).

## Reports 📊

There are three types of report implementations:


- ✅ The new reports are React-based, are feature-rich, and look much better. See [Reporting Dev](reporting-dev.md) for more details.
- ❌ Simple HTML reports, which are deprecated. They are based on an HTML template and are implemented in `simpleval/commands/reporting/eval_report/html_report.py` and `simpleval/commands/reporting/compare/compare_html.py`. 
  <br>**You should refrain from making changes to these files and keep to the new formats.**
- ❌ A matplotlib-based summary report, which is also deprecated. **Use the new formats instead.**

<br>
