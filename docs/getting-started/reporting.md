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
    <img id="reportImage" src="../media/report2.png" alt="Report" width="75%">
</div>
<div style="text-align: center;">
    <button onclick="toggleReportImage()">[See alternative report format]</button>
</div>

<script>
function toggleReportImage() {
    var img = document.getElementById('reportImage');
    if (img.src.includes('report.png')) {
        img.src = '../media/report2.png';
    } else {
        img.src = '../media/report.png';
    }
}
</script>

## Comparing Results Report 🔬

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
<br>
<div style="text-align: center;">
    <img id="compareReportImage" src="../media/compare2.png" alt="Report" width="75%">
</div>
<div style="text-align: center;">
    <button onclick="toggleCompareReportImage()">[See alternative report format]</button>
</div>

<script>
function toggleCompareReportImage() {
    var img = document.getElementById('compareReportImage');
    if (img.src.includes('compare.png')) {
        img.src = '../media/compare2.png';
    } else {
        img.src = '../media/compare.png';
    }
}
</script>

## Summary Report 📊

You can also generate an overview summary of all testcases results by running:

```bash
simpleval reports summarize -e <eval_dir> -p <metric name>
```


It supports two formats: `html` and `py` (deprecated).
The `-p` or `--primary-metric` is the main metric (will be shown first).

<br>
<br>
<div style="text-align: center;">
    <img id="summaryReportImage" src="../media/summary2.png" alt="Summary Report" width="75%">
</div>
<div style="text-align: center;">
    <button onclick="toggleSummaryReportImage()">[See alternative report format]</button>
</div>

<script>
function toggleSummaryReportImage() {
    var img = document.getElementById('summaryReportImage');
    if (img.src.includes('summary.png')) {
        img.src = '../media/summary2.png';
    } else {
        img.src = '../media/summary.png';
    }
}
</script>

<br>
