import logging
import os
import traceback
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Callable

from tenacity import RetryError
from tqdm import tqdm

from simpleval.consts import LOGGER_NAME
from simpleval.parallel_runner.schemas import TaskParams, TaskResult


class BaseRunner(ABC):
    def __init__(self, max_concurrent_tasks):
        self.max_concurrent_tasks = max_concurrent_tasks
        self.logger = logging.getLogger(LOGGER_NAME)

    def run_tasks(self, tasks: Any, task_function: Callable, task_config: Any):
        if not all(isinstance(task, TaskParams) for task in tasks):
            raise ValueError(f'Tasks must by of type {type(TaskParams)}')

        max_name_len = max(len(task.task_name) for task in tasks)
        results, errors = [], []

        with tqdm(total=len(tasks), colour='green') as progress_bar:
            with ThreadPoolExecutor(max_workers=self.max_concurrent_tasks) as executor:
                futures = [executor.submit(task_function, task.payload, task_config) for task in tasks]
                results, errors = self.collect_results(futures, progress_bar, max_name_len)

        self.process_results(results, errors)
        return results, errors

    def collect_results(self, futures, progress_bar, max_name_len):
        task_results, errors = [], []

        for future in as_completed(futures):
            if future.exception():
                exception_details = str(future.exception())
                if isinstance(future.exception(), RetryError):
                    exception_details += f' | {future.exception().last_attempt.exception()}'

                if self.logger.isEnabledFor(logging.DEBUG) or os.environ.get('LOG_LEVEL') == 'DEBUG':
                    exception_details += (
                        '\n' + '\n'.join(traceback.TracebackException.from_exception(future.exception()).format()) + '\n' + '*' * 80 + '\n'
                    )
                errors.append(exception_details)
                progress_bar.update(1)
            else:
                self.__verify_result_type(future.result())
                task_results.append(future.result())
                progress_bar.update(1)
                progress_bar.set_description(f'Processing {future.result().task_name:<{max_name_len + 1}}')

        results = [task_result.result for task_result in task_results]
        return results, errors

    def __verify_result_type(self, result):
        if not isinstance(result, TaskResult):
            raise ValueError(f'PLUGIN ERROR: Results must by of type {TaskResult}')

    @abstractmethod
    def process_results(self, results, errors):
        pass
