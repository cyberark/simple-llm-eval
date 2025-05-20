import litellm
from litellm import LlmProviders

providers = litellm.provider_list
# print(f'{providers=}')

# models = litellm.models_by_provider.get(LlmProviders.VERTEX_AI, [])
# print(f'{models=}')

params = litellm.get_supported_openai_params(model='gemini-2.0-flash-001', custom_llm_provider=LlmProviders.VERTEX_AI)
print(f'{params=}')

# for provider in providers:
#     print(f'{provider=}')
#     models = litellm.models_by_provider.get(provider, [])
#     for model in models:
#         # print(f'{model=}')
#         litellm.get_supported_openai_params(model=model, custom_llm_provider=provider)

# provider=<LlmProviders.OLLAMA: 'ollama'>
# model='llama2'

# print(litellm.get_supported_openai_params(model='llama2', custom_llm_provider='ollama'))
