from litellm import LlmProviders

from simpleval.commands.litellm_models_explorer_command import get_supported_model_ids_by_provider
from simpleval.evaluation.judges.judge_utils import verify_env_var
from simpleval.evaluation.judges.models.litellm_structured_output.judge import LiteLLMJudge

GEMINI_JUDGE_DEFAULT_MODEL = 'gemini/gemini-2.0-flash'


class GeminiJudge(LiteLLMJudge):
    """
    Gemini judge with structured output support using LiteLLM.
    """

    def __init__(self, model_id: str = None):
        model_id = model_id or GEMINI_JUDGE_DEFAULT_MODEL
        supported_models = get_supported_model_ids_by_provider(provider_name='gemini')
        super().__init__(model_id=model_id, provider_id=LlmProviders.GEMINI, supported_model_ids=supported_models)

        self.logger.info('Gemini judge initialized')

    def run_preliminary_checks(self):
        """
        Run any preliminary checks before the evaluation starts.
        """
        super().run_preliminary_checks()
        verify_env_var('GEMINI_API_KEY')

    def preliminary_checks_explanation(self):
        return 'The Gemini judge requires the following environment variable to be set:\n- GEMINI_API_KEY: Your Gemini API key.\n'
