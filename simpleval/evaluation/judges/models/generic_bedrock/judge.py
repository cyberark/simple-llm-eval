from litellm import LlmProviders

from simpleval.commands.litellm_models_explorer_command import get_supported_model_ids_by_provider
from simpleval.evaluation.judges.judge_utils import bedrock_preliminary_checks
from simpleval.evaluation.judges.models.litellm_structured_output.judge import LiteLLMJudge

GENERIC_BEDROCK_JUDGE_DEFAULT_MODEL = 'amazon.nova-pro-v1:0'


class GenericBedrockJudge(LiteLLMJudge):
    """
    Generic Bedrock judge with structured output support using LiteLLM.
    Use for models other than Anthropic. For Anthropic, use the bedrock_claude_sonnet judge.
    """

    def __init__(self, model_id: str = None):
        model_id = model_id or GENERIC_BEDROCK_JUDGE_DEFAULT_MODEL
        supported_models = get_supported_model_ids_by_provider(provider_name='bedrock')
        super().__init__(model_id=model_id, provider_id=LlmProviders.BEDROCK, supported_model_ids=supported_models)

        self.logger.info('Generic Bedrock judge initialized')

    def run_preliminary_checks(self):
        """
        Run any preliminary checks before the evaluation starts.
        """
        bedrock_preliminary_checks()

    def preliminary_checks_explanation(self):
        return 'The Bedrock judge requires working AWS credentials\nfor example, with environment variables or in a ~/.aws/credentials file'
