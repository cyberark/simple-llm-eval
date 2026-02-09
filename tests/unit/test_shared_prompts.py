"""
Tests for shared evaluation prompts module.

Verifies that shared prompts are correctly imported and used by both metric implementations.
"""

from simpleval.evaluation.metrics.models.bedrock_claude_sonnet.coherence import CoherenceMetric as BedrockCoherenceMetric
from simpleval.evaluation.metrics.models.litellm_structured_output.coherence import CoherenceMetric as LiteLLMCoherenceMetric
from simpleval.evaluation.metrics.prompts.coherence import CORE_PROMPT, POSSIBLE_RESPONSES


def test_shared_prompts_import():
    """Test that shared prompts can be imported."""
    assert CORE_PROMPT is not None
    assert len(CORE_PROMPT) > 0
    assert POSSIBLE_RESPONSES is not None
    assert len(POSSIBLE_RESPONSES) > 0


def test_bedrock_metric_uses_shared_prompt():
    """Test that bedrock metric uses the shared core prompt."""
    metric = BedrockCoherenceMetric()
    
    # Verify it uses the shared prompt
    assert CORE_PROMPT in metric.eval_prompt
    
    # Verify it uses the shared possible responses
    assert metric.possible_responses == POSSIBLE_RESPONSES
    
    # Verify it adds format-specific suffix (XML)
    assert '<response>' in metric.eval_prompt
    assert '<reasonings>' in metric.eval_prompt or '<reasoning>' in metric.eval_prompt


def test_litellm_metric_uses_shared_prompt():
    """Test that litellm metric uses the shared core prompt."""
    metric = LiteLLMCoherenceMetric()
    
    # Verify it uses the shared prompt
    assert CORE_PROMPT in metric.eval_prompt
    
    # Verify it uses the shared possible responses
    assert metric.possible_responses == POSSIBLE_RESPONSES
    
    # Verify it adds format-specific suffix (JSON schema)
    assert 'JSON schema' in metric.eval_prompt
    assert '"enum"' in metric.eval_prompt


def test_shared_prompt_contains_required_elements():
    """Test that the shared prompt contains required elements."""
    assert '{prompt}' in CORE_PROMPT
    assert '{prediction}' in CORE_PROMPT
    assert 'logical cohesion' in CORE_PROMPT.lower() or 'coherence' in CORE_PROMPT.lower()
