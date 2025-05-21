from typing import Set

import litellm
from colorama import Fore
from litellm import LlmProviders, ModelResponse

from simpleval.evaluation.judges.base_judge import BaseJudge
from simpleval.evaluation.judges.models.litellm_structured_output.consts import LITELLM_STRUCTURED_OUTPUT_DEFAULT_MODEL
from simpleval.evaluation.metrics.models.litellm_structured_output.base.base_metric import LiteLLMMetric
from simpleval.logger import debug_logging_enabled, log_bookkeeping_data
from simpleval.utilities.retryables import LITELLM_LIMITS_EXCEPTIONS, litellm_limits_retry


class LiteLLMJudge(BaseJudge):
    """
    LLM Lite based judge with structured output support.

    See lite llm documentation for more details:
    https://docs.litellm.ai/docs/completion/json_mode

    The list of supported models can be found here:
    https://github.com/BerriAI/litellm/blob/main/model_prices_and_context_window.json
    see "supports_response_schema": true
    """

    TEMPERATURE = 0.0

    def __init__(self, model_id: str = None, provider_id: str = None, supported_model_ids=None):
        model_id = model_id or LITELLM_STRUCTURED_OUTPUT_DEFAULT_MODEL
        self.provider_id = provider_id
        if model_id == LITELLM_STRUCTURED_OUTPUT_DEFAULT_MODEL:
            self.provider_id = LlmProviders.OPENAI

        super().__init__(model_id=model_id, supported_model_ids=supported_model_ids)

        if debug_logging_enabled():
            litellm.set_verbose = True

        self.model_params = litellm.get_supported_openai_params(model=model_id, custom_llm_provider=self.provider_id)

        # See litellm documentation: https://docs.litellm.ai/docs/completion/json_mode
        self.model_supports_response_format = 'response_format' in self.model_params
        self.model_supports_json_schema = litellm.supports_response_schema(self.model_id)

        self.logger.debug(f'LiteLLM judge initialized with model_id: {model_id}, model_params: {self.model_params}')
        self.logger.debug(f'Model params: {self.model_supports_response_format=}, {self.model_supports_json_schema=}')

        if not self.model_params:
            models_providers_info = (
                'Provider List: https://docs.litellm.ai/docs/providers and '
                'Models: https://github.com/BerriAI/litellm/blob/main/model_prices_and_context_window.json'
            )
            raise ValueError(f'Model ID {model_id} not supported by litellm. Please provide a valid model ID. See {models_providers_info}')

    @property
    def _metrics_model(self) -> Set[str]:
        return 'litellm_structured_output'

    def run_preliminary_checks(self):
        """
        Run any preliminary checks before the evaluation starts.
        """
        if not self.model_id:
            raise ValueError(f'Model ID is not set correctly. Please provide a valid model ID (Model ID: {self.model_id})')

        if not self.model_supports_response_format and not self.model_supports_json_schema:
            raise ValueError(
                f'Model ID {self.model_id} does not support structured output. Please provide a valid model ID. '
                'Model must support either "response_format" or "json_schema".'
                'See https://docs.litellm.ai/docs/completion/json_mode for more details.'
            )

    def preliminary_checks_explanation(self):
        return (
            'The LiteLLM judge requires that the model id provided supports structured output.\n'
            "The model must support either 'response_format' or 'json_schema'.\n"
            'See https://docs.litellm.ai/docs/completion/json_mode for more details.\n\n'
            'It also requires an authentication, depending on the provider\n'
            'See Lite LLM documentation for more details\n'
        )

    def _model_inference(self, eval_prompt: str, metric: LiteLLMMetric) -> str:
        """
        Calling the actual model inference logic for the evaluation using lite llm
        This should be implemented in the concrete judge class.
        """
        if not isinstance(metric, LiteLLMMetric):
            raise TypeError(f'metric {metric.name} must be an instance of LiteLLMMetric')

        return self.call_litellm_completion(eval_prompt=eval_prompt, metric=metric)

    @litellm_limits_retry
    def call_litellm_completion(self, eval_prompt: str, metric: LiteLLMMetric) -> str:
        if self.model_supports_json_schema and not self.model_supports_response_format:
            # Since we will only work with one model at a certain time, then we can set this globally
            litellm.enable_json_schema_validation = True
            self.logger.debug('LiteLLM judge initialized with json schema validation enabled')

        try:
            messages = [
                {
                    'role': 'user',
                    'content': eval_prompt,
                }
            ]

            self.logger.debug(f'Calling LiteLLM completion, {self.model_id=}, {messages=}')

            # https://docs.litellm.ai/docs/completion/json_mode
            model_response: ModelResponse = litellm.completion(
                temperature=self.TEMPERATURE,
                model=self.model_id,
                messages=messages,
                response_format=metric.output_model,
            )

            input_tokens = model_response.usage.prompt_tokens
            output_tokens = model_response.usage.completion_tokens

            self.logger.debug(f'LiteLLM completion response: {model_response}, {input_tokens=}, {output_tokens=}')

            log_bookkeeping_data(source='eval', model_name=self.model_id, input_tokens=input_tokens, output_tokens=output_tokens)

            output_model = metric.output_model.model_validate_json(model_response.choices[0].message.content)
            output = output_model.model_dump_json()
            self.logger.debug(f'LiteLLM completion response content: {output_model=}, {output=}')

            return output

        except LITELLM_LIMITS_EXCEPTIONS as e:
            self.logger.error(f'{Fore.YELLOW}Call to LiteLLM completion ended with a retryable error: {str(e)}{Fore.RESET}')
            raise
