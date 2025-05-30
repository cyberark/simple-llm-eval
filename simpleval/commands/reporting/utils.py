import logging

from tabulate import tabulate

from simpleval.consts import LOGGER_NAME


def print_table(table, headers):
    try:
        print(tabulate(table, headers=headers, tablefmt='heavy_grid'))
    except UnicodeError as e:
        logging.getLogger(LOGGER_NAME).debug(f'Error printing table: {e}. Using plain text format instead.')
        print(tabulate(table, headers=headers))
