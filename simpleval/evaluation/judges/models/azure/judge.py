from litellm import LlmProviders

from simpleval.commands.litellm_models_explorer_command import get_supported_model_ids_by_provider
from simpleval.evaluation.judges.judge_utils import verify_env_var
from simpleval.evaluation.judges.models.litellm_structured_output.judge import LiteLLMJudge

AZURE_JUDGE_DEFAULT_MODEL = 'azure/gpt-4.1-mini'


class AzureJudge(LiteLLMJudge):
    """
    Azure judge with structured output support using LiteLLM.
    """

    def __init__(self, model_id: str = None):
        model_id = model_id or AZURE_JUDGE_DEFAULT_MODEL
        supported_models = get_supported_model_ids_by_provider(provider_name='azure')
        super().__init__(model_id=model_id, provider_id=LlmProviders.AZURE, supported_model_ids=supported_models)

        self.logger.info('Azure judge initialized')

    def run_preliminary_checks(self):
        """
        Run any preliminary checks before the evaluation starts.
        """
        super().run_preliminary_checks()
        verify_env_var('AZURE_OPENAI_API_KEY')
        verify_env_var('AZURE_API_BASE')
        verify_env_var('AZURE_API_VERSION')

    def preliminary_checks_explanation(self):
        return (
            'The Azure judge requires the following environment variables to be set:\n'
            '- AZURE_OPENAI_API_KEY: Your Azure OpenAI API key.\n'
            '- AZURE_API_BASE: The base URL for the Azure OpenAI API.\n'
            '- AZURE_API_VERSION: The version of the Azure OpenAI API.\n\n'
            'Example:\n'
            'AZURE_OPENAI_API_KEY=<your_api_key>\n'
            'AZURE_API_BASE=https://<your_resource_name>.openai.azure.com/\n'
            'AZURE_API_VERSION=2024-04-01-preview\n'
        )
