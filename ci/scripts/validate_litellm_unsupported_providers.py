#!/usr/bin/env python3
"""
Validate that UNSUPPORTED_PROVIDERS in simpleval stays in sync with litellm's
internal _skip_get_model_info_providers set.

litellm maintains a local variable inside register_model() that lists providers
which trigger side effects (e.g. OAuth device-code flows) when get_model_info
is called. This script extracts that set via source inspection and verifies
our UNSUPPORTED_PROVIDERS is a superset of it.

Two layers, because source inspection alone is brittle:
  1. Source extraction of the set literal (fails loudly if litellm refactors).
  2. A behavioural probe that register_model() really does skip get_model_info
     for those providers. This cross-checks layer 1: if litellm keeps a
     same-shaped set literal but stops honouring it, layer 1 still matches
     while layer 2 catches the regression.

If litellm refactors and either layer breaks, this script fails loudly so
we can update it.
"""

import contextlib
import inspect
import logging
import re
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
    Extract the _skip_get_model_info_providers set from litellm's register_model
    function source code by finding LlmProviders.<NAME>.value references.
    """
    from litellm.types.utils import LlmProviders
    from litellm.utils import register_model

    source = inspect.getsource(register_model)

    # The optional `: <annotation>` group tolerates PEP 526 annotations on the
    # assignment (litellm 1.97.0 changed the bare assignment to `: Final`).
    # An annotation carries no meaning for what we check, so it must not fail the guard.
    block_match = re.search(
        r'_skip_get_model_info_providers\s*(?::\s*[^=]+?)?\s*=\s*\{([^}]+)\}',
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
                            f'but source inspection says it should be skipped.\n'
                            f'  litellm no longer honours its own _skip_get_model_info_providers set, so registering '
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
                f'  litellm _skip_get_model_info_providers: {sorted(litellm_skip)}\n'
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
