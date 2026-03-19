#!/usr/bin/env python3
"""
Validate that UNSUPPORTED_PROVIDERS in simpleval stays in sync with litellm's
internal _skip_get_model_info_providers set.

litellm maintains a local variable inside register_model() that lists providers
which trigger side effects (e.g. OAuth device-code flows) when get_model_info
is called. This script extracts that set via source inspection and verifies
our UNSUPPORTED_PROVIDERS is a superset of it.

If litellm refactors and the extraction breaks, this script fails loudly so
we can update it.
"""
import inspect
import re
import sys


def extract_litellm_skip_providers() -> set[str]:
    """
    Extract the _skip_get_model_info_providers set from litellm's register_model
    function source code by finding LlmProviders.<NAME>.value references.
    """
    from litellm.types.utils import LlmProviders
    from litellm.utils import register_model

    source = inspect.getsource(register_model)

    block_match = re.search(
        r'_skip_get_model_info_providers\s*=\s*\{([^}]+)\}',
        source,
        re.DOTALL,
    )
    if not block_match:
        raise RuntimeError(
            'Could not find _skip_get_model_info_providers in litellm.utils.register_model source. '
            'litellm may have refactored — update this script.'
        )

    block = block_match.group(1)
    enum_names = re.findall(r'LlmProviders\.(\w+)\.value', block)
    if not enum_names:
        raise RuntimeError(
            'Found _skip_get_model_info_providers block but could not parse any LlmProviders entries. '
            'litellm may have changed the format — update this script.'
        )

    providers = set()
    for name in enum_names:
        member = getattr(LlmProviders, name, None)
        if member is None:
            raise RuntimeError(
                f'LlmProviders.{name} referenced in _skip_get_model_info_providers does not exist. '
                f'litellm may have renamed it — update this script.'
            )
        providers.add(member.value)

    return providers


def main():
    try:
        litellm_skip = extract_litellm_skip_providers()

        from simpleval.commands.litellm_models_explorer_command import UNSUPPORTED_PROVIDERS

        our_set = set(UNSUPPORTED_PROVIDERS)
        missing = litellm_skip - our_set

        if missing:
            missing_str = ', '.join(sorted(missing))
            raise RuntimeError(
                f'UNSUPPORTED_PROVIDERS is missing providers that litellm marks as problematic: {missing_str}\n'
                f'  litellm _skip_get_model_info_providers: {sorted(litellm_skip)}\n'
                f'  Our UNSUPPORTED_PROVIDERS:              {sorted(our_set)}\n'
                f'\n'
                f'  Update UNSUPPORTED_PROVIDERS in simpleval/commands/litellm_models_explorer_command.py '
                f'to include the missing providers.'
            )

        print(f'✅ UNSUPPORTED_PROVIDERS is in sync with litellm (providers: {sorted(our_set)})')
        sys.exit(0)

    except Exception as e:
        print(f'❌ {e}')
        sys.exit(1)


if __name__ == '__main__':
    main()
