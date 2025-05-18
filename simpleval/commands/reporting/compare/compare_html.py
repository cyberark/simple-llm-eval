# pylint: disable=consider-using-join
import logging
import os
import webbrowser
from datetime import datetime

from bs4 import BeautifulSoup

from simpleval.commands.reporting.compare.common import CompareArgs, _generate_details_table2, _generate_summary_table, is_float
from simpleval.consts import LOGGER_NAME, RESULTS_FOLDER


def _compare_results_html(left_side: CompareArgs, right_side: CompareArgs):
    summary_headers, summary_table = _generate_summary_table(left_side, right_side)
    details_headers, details_table = _generate_details_table2(left_side, right_side)

    summary_html = _generate_html_summary_table(summary_headers, summary_table)
    summary_html = _apply_html_color_to_cols(summary_html, 1, 2)

    details_html = _generate_html_detailed_table(details_headers, details_table)
    index_of_score = details_headers.index('Score')
    details_html = _apply_html_color_to_rows(details_html, index_of_score)

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Comparison Report</title>
        <style>
            body {{
                font-family: 'Arial', sans-serif;
                margin: 0;
                padding: 0;
                line-height: 1.6;
                background-color: #f9f9f9;
                color: #333;
            }}
            h1, h2 {{
                text-align: center;
                color: #444;
            }}
            .summary {{
                text-align: left;
                margin: 20px;
                font-size: 1.2em;
                background-color: #e9ecef;
                padding: 10px;
                border-radius: 5px;
                box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
            }}
            .summary p {{
                margin: 5px 0;
                font-weight: bold;
            }}
            table {{
                width: 90%;
                margin: 20px auto;
                border-collapse: collapse;
                background-color: #fff;
                box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
            }}
            th, td {{
                border: 1px solid #ddd;
                padding: 12px 15px;
                text-align: left;
            }}
            th {{
                background-color: #0078d7;
                color: white;
                font-weight: bold;
                position: sticky;
                top: 0;
                z-index: 1;
            }}
            tr:nth-child(even) {{
                background-color: #f2f2f2;
            }}
            tr:hover {{
                background-color: #f1f1f1;
            }}
            .red {{
                background-color: #ffccd5 !important;
                color: #a4001d;
            }}
            .yellow {{
                background-color: #fff6d2 !important;
                color: #a18a00;
            }}
            .green {{
                background-color: #d2f7e0 !important;
                color: #005c42;
            }}
            .popup {{
                display: none;
                position: fixed;
                z-index: 1;
                left: 0;
                top: 0;
                width: 100%;
                height: 100%;
                overflow: auto;
                background-color: rgb(0,0,0);
                background-color: rgba(0,0,0,0.4);
            }}
            .popup-content {{
                background-color: #fefefe;
                margin: 15% auto;
                padding: 20px;
                border: 1px solid #888;
                width: 80%;
            }}
            .popup-content p {{
                white-space: pre-wrap;
            }}
            .close {{
                color: #aaa;
                float: right;
                font-size: 28px;
                font-weight: bold;
            }}
            .close:hover,
            .close:focus {{
                color: black;
                text-decoration: none;
                cursor: pointer;
            }}
        </style>
        <script>
            function showPopup(id, event) {{
                event.preventDefault();
                document.getElementById(id).style.display = 'block';
            }}
            function closePopup(id, event) {{
                event.preventDefault();
                document.getElementById(id).style.display = 'none';
            }}
        </script>
    </head>
    <body>
        <h1>Comparison Report</h1>
        <h2>Summary</h2>
        {summary_html}
        <h2>Details</h2>
        {details_html}
    </body>
    </html>
    """

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    folder = RESULTS_FOLDER
    file_name = f'comparison_report_{left_side.name}_vs_{right_side.name}_{timestamp}.html'.replace(':', '_')
    file_path = os.path.join(folder, file_name)
    os.makedirs(folder, exist_ok=True)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    logging.getLogger(LOGGER_NAME).info(f'Report saved to {file_path}')
    full_path = os.path.abspath(file_path)
    webbrowser.open(f'file://{full_path}')
    return file_path


def _generate_html_summary_table(headers, table):
    html = '<table><thead><tr>'
    for header in headers:
        html += f'<th>{header}</th>'
    html += '</tr></thead><tbody>'
    for row in table:
        html += '<tr>'
        for cell in row:
            html += f'<td>{cell}</td>'
        html += '</tr>'
    html += '</tbody></table>'
    return html


def _generate_html_detailed_table(headers, table):
    html = '''
    <table><thead><tr>
    '''
    for header in headers:
        html += f'<th>{header}</th>'
    html += '''
    </tr></thead><tbody>
    '''
    for row_idx, row in enumerate(table):
        html += '<tr>'
        for col_idx, cell in enumerate(row):
            if col_idx == 2 and cell:
                prompt = cell
                html += f'''
                <td>
                    <a href="#" onclick="showPopup('popup-prompt-{row_idx}', event)">show</a>
                    <div id="popup-prompt-{row_idx}" class="popup">
                        <div class="popup-content">
                            <span class="close" onclick="closePopup('popup-prompt-{row_idx}', event)">&times;</span>
                            <p style="color: #0078d7; font-weight: bold;">Prompt</p>
                            <p>{prompt}</p>
                        </div>
                    </div>
                </td>
                '''
            elif col_idx == 6 and isinstance(cell, dict):  # Eval Result
                eval_result = cell.get('eval_result', 'N/A')
                result_explanation = cell.get('result_explanation', 'N/A')
                html += f'''
                <td>
                    <a href="#" onclick="showPopup('popup-eval-{row_idx}', event)">show</a>
                    <div id="popup-eval-{row_idx}" class="popup">
                        <div class="popup-content">
                            <span class="close" onclick="closePopup('popup-eval-{row_idx}', event)">&times;</span>
                            <p style="color: #0078d7; font-weight: bold;">Eval result</p>
                            <p>{eval_result}</p>
                            <p style="color: #0078d7; font-weight: bold;">Explanation</p>
                            <p>{result_explanation}</p>
                        </div>
                    </div>
                </td>
                '''
            else:
                html += f'<td>{cell}</td>'
        html += '</tr>'
    html += '''
    </tbody></table>
    '''
    return html


def _apply_html_color_to_cols(html, col1_idx, col2_idx):
    soup = BeautifulSoup(html, 'html.parser')
    rows = soup.find_all('tr')[1:]  # Skip header row

    for row in rows:
        cells = row.find_all('td')
        if len(cells) > max(col1_idx, col2_idx):
            val1 = float(cells[col1_idx].text)
            val2 = float(cells[col2_idx].text)
            if val1 > val2:
                cells[col1_idx]['style'] = 'color: green; font-weight: bold;'
            elif val2 > val1:
                cells[col2_idx]['style'] = 'color: green; font-weight: bold;'

    return str(soup)


def _apply_html_color_to_rows(html, col_idx):
    soup = BeautifulSoup(html, 'html.parser')
    rows = soup.find_all('tr')[1:]  # Skip header row

    for idx in range(0, len(rows) - 1):
        cells1 = rows[idx].find_all('td')
        cells2 = rows[idx + 1].find_all('td')
        val1 = cells1[col_idx].text
        val2 = cells2[col_idx].text
        if is_float(val1) and is_float(val2):
            if val1 > val2:
                cells1[col_idx]['style'] = 'color: green; font-weight: bold;'
            elif val2 > val1:
                cells2[col_idx]['style'] = 'color: green; font-weight: bold;'

    return str(soup)
