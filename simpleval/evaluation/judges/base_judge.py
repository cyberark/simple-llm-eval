import importlib
import inspect
import logging
import os
from abc import ABC, abstractmethod
from typing import Dict, List, Set

from colorama import Fore
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_fixed

from simpleval.consts import LOGGER_NAME
from simpleval.evaluation.judges.judge_utils import get_metrics_dir
from simpleval.evaluation.metrics.base_metric import EvaluationMetric
from simpleval.evaluation.metrics.consts import METRIC_PACKAGE
from simpleval.evaluation.metrics.metric_result_schema import MetricResult
from simpleval.evaluation.metrics.normalizers import get_normalize_score
from simpleval.evaluation.metrics.parsers.common import RETRYABLE_PARSING_ERRORS
from simpleval.evaluation.metrics.parsers.parsed_output_schema import JudgeParsedOutput


class BaseJudge(ABC):
    def __init__(self, model_id: str, supported_model_ids: Set[str]):
        """
        Base class for all judges.

        Args:
            model_id (str): model_id to use for evaluation. You can pass any id you want, but make sure it is
                            supported by the judge implementation.
            metrics_model (str): The model of the models to use. See `evaluation/metrics/models` for available metric models.
            supported_model_ids (Set[str]): Officially supported model IDs. Pass None to ignore this check.
        """

        self.model_id: str = model_id
        self._supported_model_ids: Set[str] = supported_model_ids or set()
        self.__metrics: Dict[str, EvaluationMetric] = {}

        self.logger = logging.getLogger(LOGGER_NAME)

        self.logger.debug(f'Initializing {self.name} judge with model_id: {model_id}')

        if self._supported_model_ids and model_id not in self._supported_model_ids:
            self.logger.warning(
                f'{Fore.YELLOW}model_id: {model_id} is not officially supported for {self.name}, test it is working as expected{Fore.RESET}'
            )

        self.__load_metrics()

    @property
    @abstractmethod
    def _metrics_model(self) -> Set[str]:
        """
        The model that the metrics support.
        Metrics are in their core llm prompts and as such might fit certain models.
        The metric model is the name of the folder under `evaluation/metrics/models`.
        For example: 'bedrock_claude_sonnet' metrics will work with Claude implementations.
        """

    @abstractmethod
    def _model_inference(self, eval_prompt: str, metric: EvaluationMetric) -> str:
        """
        Placeholder for model inference logic.
        This should be implemented in the concrete judge class.
        """

    @abstractmethod
    def run_preliminary_checks(self):
        """
        Run any preliminary checks before the evaluation starts.
        For example, AWS Bedrock based judges should check if the STS credentials are valid.
        """

    @abstractmethod
    def preliminary_checks_explanation(self):
        """
        Provide an explanation of the preliminary checks that are run - displayed to the user.
        """

    @property
    def supported_model_ids(self) -> Set[str]:
        """
        The model IDs that are supported by the judge. Other might also for (e.g. Haiku models for Claude Sonnet but are not guaranteed).
        """
        return self._supported_model_ids

    @property
    def name(self) -> str:
        """
        Dynamically fetch the file name from the concrete class.
        This is the directory name of the judge class.
        """
        return os.path.basename(os.path.dirname(inspect.getfile(self.__class__)))

    def get_metric(self, metric_name: str) -> EvaluationMetric:
        if metric_name not in self.__metrics:
            raise ValueError(f"Metric '{metric_name}' not found for judge: {self.name}. Available metrics: {list(self.__metrics.keys())}")
        return self.__metrics[metric_name]

    @retry(retry=retry_if_exception_type(RETRYABLE_PARSING_ERRORS), stop=stop_after_attempt(5), wait=wait_fixed(1))
    def evaluate(self, metric_name: str, prompt: str, prediction: str, **kwargs) -> MetricResult:
        """
        Evaluate the model output based on the provided metric.

        :param metric_name: The name of the metric to use for evaluation - this must match an existing metric
        :param prompt: The input prompt given to the model.
        :param prediction: The model's output/prediction.
        :param kwargs: Additional arguments such as ground_truth or other data.
        :return: A dictionary containing the evaluation results.
        """

        metric = self.get_metric(metric_name)
        eval_prompt = metric.render_eval_prompt(prompt=prompt, prediction=prediction, **kwargs)
        self.logger.debug(f'Eval prompt: {eval_prompt}')

        model_response = self._model_inference(eval_prompt=eval_prompt, metric=metric)
        self.logger.debug(f'Model response: {model_response}')

        parsed_response: JudgeParsedOutput = metric.parser(model_response)
        self.logger.debug(f'Parsed response: {parsed_response}')

        score = get_normalize_score(value=parsed_response.answer, items=metric.possible_responses)
        self.logger.debug(f'Score: {score}')

        return MetricResult(result=parsed_response.answer, explanation=parsed_response.reasonings, normalized_score=score)

    def list_metrics(self) -> List[str]:
        """
        List all available evaluation metrics by scanning the judge metrics directory.
        :return: A list of metric module names.
        """
        metrics_dir = get_metrics_dir(self._metrics_model)
        metric_files = [f for f in os.listdir(metrics_dir) if f.endswith('.py') and f != '__init__.py']
        metric_modules = [os.path.splitext(f)[0] for f in metric_files]

        return metric_modules

    def get_metrics_dir(self) -> str:
        """
        Get the directory path for the metrics of this judge.
        :return: The path to the metrics directory.
        """
        return get_metrics_dir(self._metrics_model)

    def get_all_metrics(self) -> Dict[str, EvaluationMetric]:
        """
        Retrieve all available metrics as a dictionary where the key is the metric name and the value is the metric instance.

        :return: A dictionary of all metrics.
        """
        all_metrics = {}
        for metric_name in self.list_metrics():
            all_metrics[metric_name] = self.get_metric(metric_name)
        return all_metrics

    def __load_metrics(self):
        metric_names = self.list_metrics()
        for metric_name in metric_names:
            package = METRIC_PACKAGE.format(metric_model=self._metrics_model, metric_name=metric_name)
            module = importlib.import_module(package)
            metric_class = self.__get_metric_class(module)
            if metric_class:
                self.__metrics[metric_name] = metric_class()

    def __get_metric_class(self, module) -> EvaluationMetric:
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if inspect.isclass(attr) and issubclass(attr, EvaluationMetric) and not inspect.isabstract(attr):
                return attr
        return None
