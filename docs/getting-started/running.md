# Running an evaluation 🏃‍♂️‍➡️ 

After you go through the init process, updated your config file if needed, defined your ground truth file and implemented your task logic, you are ready to run your first evaluation.

Run:

```bash
simpleval run -e <eval_dir> -t <testcase>
```
A report with the results and calculated scores will open and saved to `results` directory.
It includes mean score (normalized) for each test and metric.

<div style="text-align: center;">
    <img src="../media/report2.png" alt="Report" width="75%">
    <div style="font-size: 0.95em; color: #555; margin-top: 8px;">
        Figure: Example of eval results report in HTML format
    </div>
</div>

Results are saved to:

* LLM task results: `<eval_dir>/testcases/<testcase>/llm_task_results.jsonl`
* Evaluation results: `<eval_dir>/testcases/<testcase>/eval_results.jsonl`

Errors are saved to:

* LLM task errors: `<eval_dir>/testcases/<testcase>/llm_task_errors.txt`
* Evaluation errors: `<eval_dir>/testcases/<testcase>/eval_errors.txt`

## Handling errors 🐞

The report will include the number of errors. You might not care if some failed, but if you do:

* In case they are transient errors, like throttling or random parsing issues, simply run the eval again. It will run only on the missing tests.

!!! warning
    Never run with the `--overwrite` or `-o` flag if you want to retry, otherwise, it will overwrite all existing results and run everything again.

* In case they are actual error, look in the error files (location above) and solve the issue.


!!! tip
    You can use the `--verbose` or `-v` flag to get more detailed information about the errors. This will also make the error files more detailed.


## Re-running an evaluation
If you made changes to your prompts/model params/logic/etc, you want to re-run the entire evaluation.
Do this by using the `--overwrite` or `-o` flag:

```bash
simpleval run -e <eval_dir> -t <testcase> -o
```

## Generating the report
If you only want to generate a report from existing results, run:

```bash
simpleval reports eval -e <eval_dir> -t <testcase>
```
<br>
