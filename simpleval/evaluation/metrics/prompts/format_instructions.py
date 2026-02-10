"""
Shared format instructions for evaluation metrics.

This module provides JSON format instructions that can be used by both
bedrock_claude_sonnet and litellm_structured_output metrics.
"""

from typing import List


def get_json_format_instructions(answer_options: List[str]) -> str:
    """
    Generate JSON format instructions for a metric with the given answer options.

    Args:
        answer_options: List of valid answer options for the metric.

    Returns:
        A string containing JSON schema format instructions.

    Note:
        Uses double braces {{}} because the returned string will be passed to
        Python's .format() method, which treats {{ as a literal {.
    """
    # Build the enum array for the schema
    enum_str = ', '.join(f'"{opt}"' for opt in answer_options)

    # Build the description with backtick-quoted options
    description_options = ', '.join(f'`{opt}`' for opt in answer_options)

    # Build the JSON schema string (note: double braces become single after .format())
    json_schema = (
        '{{"properties": {{"reasoning": {{"description": "step by step reasoning to derive the final answer", '
        '"title": "Reasoning", "type": "string"}}, "answer": {{"description": "answer should be one of '
        + description_options
        + '", "enum": ['
        + enum_str
        + '], "title": "Answer", "type": "string"}}}}, "required": ["reasoning", "answer"]}}'
    )

    return """
					The output should be a well-formatted JSON instance that conforms to the JSON schema below.

					As an example, for the schema {{"properties": {{"foo": {{"title": "Foo", "description": "a list of strings", "type": "array", "items": {{"type": "string"}}}}}}, "required": ["foo"]}}
					the object {{"foo": ["bar", "baz"]}} is a well-formatted instance of the schema. The object {{"properties": {{"foo": ["bar", "baz"]}}}} is not well-formatted.

					Here is the output JSON schema:
					```
					""" + json_schema + """
					```

					Do not return any preamble or explanations, return only a pure JSON string surrounded by triple backticks (```).
"""
