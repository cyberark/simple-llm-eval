import json
from typing import Set

import boto3
from colorama import Fore

from simpleval.evaluation.judges.base_judge import BaseJudge
from simpleval.evaluation.judges.judge_utils import bedrock_preliminary_checks
from simpleval.evaluation.judges.models.bedrock_claude_sonnet.consts import (
    AWS_REGION_PLACEHOLDER,
    SONNET35_V1_MODEL_ID,
    SONNET35_V2_MODEL_ID,
    SONNET37_V1_MODEL_ID,
)
from simpleval.evaluation.metrics.base_metric import EvaluationMetric
from simpleval.evaluation.metrics.models.bedrock_claude_sonnet.base.base_metric import BaseBedrockSonnetMetric
from simpleval.logger import log_bookkeeping_data
from simpleval.utilities.retryables import BEDROCK_LIMITS_EXCEPTIONS, bedrock_limits_retry


class BedrockClaudeSonnetJudge(BaseJudge):
    """
    Concrete Judge class using Bedrock Claude Sonnet (or similar) models.
    retries call_claude_completion on retryable errors like rate limits.
    """

    DEFAULT_MODEL_ID = SONNET35_V1_MODEL_ID
    DEFAULT_REGION = 'us-east-1'

    SUPPORTED_MODEL_IDS = {
        SONNET35_V1_MODEL_ID,
        SONNET35_V2_MODEL_ID,
        SONNET37_V1_MODEL_ID,
    }

    # bedrock's default values (https://docs.aws.amazon.com/bedrock/latest/userguide/model-parameters-claude.html):
    # top_p: min=0, max=1, default=1
    # top_k: min=0, max=500, default=250
    # temperature: min=0, max=1, default=0.5
    # max_tokens_to_sample: min=0, max=4096, default=200
    # learn more here: https://docs.anthropic.com/en/api/complete
    TEMPERATURE = 0.0
    MAX_TOKENS_TO_SAMPLE = 500

    def __init__(self, model_id: str = None):
        model_id = model_id or self.DEFAULT_MODEL_ID
        region = boto3.session.Session().region_name or self.DEFAULT_REGION
        if AWS_REGION_PLACEHOLDER in model_id:
            model_id = model_id.replace(AWS_REGION_PLACEHOLDER, region)

        supported_model_ids = {model_id.replace(AWS_REGION_PLACEHOLDER, region) for model_id in self.SUPPORTED_MODEL_IDS}
        super().__init__(model_id=model_id, supported_model_ids=supported_model_ids)

    @property
    def _metrics_model(self) -> Set[str]:
        return 'bedrock_claude_sonnet'

    def run_preliminary_checks(self):
        """
        Run any preliminary checks before the evaluation starts.
        """
        bedrock_preliminary_checks()

    def preliminary_checks_explanation(self):
        return 'The Bedrock judge requires working AWS credentials\nfor example, with environment variables or in a ~/.aws/credentials file'

    def _model_inference(self, eval_prompt: str, metric: EvaluationMetric) -> str:
        """
        Calling the actual model inference logic for the evaluation.
        """
        if not isinstance(metric, BaseBedrockSonnetMetric):
            raise TypeError(f'metric {metric.name} must be an instance of BaseBedrockSonnetMetric')

        return self.call_claude_completion(eval_prompt=eval_prompt, prefill=metric.prefill)

    @bedrock_limits_retry
    def call_claude_completion(self, eval_prompt: str, prefill: str):
        try:
            body_dict = self.__get_claude_body_dict(sys_prompt=eval_prompt, prefill=prefill)
            body = json.dumps(body_dict)

            accept = 'application/json'
            content_type = 'application/json'

            self.logger.debug(f'Calling Claude completion, {self.model_id=}, {body=}')

            bedrock = boto3.client(service_name='bedrock-runtime')
            response = bedrock.invoke_model(body=body, modelId=self.model_id, accept=accept, contentType=content_type)

            result = json.loads(response.get('body').read())
            input_tokens = result.get('usage', {}).get('input_tokens', '')
            output_tokens = result.get('usage', {}).get('output_tokens', '')
            output_list = result.get('content', [])
            self.logger.debug(f'Claude completion response: {output_list}, {input_tokens=}, {output_tokens=}')

            log_bookkeeping_data(source='eval', model_name=self.model_id, input_tokens=input_tokens, output_tokens=output_tokens)

            if not output_list:
                raise ValueError('empty response from sonnet35')
            else:
                output = output_list[0].get('text', '')

                # Note that if you include the { as the prefill, it will not be included in the response so we add it ourselves
                # see cookbook: https://github.com/anthropics/anthropic-cookbook/blob/main/misc/how_to_enable_json_mode.ipynb
                output = prefill + output
                return output

        except BEDROCK_LIMITS_EXCEPTIONS as e:
            self.logger.error(f'{Fore.YELLOW}Call to Claude completion ended with a retryable error: {str(e)}{Fore.RESET}')
            raise

    def __get_claude_body_dict(self, sys_prompt: str, prefill: str) -> dict:
        user_prompt = 'You are a helpful agent tasked with evaluating LLM responses based on a specific metric. Your goal is to assess the quality of the response according to the provided evaluation criteria.'  # pylint: disable=line-too-long

        body_dict = {
            'anthropic_version': 'bedrock-2023-05-31',
            'system': sys_prompt,
            'max_tokens': self.MAX_TOKENS_TO_SAMPLE,
            'messages': [
                {
                    'role': 'user',
                    'content': [{'type': 'text', 'text': user_prompt}],
                },
                {
                    'role': 'assistant',
                    'content': [
                        {
                            'type': 'text',
                            # see https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/prefill-claudes-response
                            'text': f'[LLM As a judge] {prefill}'.strip(),
                        }
                    ],
                },
            ],
        }

        body_dict['temperature'] = self.TEMPERATURE
        # Using default values for top_k and top_p, stop_sequences, etc.

        return body_dict
