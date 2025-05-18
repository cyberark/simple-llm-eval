import logging
from typing import List

from colorama import Fore
from jinja2 import Template

from simpleval.commands.reporting.eval.html_common import save_html_report
from simpleval.consts import EVAL_ERROR_FILE_NAME, LLM_TASKS_ERROR_FILE_NAME, LOGGER_NAME
from simpleval.evaluation.schemas.eval_result_schema import EvalTestResult

REPORT_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    <style>
        body {
            font-family: 'Arial', sans-serif;
            margin: 0;
            padding: 0;
            line-height: 1.6;
            background-color: #f9f9f9;
            color: #333;
        }

        h1, h2 {
            text-align: center;
            color: #444;
        }

        table {
            width: 90%;
            margin: 20px auto;
            border-collapse: collapse;
            background-color: #fff;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
        }

        th, td {
            border: 1px solid #ddd;
            padding: 12px 15px;
            text-align: left;
        }

        th {
            background-color: #0078d7;
            color: white;
            font-weight: bold;
            position: sticky;
            top: 0;
            z-index: 1;
        }

        tr:nth-child(even) {
            background-color: #f2f2f2;
        }

        tr:hover {
            background-color: #f1f1f1;
        }

        .red {
            background-color: #ffccd5 !important; /* Soft reddish-pink */
            color: #a4001d;
        }

        .yellow {
            background-color: #fff6d2 !important; /* Soft pastel yellow */
            color: #a18a00;
        }

        .green {
            background-color: #d2f7e0 !important; /* Soft pastel green */
            color: #005c42;
        }

        ul {
            width: 50%;
            margin: 20px auto;
            padding: 0;
            list-style-type: none;
        }

        ul li {
            background: #0078d7;
            color: white;
            margin: 5px 0;
            padding: 10px 15px;
            border-radius: 4px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }

        p {
            width: 80%;
            margin: 10px auto;
            text-align: center;
            background: none; /* Remove blue background */
            color: #333; /* Change text color to default */
            padding: 10px;
            border-radius: 4px;
            font-size: 18px;
        }

        th:first-child, td:first-child {
            width: 0%;
        }

        th:nth-child(2), td:nth-child(2) {
            width: 10%;
        }

        th:nth-child(3), td:nth-child(3) {
            width: 10%;
        }

        th:nth-child(4), td:nth-child(4) {
            width: 10%;
        }

        th:nth-child(5), td:nth-child(5) {
            width: 10%;
        }

        th:nth-child(6), td:nth-child(6) {
            width: 10%;
        }

        th:nth-child(7), td:nth-child(7) {
            width: 8%;
        }

        th:nth-child(8), td:nth-child(8) {
            width: 15%;
        }

        @media (max-width: 768px) {
            table, th, td {
                font-size: 14px;
            }

            ul li, p {
                font-size: 16px;
            }
        }

        .explanation {
            display: none;
            margin-top: 10px;
            padding: 10px;
            background-color: #f1f1f1;
            border: 1px solid #ddd;
            border-radius: 4px;
        }

        .tooltip {
            position: relative;
            display: inline-block;
            cursor: pointer;
            color: #0078d7;
            text-decoration: underline;
        }

        .tooltip .tooltiptext {
            visibility: hidden;
            width: 150px;
            background-color: #f9f9f9;
            color: #333;
            text-align: center; /* Align text to the left */
            border-radius: 6px;
            padding: 5px;
            border: 1px solid #ddd;
            position: absolute;
            z-index: 1;
            bottom: 125%; /* Position the tooltip above the text */
            left: 50%;
            # margin-left: -100px;
            opacity: 0;
            transition: opacity 0.3s;
            font-size: 14px;
        }

        .tooltip:hover .tooltiptext {
            visibility: visible;
            opacity: 1;
        }

        .popup {
            display: none;
            position: fixed;
            z-index: 1;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            overflow: auto;
            background-color: rgba(0, 0, 0, 0.4);
        }

        .popup-content {
            background-color: #fefefe;
            margin: 15% auto;
            padding: 20px;
            border: 1px solid #888;
            width: 120%; /* Increased width */
            max-width: 1000px; /* Increased max-width */
            border-radius: 10px;
        }

        .popup-content p {
            white-space: pre-wrap; /* Respect new lines */
            text-align: left; /* Align text to the left */
        }

        .close {
            color: #aaa;
            float: right;
            font-size: 28px;
            font-weight: bold;
        }

        .close:hover,
        .close:focus {
            color: black;
            text-decoration: none;
            cursor: pointer;
        }
        .warning {
            background-color: #fff3cd;  /* light yellowish background */
            color: #856404;            /* darker golden text */
            border: 1px solid #ffeeba;
            padding: 15px;
            border-radius: 5px;
            margin: 20px auto;
            width: 80%;
            text-align: left;
            font-size: 18px;
        }
    </style>
    <script>
        function toggleExplanation(id) {
            var element = document.getElementById(id);
            if (element.style.display === "none") {
                element.style.display = "block";
            } else {
                element.style.display = "none";
            }
        }

        function showPopup(id) {
            var popup = document.getElementById(id);
            popup.style.display = "block";
        }

        function closePopup(id) {
            var popup = document.getElementById(id);
            popup.style.display = "none";
        }
    </script>
</head>
<body>
    <h1>Evaluation Report: {{ title }}</h1>
    <h2>Testcase: {{ testcase }}</h2>
    <h2>Scores</h2>
    <ul style="width: 25%;">
        {% for metric, mean in metric_means.items() %}
            <li>{{ metric }}: {{ mean.mean }} (std dev: {{ mean.std_dev }})</li>
        {% endfor %}
        <li>aggregate mean: {{ aggregate_mean }}</li>
    </ul>
    <h2>Detailed Results</h2>
    <p class="{{ error_style }}">{{ error_message }}</p>
    <table>
        <thead>
            <tr>
                <th>#</th>
                <th>Test Name</th>
                <th>Prompt To LLM</th>
                <th>LLM Response</th>
                <th>Expected LLM Response</th>
                <th>Eval Result</th>
                <th>Normalized Score</th>
            </tr>
        </thead>
        <tbody>
            {% for idx, eval_result in enumerate(eval_results, 1) %}
                <tr class="{% if eval_result.normalized_score < red_threshold %}red{% elif eval_result.normalized_score < yellow_threshold %}yellow{% else %}green{% endif %}">
                    <td>{{ idx }}</td>
                    <td>{{ eval_result.name_metric }}</td>
                    <td>
                        <div class="tooltip" onclick="showPopup('prompt-popup-{{ idx }}')">show
                            <span class="tooltiptext">{{ 'show prompt' }}</span>
                        </div>
                        <div id="prompt-popup-{{ idx }}" class="popup">
                            <div class="popup-content">
                                <span class="close" onclick="closePopup('prompt-popup-{{ idx }}')">&times;</span>
                                <p><strong><u>Prompt To LLM:</u></strong><br>{{ eval_result.llm_run_result.prompt }}</p>
                            </div>
                        </div>
                    </td>
                    <td>{{ eval_result.llm_run_result.prediction }}</td>
                    <td>{{ eval_result.llm_run_result.expected_prediction }}</td>
                    <td>{{ eval_result.result }}</td>
                    <td>
                        <div class="tooltip" onclick="showPopup('popup-{{ idx }}')">{{ eval_result.normalized_score }}
                            <span class="tooltiptext">{{ 'show explanation' }}</span>
                        </div>
                        <div id="popup-{{ idx }}" class="popup">
                            <div class="popup-content">
                                <span class="close" onclick="closePopup('popup-{{ idx }}')">&times;</span>
                                <p><strong><u>Eval result explanation:</u></strong><br>{{ eval_result.explanation }}</p>
                            </div>
                        </div>
                    </td>
                </tr>
            {% endfor %}
        </tbody>
    </table>
</body>
</html>
"""


def _generate_html_report(name: str, testcase: str, eval_results: List[EvalTestResult], metric_means: dict, aggregate_mean: float,
                          llm_task_errors_count: int, eval_errors_count: int, yellow_threshold: float, red_threshold: float) -> str:
    logger = logging.getLogger(LOGGER_NAME)

    logger.warning(f'{Fore.YELLOW}NOTICE: `html` format is obsolete, use `html2` instead')

    template = Template(REPORT_TEMPLATE, autoescape=True)
    template.globals['enumerate'] = enumerate  # Add this line to import enumerate

    if llm_task_errors_count == 0 and eval_errors_count == 0:
        error_style = ''
        error_message = ''
    else:
        error_style = 'warning'
        error_message = f'LLM tasks errors: {llm_task_errors_count}, Eval errors: {eval_errors_count}.  Run again to retry only errors or see {testcase}/{EVAL_ERROR_FILE_NAME}, {LLM_TASKS_ERROR_FILE_NAME}'  # pylint:disable=line-too-long

    metric_means_values = {metric: {'mean': scores.mean, 'std_dev': scores.std_dev} for metric, scores in metric_means.items()}

    html_content = template.render(title=name, testcase=testcase, eval_results=eval_results, red_threshold=red_threshold,
                                   yellow_threshold=yellow_threshold, metric_means=metric_means_values, aggregate_mean=aggregate_mean,
                                   error_style=error_style, error_message=error_message)

    return save_html_report(name=name, testcase=testcase, html_content=html_content)
