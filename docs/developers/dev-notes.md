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

    Optionally also run `./ci/run_code_cov.py` to make sure the code coverage is adequate.

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
* Update one package: `uv lock --upgrade-package <package-name> && uv sync`
* Update all packages: `uv lock --upgrade && uv sync`
* Update dependencies constraints in `pyproject.toml` as needed

## Update npm packages 📦
* `cd reports-frontend`
* `npm update`
* `npm audit` to check for vulnerabilities

!!! warning "`npm audit fix --force` can fail with `ETARGET`"
    Our npm environment enforces a "before" date cutoff (a time-travel/reproducibility pin),
    so only package versions published before that date can be installed.

    `npm audit fix --force` always targets the *latest* fix version, which may be newer than
    the cutoff, causing `npm error code ETARGET / No matching version found ... with a date before <date>`.

    Workaround: don't use `audit fix --force`. Instead, find the latest in-range version that
    contains the fix and pin it manually in `package.json`, then `npm install`. For example,
    if the advisory is fixed in `vitest >= 4.1.0`, set `"vitest": "^4.1.0"` and run `npm install`
    (it resolves to the newest `4.1.x` available before the cutoff). Re-run `npm audit` and the
    tests/build to confirm.

## Publishing the docs 📚
This project uses mkdocs/mike to publish its docs to GitHub Pages on a release.

!!! info "What is Published Automatically"
    The release workflow will publish the docs but only for release versions, not for pre-release versions.
    
    To publish docs for pre-release versions, you can trigger the `Docs Release Manual` workflow manually.

Here are some details on how to use mike and mkdocs:

* To test the docs locally, run: `mike serve` or `mkdocs serve`
* The pipeline publishes the docs after a successful merge to main.
* There is also a manual docs publish workflow: `.github/workflows/docs-release.yml`
* Version support is handled by `mike`, see the `mkdocs.yml` file, see: https://github.com/jimporter/mike/blob/master/README.md

### Deploying the docs (performed by the pipeline)
 
* Deploy and push docs changes: `mike deploy [version] [alias] --push`, for example: `mike deploy 0.1 latest --push`
* Deploy and push alias update: `mike deploy --push --update-aliases <version> latest`
* **IMPORTANT:** `mike set-default --push latest`, to set the default version to latest

### Deleting docs versions
* To delete a version: `mike delete 0.1 --push --message "Delete version 0.1" [--update-aliases latest]`
* Delete all docs versions: `mike delete --all --push`

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
