import logging
import os
import re
from logging.handlers import RotatingFileHandler

from simpleval.consts import BOOKKEEPING_LOG_FILE_NAME, BOOKKEEPING_LOGGER_NAME, LOGGER_NAME

DEFAULT_LOGLEVEL = logging.INFO
VERBOSE_LOGLEVEL = logging.DEBUG

LOGGER_INIT = False


class StripColorFormatter(logging.Formatter):
    COLOR_CODE_RE = re.compile(r'\x1b\[[0-9;]*m')

    def format(self, record):
        original = super().format(record)
        return self.COLOR_CODE_RE.sub('', original)


def add_debug_file_handler(logger, formatter=None):
    """Add a rotating debug file handler to the logger."""
    debug_log_path = os.path.join(os.getcwd(), 'logs', 'simpleval.log')
    debug_file_handler = RotatingFileHandler(debug_log_path, maxBytes=10 * 1024 * 1024, backupCount=1, encoding='utf-8')
    debug_file_handler.setLevel(logging.DEBUG)
    if formatter is None:
        formatter = StripColorFormatter('%(asctime)s [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    debug_file_handler.setFormatter(formatter)
    logger.addHandler(debug_file_handler)


def init_logger(console_loglevel: int = DEFAULT_LOGLEVEL):
    os.makedirs('logs', exist_ok=True)

    global LOGGER_INIT
    if LOGGER_INIT:
        return

    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(console_loglevel)
    console_handler = logging.StreamHandler()  # Logs to the console
    console_handler.setLevel(console_loglevel)
    console_formatter = logging.Formatter('%(message)s')
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # Use StripColorFormatter for file handler (includes log level)
    file_formatter = StripColorFormatter('%(asctime)s [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    add_debug_file_handler(logger, file_formatter)

    logger.debug(f'DEBUG: Settings verbose: True, LOGLEVEL: {logging.getLevelName(console_loglevel)}')

    init_bookkeeping_logger()

    LOGGER_INIT = True


def init_bookkeeping_logger():
    os.makedirs('logs', exist_ok=True)
    file_path = os.path.join(os.getcwd(), 'logs', BOOKKEEPING_LOG_FILE_NAME)

    if not os.path.exists(file_path):
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write('time,source,model,input_tokens,output_tokens\n')

    bk_logger = logging.getLogger(BOOKKEEPING_LOGGER_NAME)
    bk_logger.setLevel(logging.INFO)
    bk_file_handler = logging.FileHandler(file_path)
    bk_file_handler.setLevel(logging.INFO)
    bk_formatter = logging.Formatter(
        '%(asctime)s, %(levelname)s, %(source)s, %(model)s, %(input_tokens)s, %(output_tokens)s', datefmt='%Y-%m-%d %H:%M:%S'
    )
    bk_file_handler.setFormatter(bk_formatter)
    bk_logger.addHandler(bk_file_handler)


def log_bookkeeping_data(source: str, model_name: str, input_tokens: int, output_tokens: int):
    bk_logger = logging.getLogger(BOOKKEEPING_LOGGER_NAME)
    bk_logger.info(
        'msg',
        extra={
            'source': source.replace(',', ''),
            'model': model_name.replace(',', ''),
            'input_tokens': input_tokens,
            'output_tokens': output_tokens,
        },
    )


def debug_logging_enabled(logger=None) -> bool:
    logger = logger or logging.getLogger(LOGGER_NAME)
    return logger.isEnabledFor(logging.DEBUG)
