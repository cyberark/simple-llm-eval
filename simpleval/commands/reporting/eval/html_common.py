import logging
import os
import webbrowser
from datetime import datetime

from simpleval.consts import LOGGER_NAME, RESULTS_FOLDER


def save_html_report(name: str, testcase: str, html_content: str) -> str:
    logger = logging.getLogger(LOGGER_NAME)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    folder = RESULTS_FOLDER
    file_name = f'results_{name}_{testcase}_report_{timestamp}.html'.replace(':', '_')
    file_path = os.path.join(folder, file_name)
    file_path.replace(':', '_')
    os.makedirs(folder, exist_ok=True)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    logger.info(f'Report saved to {file_path}')
    full_path = os.path.abspath(file_path)
    webbrowser.open(f'file://{full_path}')
    return file_path
