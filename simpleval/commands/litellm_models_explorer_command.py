import logging
from typing import Dict

import litellm
from colorama import Fore
from InquirerPy import prompt

from simpleval.consts import LOGGER_NAME

UNSUPPORTED_PROVIDERS = []


def get_model_info(model: str, provider: str) -> Dict:
    """
    Get model information from litellm.
    """
    logger = logging.getLogger(LOGGER_NAME)
    try:
        model_info = litellm.get_model_info(model=model, custom_llm_provider=provider)
        return model_info
    except Exception as e:
        logger.debug(f'Error getting model info for {model}: {e}')
        return {}


def get_supported_models(provider_name: str) -> list:
    """
    Get supported models for a specific provider.

    Args:
        provider_name: The name of the provider.

    Returns:
        List of models that support response_format or json_schema.
    """
    logger = logging.getLogger(LOGGER_NAME)
    filtered_models = []
    models = litellm.models_by_provider.get(provider_name, [])

    for model in models:
        logger.debug(f'Checking model: {model} for provider: {provider_name}')

        model_info = get_model_info(model=model, provider=provider_name)
        mode = model_info.get('mode')
        if mode != 'chat':
            logger.debug(f'Model {model} is not in chat or completion mode. Skipping.')
            continue

        model_params = litellm.get_supported_openai_params(model=model, custom_llm_provider=provider_name)
        supports_response_format = model_params and 'response_format' in model_params
        supports_json_schema = litellm.supports_response_schema(model)

        logger.debug(f'Model: {model}, supports_response_format: {supports_response_format}, supports_json_schema: {supports_json_schema}')

        if supports_response_format or supports_json_schema:
            filtered_models.append(
                {
                    'model': model,
                    'supports_response_format': supports_response_format,
                    'supports_json_schema': supports_json_schema,
                }
            )

    return filtered_models


def get_supported_model_ids_by_provider(provider_name: str) -> list:
    models = get_supported_models(provider_name)
    return [model.get('model') for model in models]


def supported_models_by_provider() -> Dict[str, str]:
    logger = logging.getLogger(LOGGER_NAME)

    supported_models = {}

    supported_providers = [provider for provider in litellm.provider_list if provider.value not in UNSUPPORTED_PROVIDERS]

    for provider in supported_providers:
        provider_name = provider.value
        logger.debug(f'Checking provider: {provider_name}')
        filtered_models = get_supported_models(provider_name)

        if filtered_models:
            supported_models[provider_name] = filtered_models

    return supported_models


def litellm_models_explorer_command():
    logger = logging.getLogger(LOGGER_NAME)
    logger.info(f'{Fore.GREEN}Find LiteLLM models by provider{Fore.RESET}')
    logger.info(f'{Fore.GREEN}Only models that support "response format" or "json schema" are supported {Fore.RESET}')
    logger.info(f'{Fore.GREEN}See https://docs.litellm.ai/docs/completion/json_mode for more details{Fore.RESET}')

    models_by_provider = supported_models_by_provider()

    # Prompt user to select a provider
    questions = [{'type': 'list', 'name': 'selected_provider', 'message': 'Select an LLM provider:', 'choices': models_by_provider.keys()}]

    answers = prompt(questions)
    selected_provider = answers['selected_provider']

    models = models_by_provider.get(selected_provider)
    logger.info(f"Models available for provider '{selected_provider}':")
    for model in models:
        logger.info(model.get('model'))


if __name__ == '__main__':
    # models = get_supported_model_ids_by_provider(provider_name='openai')
    # print(models)
    litellm_models_explorer_command()
