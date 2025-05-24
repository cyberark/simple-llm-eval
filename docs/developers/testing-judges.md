# Testing the judges 👩‍⚖️🧑‍⚖️

## Minimal Judge Tests

A minimal test to verify that the main judges are working as expected is include here:

`tests/integration/test_judges_minimal.py:test_judges_minimal`

Since it consumes LLM tokens, it does not run by default.
It requires credentials for all relevant providers.

To run these tests set this environment variable:

`RUN_ALL_MINIMAL_JUDGE_TESTS=1`

For example:

```bash
RUN_ALL_MINIMAL_JUDGE_TESTS=1 pytest -v tests/integration/test_judges_minimal.py```
```

There are also provider specific environment variables (see in code).

## In-Depth Judge Tests

To make sure that the LLM as a judge implementation is working as expected, you can run the judges on a set of evaluation sets for three use cases: "Classify products", "Detect Toxicity" and "Spam Detection".

!!! info
    The ground truth for each evaluation is kept here, by provider:
    `tests/resources/llm_as_a_judge_test_eval_results_golden_set`

    The last results for each evaluation and provider and the config file needed to run the eval are kept here:
    `tests/resources/llm_as_a_judge_datasets`

    
The `tests/integration/test_llm_as_a_judge.py` integration test runs in the pipeline, but it compares the static results with the ground truth. **In case there are changes in the prompt, models used, model parameters, etc.**, you should run the evaluation again for the relevant judge(s) and update the static results.

## Running the Evaluations 🏃‍♂️‍➡️

You can run all evaluation for a judge with this script:
```bash
python tools/run_all_llm_as_a_judge_tests.py --config-file <config> 
```

The code retries on errors, but if you still get temporary errors (like throttling, parsing issues), simply run again without overwriting. This usually finishes the failed tests:

```bash
python tools/run_all_llm_as_a_judge_tests.py --config-file <config> --do-not-overwrite-eval-results
```

!!! example
    ```bash
    python tools/run_all_llm_as_a_judge_tests.py -c tests/resources/llm_as_a_judge_datasets/classify_product/eval_set/config_open_ai.json
    ```

!!! warning
    Make sure to run with `-d` if you only want to rerun the failed tests, otherwise it will delete the previous results.

Use the `--help` flag to see all the options, `-v` for verbose output.


## View the reports 📊
To open the reports for a specific judge use this script and select the judge you want to use:

```bash
python tools/show_reports_for_all_llm_as_a_judge_tests.py
```

Use the `--help` flag to see all the options.

<br>
