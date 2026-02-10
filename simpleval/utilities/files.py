import logging
from pathlib import Path

from colorama import Fore

from simpleval.consts import LOGGER_NAME


def delete_file(file_path: str, log: bool = True):
    """
    Delete a file if it exists and log the deletion.

    Args:
        file_path (str): _description_
        log (bool, optional): Whether to log the deletion. Defaults to True.
    """
    path = Path(file_path)
    if path.exists():
        path.unlink()
        if log:
            logger = logging.getLogger(LOGGER_NAME)
            logger.debug(f'{Fore.YELLOW}`{file_path}` deleted{Fore.RESET}\n')


def is_subpath(child_path: str, parent_path: str):
    child = Path(child_path).resolve()
    parent = Path(parent_path).resolve()

    if child == parent:
        return False

    try:
        child.relative_to(parent)
        return True
    except ValueError:
        return False
