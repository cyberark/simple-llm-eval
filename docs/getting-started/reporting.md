# Reporting 📊


Currently, there are three types of reports:

* Eval results
* Comparison report
* Summary report


List report types:

```bash
simpleval reports
```

## Report Format
Usually you can select the report format with the `--report-format console` (`-r console`) argument:

* `html` - React based HTML report (default)
* `console` - Console report

## Output Directory
Reports are saved to `results` directory and can be considered as temporary files (they can be regenerated easily again)

## Eval Run Report 🏃‍♂️‍➡️

This is the basic report; it is generated when the run command finishes.
If you just want to re-generate the report, you can use the `reports eval` command instead of running the entire evaluation.

```bash
simpleval reports eval -e <eval_dir> -t <testcase>
```

You can also run it by passing the eval name and results file directly:

```bash
simpleval reports eval-file -n <eval-name> -f <eval_file>
```

<br>
<div style="text-align: center;">
    <img src="../media/report2.png" alt="Report" width="100%">
    <div style="font-size: 0.95em; color: #555; margin-top: 8px;">
        Figure: Example of an Eval Run Report in HTML format
    </div>
</div>

## Results Comparison Report 🔬

After you run more than one testcase evaluation, you can compare the results by running the compare command:

Run:

```bash
simpleval reports compare -e <eval_dir> -t1 <testcase1> -t2 <testcase2>
```


t1 and t2 are two testcases under the same evaluation set directory (they must have the same ground truths).

Better results are highlighted in green.


You can also run it by passing the eval name and results file directly:

```bash
simpleval reports compare-files -n <eval-name> -f1 <eval_file1> -f2 <eval_file2>
```

<br>
<div style="text-align: center;">
    <img src="../media/compare2.png" alt="Report" width="100%">
    <div style="font-size: 0.95em; color: #555; margin-top: 8px;">
        Figure: Example of a Result Comparison in HTML format
    </div>
</div>


## Summary Report 📊

You can also generate an overview summary of all testcases results by running:

```bash
simpleval reports summarize -e <eval_dir> -p <metric name>
```

<br>
<div style="text-align: center;">
    <img src="../media/summary2.png" alt="Report" width="75%">
    <div style="font-size: 0.95em; color: #555; margin-top: 8px;">
        Figure: Example of a summary report in HTML format
    </div>
</div>

<br>
