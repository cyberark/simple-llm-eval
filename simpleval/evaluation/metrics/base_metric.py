import inspect
import os
from abc import ABC, abstractmethod
from typing import Callable, List


class EvaluationMetric(ABC):
    """
    Base class for all metrics.
    """

    @property
    def name(self) -> str:
        """
        Dynamically fetch the file name from the concrete class.
        :return: The metric name name as a string.
        """
        return os.path.splitext(os.path.basename(inspect.getfile(self.__class__)))[0]

    def render_eval_prompt(self, prompt: str, prediction: str, **kwargs) -> str:
        """
        Format the evaluation prompt with the given prompt, prediction, and additional arguments.

        :param prompt: The original prompt to test
        :param prediction: The model's prediction.
        :param kwargs: Additional arguments for formatting.
        :return: The formatted evaluation prompt.
        """
        return self.eval_prompt.format(prompt=prompt, prediction=prediction, **kwargs)

    @property
    @abstractmethod
    def eval_prompt(self) -> str:
        """
        The evaluation prompt that defines how the metric is assessed.
        """

    @property
    @abstractmethod
    def possible_responses(self) -> List[str]:
        """
        The possible responses that the metric can return.
        """

    @property
    @abstractmethod
    def parser(self) -> Callable:
        """
        The parser that converts the model's output into a structured format.
        """
