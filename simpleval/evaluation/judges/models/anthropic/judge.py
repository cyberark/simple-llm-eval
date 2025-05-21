from litellm import LlmProviders

from simpleval.commands.litellm_models_explorer_command import get_supported_model_ids_by_provider
from simpleval.evaluation.judges.judge_utils import verify_env_var
from simpleval.evaluation.judges.models.litellm_structured_output.judge import LiteLLMJudge

ANTHROPIC_JUDGE_DEFAULT_MODEL = 'claude-3-5-haiku-latest'


class AnthropicJudge(LiteLLMJudge):
    """
    Anthropic judge with structured output support using LiteLLM.
    """

    def __init__(self, model_id: str = None):
        model_id = model_id or ANTHROPIC_JUDGE_DEFAULT_MODEL
        supported_models = get_supported_model_ids_by_provider(provider_name='anthropic')
        super().__init__(model_id=model_id, provider_id=LlmProviders.ANTHROPIC, supported_model_ids=supported_models)

        self.logger.info('Anthropic judge initialized')

    def run_preliminary_checks(self):
        """
        Run any preliminary checks before the evaluation starts.
        """
        super().run_preliminary_checks()
        verify_env_var('ANTHROPIC_API_KEY')

    def preliminary_checks_explanation(self):
        return 'The Anthropic judge requires the following environment variables to be set:\n- ANTHROPIC_API_KEY: Your Anthropic API key.'
