import logging
import os

from colorama import Fore

from simpleval.consts import LOGGER_NAME


def delete_file(file_path: str, log: bool = True):
    """
    Delete a file if it exists and log the deletion.

    Args:
        file_path (str): _description_
        log (bool, optional): Whether to log the deletion. Defaults to True.
    """
    if os.path.exists(file_path):
        os.remove(file_path)
        if log:
            logger = logging.getLogger(LOGGER_NAME)
            logger.debug(f'{Fore.YELLOW}`{file_path}` deleted{Fore.RESET}\n')
