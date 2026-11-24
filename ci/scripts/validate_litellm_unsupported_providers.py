#!/usr/bin/env python3
"""
Validate that UNSUPPORTED_PROVIDERS in simpleval stays in sync with litellm's
PROVIDERS_THAT_AUTHENTICATE_ON_PROVIDER_INFO set.

litellm keeps a set of providers that trigger side effects (e.g. OAuth device-code flows)
when get_model_info is called, and its model registration path (register_model) skips
get_model_info for them. This script reads that set and verifies our UNSUPPORTED_PROVIDERS
is a superset of it.

History of where litellm kept the set, for context when this breaks again:
  - up to 1.104: an inline set literal in register_model (_skip_get_model_info_providers)
  - 1.105 - 1.106: that local variable bound to the module-level constant
  - 1.108: the local variable is gone, the registration helpers check the constant directly

Two layers, because reading the set alone does not prove litellm still honours it:
  1. Read the set from litellm.utils (fails loudly if litellm renames or reshapes it).
  2. A behavioural probe that register_model() really does skip get_model_info
     for those providers. This is the real safety net: if litellm keeps the constant
     but stops honouring it, layer 1 still matches while layer 2 catches the regression.

If litellm refactors and either layer breaks, this script fails loudly so
we can update it.
"""

import contextlib
import inspect
import logging
import sys

# Provider used as the positive control in the behavioural probe: get_model_info is
# expected to be called for it. That call proves the probe's spy is wired to the symbol
# register_model actually uses -- without it, "was not called" could just mean we
# patched the wrong function.
#
# Two requirements, both asserted in verify_skip_behaviour because register_model itself
# checks neither (its skip test is a bare string-membership check on litellm_provider):
#   - NOT in litellm's skip set, or get_model_info would be skipped and prove nothing.
#   - A real LlmProviders value. Any unknown string reaches get_model_info today, but a
#     fake would silently become a false alarm if litellm ever validates litellm_provider
#     and rejects unknown ones before the get_model_info call.
CONTROL_PROVIDER = 'anthropic'

# Prefix for throwaway model keys the probe registers, so cleanup can find them.
PROBE_KEY_PREFIX = 'simpleval-litellm-guard-probe'


def extract_litellm_skip_providers() -> set[str]:
    """
    Read the set of providers litellm refuses to call get_model_info for, from the module-level
    PROVIDERS_THAT_AUTHENTICATE_ON_PROVIDER_INFO constant that its registration path checks.

    The constant is read from litellm.utils (the module that checks it), not from the module that
    defines it, so we get exactly the object the registration code sees.
    """
    import litellm.utils
    from litellm.types.utils import LlmProviders

    name = 'PROVIDERS_THAT_AUTHENTICATE_ON_PROVIDER_INFO'
    if not hasattr(litellm.utils, name):
        raise RuntimeError(f'litellm.utils.{name} no longer exists. litellm may have refactored — update this script.')

    value = getattr(litellm.utils, name)
    if not isinstance(value, (set, frozenset)) or not value or not all(isinstance(p, str) for p in value):
        raise RuntimeError(
            f'litellm.utils.{name} is {value!r}, expected a non-empty set of provider names. '
            f'litellm may have changed the format — update this script.'
        )

    unknown = sorted(set(value) - {provider.value for provider in LlmProviders})
    if unknown:
        raise RuntimeError(
            f'{name} contains providers that are not LlmProviders values: {unknown}. '
            f'litellm may have renamed them — update this script.'
        )
    return set(value)


@contextlib.contextmanager
def _spied_get_model_info():
    """
    Patch litellm.utils.get_model_info with a recording spy and yield the call log.

    register_model reaches get_model_info through the litellm.utils module global
    (via _get_builtin_model_info_for_registration), so patching the module attribute
    intercepts it.

    The spy raises instead of delegating. That keeps the probe safe by construction:
    even if a future litellm calls get_model_info for a provider it used to skip, the
    real implementation never runs, so the OAuth flow we are guarding against cannot
    fire -- we only record that the call was attempted. _get_builtin_model_info_for_registration
    swallows the exception and treats the model as unknown, which is a normal code path.
    """
    import litellm.utils

    calls: list[str] = []
    original = litellm.utils.get_model_info

    def spy(*args, **kwargs):
        calls.append(kwargs.get('model') or (args[0] if args else ''))
        raise KeyError('validate_litellm_unsupported_providers probe: get_model_info intentionally blocked')

    litellm.utils.get_model_info = spy
    try:
        yield calls
    finally:
        litellm.utils.get_model_info = original


def _register_probe_model(key: str, provider: str):
    """Register a throwaway model entry, tolerating litellm versions without persist_across_reloads."""
    import litellm.utils

    model_cost = {key: {'litellm_provider': provider, 'mode': 'chat', 'input_cost_per_token': 0.0, 'output_cost_per_token': 0.0}}

    # persist_across_reloads was added in litellm 1.97.0; pass it only where supported so
    # the probe does not leave the entry to be replayed on every future cost-map refresh.
    if 'persist_across_reloads' in inspect.signature(litellm.utils.register_model).parameters:
        litellm.utils.register_model(model_cost, persist_across_reloads=False)
    else:
        litellm.utils.register_model(model_cost)


def _cleanup_probe_models():
    """Drop the throwaway entries the probe added to litellm's global cost map."""
    import litellm

    # Containment, not startswith: probe keys take both the '<prefix>-<provider>' and
    # '<provider>/<prefix>' forms, and the latter does not start with the prefix.
    for key in [k for k in litellm.model_cost if PROBE_KEY_PREFIX in str(k)]:
        del litellm.model_cost[key]


def verify_skip_behaviour(skip_providers: set[str]) -> None:
    """
    Verify register_model actually skips get_model_info for each provider in skip_providers.

    Probes both arms of litellm's condition: the provider named in the litellm_provider
    field, and the provider used as a "<provider>/<model>" key prefix.
    """
    from litellm.types.utils import LlmProviders

    if CONTROL_PROVIDER in skip_providers:
        raise RuntimeError(
            f"Positive control provider {CONTROL_PROVIDER!r} is now in litellm's skip set, so it can no longer "
            f'prove the probe works. Pick a different CONTROL_PROVIDER that litellm does not skip.'
        )

    if CONTROL_PROVIDER not in {provider.value for provider in LlmProviders}:
        raise RuntimeError(
            f'Positive control provider {CONTROL_PROVIDER!r} is not a real litellm provider (not in LlmProviders).\n'
            f'  The control probe must use a provider litellm recognises, so it keeps proving the spy works even if '
            f'litellm starts validating litellm_provider and rejects unknown values before calling get_model_info.\n'
            f'  Either litellm renamed/removed this provider, or CONTROL_PROVIDER was edited to a bogus value.'
        )

    # litellm logs a warning for unknown models; the probe registers deliberately
    # unknown ones, so keep that expected noise out of the CI output.
    litellm_logger = logging.getLogger('LiteLLM')
    original_level = litellm_logger.level
    litellm_logger.setLevel(logging.ERROR)

    try:
        with _spied_get_model_info() as calls:
            for provider in sorted(skip_providers):
                for key in (f'{provider}/{PROBE_KEY_PREFIX}', f'{PROBE_KEY_PREFIX}-{provider}'):
                    del calls[:]
                    _register_probe_model(key, provider)
                    if calls:
                        raise RuntimeError(
                            f'litellm.register_model called get_model_info for provider {provider!r} (key {key!r}), '
                            f'but the litellm skip set says it should be skipped.\n'
                            f'  litellm no longer honours its own PROVIDERS_THAT_AUTHENTICATE_ON_PROVIDER_INFO set, so registering '
                            f'a model for this provider can trigger side effects (e.g. an OAuth device-code flow).\n'
                            f'  Investigate the change in litellm.utils.register_model before upgrading.'
                        )

            # Positive control: a non-skipped provider must still reach get_model_info.
            del calls[:]
            _register_probe_model(f'{PROBE_KEY_PREFIX}-control', CONTROL_PROVIDER)
            if not calls:
                raise RuntimeError(
                    f'Probe self-check failed: get_model_info was not called for the non-skipped control provider '
                    f'{CONTROL_PROVIDER!r}.\n'
                    f'  The spy is no longer observing the function register_model uses, so the "skipped" results '
                    f'above prove nothing. litellm likely changed how it resolves model info — update this script.'
                )
    finally:
        litellm_logger.setLevel(original_level)
        _cleanup_probe_models()


def main():
    try:
        litellm_skip = extract_litellm_skip_providers()
        verify_skip_behaviour(litellm_skip)

        from simpleval.commands.litellm_models_explorer_command import UNSUPPORTED_PROVIDERS

        our_set = set(UNSUPPORTED_PROVIDERS)
        missing = litellm_skip - our_set

        if missing:
            missing_str = ', '.join(sorted(missing))
            raise RuntimeError(
                f'UNSUPPORTED_PROVIDERS is missing providers that litellm marks as problematic: {missing_str}\n'
                f'  litellm PROVIDERS_THAT_AUTHENTICATE_ON_PROVIDER_INFO: {sorted(litellm_skip)}\n'
                f'  Our UNSUPPORTED_PROVIDERS:              {sorted(our_set)}\n'
                f'\n'
                f'  Update UNSUPPORTED_PROVIDERS in simpleval/commands/litellm_models_explorer_command.py '
                f'to include the missing providers.'
            )

        print(f'✅ UNSUPPORTED_PROVIDERS is in sync with litellm (providers: {sorted(our_set)})')
        print(f'✅ litellm.register_model verified to skip get_model_info for: {sorted(litellm_skip)}')
        sys.exit(0)

    except Exception as e:
        print(f'❌ {e}')
        sys.exit(1)


if __name__ == '__main__':
    main()
