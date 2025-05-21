from litellm import LlmProviders

from simpleval.commands.litellm_models_explorer_command import get_supported_model_ids_by_provider
from simpleval.evaluation.judges.judge_utils import verify_env_var
from simpleval.evaluation.judges.models.litellm_structured_output.judge import LiteLLMJudge

VERTEX_AI_JUDGE_DEFAULT_MODEL = 'gemini-2.0-flash'
VERTEX_AI_PROVIDER_NAME_PREFIX = 'vertex_ai'


class VertexAIJudge(LiteLLMJudge):
    """
    Vertex AI judge with structured output support using LiteLLM.
    """

    def __init__(self, model_id: str = None):
        model_id = model_id or VERTEX_AI_JUDGE_DEFAULT_MODEL
        if not model_id.startswith(VERTEX_AI_PROVIDER_NAME_PREFIX):
            model_id = f'{VERTEX_AI_PROVIDER_NAME_PREFIX}/{model_id}'

        supported_models = get_supported_model_ids_by_provider(provider_name=LlmProviders.VERTEX_AI)
        supported_models = [
            model_id if model_id.startswith(VERTEX_AI_PROVIDER_NAME_PREFIX) else f'{VERTEX_AI_PROVIDER_NAME_PREFIX}/{model_id}'
            for model_id in supported_models
        ]

        super().__init__(model_id=model_id, provider_id=LlmProviders.VERTEX_AI, supported_model_ids=supported_models)

        self.logger.info('Vertex AI judge initialized')

    def run_preliminary_checks(self):
        """
        Run any preliminary checks before the evaluation starts.
        """
        super().run_preliminary_checks()
        verify_env_var('GOOGLE_APPLICATION_CREDENTIALS')
        verify_env_var('VERTEXAI_LOCATION')
        verify_env_var('VERTEXAI_PROJECT')

    def preliminary_checks_explanation(self):
        return (
            'The Vertex AI judge requires the following environment variables to be set:\n'
            '- GOOGLE_APPLICATION_CREDENTIALS: Path to your Google Cloud service account key file.\n'
            '- VERTEXAI_LOCATION: The location of your Vertex AI resources.\n'
            '- VERTEXAI_PROJECT: Your Google Cloud project ID.\n'
        )
