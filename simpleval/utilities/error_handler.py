import logging
import sys
import traceback
from functools import wraps

from colorama import Fore

from simpleval.consts import LOGGER_NAME
from simpleval.exceptions import NoWorkToDo, TerminationError
from simpleval.logger import debug_logging_enabled


def handle_exceptions(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except NoWorkToDo:
            logging.getLogger(LOGGER_NAME).debug('No work to do')
            sys.exit(3)
        except TerminationError as ex:
            logging.getLogger(LOGGER_NAME).error(f'{Fore.RED}{str(ex)}{Fore.RESET}')
            if debug_logging_enabled():
                log_exception_traceback(ex)
            sys.exit(2)
        except Exception as ex:
            logging.getLogger(LOGGER_NAME).error(f'{Fore.RED}An unexpected error occurred: {ex}{Fore.RESET}')
            if debug_logging_enabled():
                log_exception_traceback(ex)
            sys.exit(1)

    return wrapper


def log_exception_traceback(ex: Exception):
    logging.getLogger(LOGGER_NAME).error('\n'.join(traceback.TracebackException.from_exception(ex).format()))
