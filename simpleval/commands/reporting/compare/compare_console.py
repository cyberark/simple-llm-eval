import logging

from colorama import Fore

from simpleval.commands.reporting.compare.common import CompareArgs, _generate_details_table, _generate_summary_table
from simpleval.commands.reporting.utils import print_table
from simpleval.consts import LOGGER_NAME


def _compare_results_console(left_side: CompareArgs, right_side: CompareArgs):
    logger = logging.getLogger(LOGGER_NAME)

    logger.info('General scores:')
    headers, summary_table = _generate_summary_table(left_side, right_side)
    _apply_color_to_cols(summary_table, 1, 2)
    print_table(table=summary_table, headers=headers)

    logger.info('\n')
    logger.info('Detailed scores:')
    headers, details_table = _generate_details_table(left_side, right_side)
    _apply_console_color_to_rows(details_table, 2)
    print_table(table=details_table, headers=headers)


def _apply_color_to_cols(table, col1_idx, col2_idx):
    for row in table:
        val1 = row[col1_idx]
        val2 = row[col2_idx]
        row[col1_idx] = _console_color_score(val1, val2)
        row[col2_idx] = _console_color_score(val2, val1)


def _apply_console_color_to_rows(table, col_idx):
    for idx in range(0, len(table) - 1):
        val1 = table[idx][col_idx]
        val2 = table[idx + 1][col_idx]

        if isinstance(val1, float) and isinstance(val2, float):
            table[idx][col_idx] = _console_color_score(val1, val2)
            table[idx + 1][col_idx] = _console_color_score(val2, val1)


def _console_color_score(score1, score2):
    if score1 > score2:
        return f'{Fore.GREEN}{score1}{Fore.RESET}'
    return score1
