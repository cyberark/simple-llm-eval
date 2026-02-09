"""
Shared evaluation prompts module.

This module contains the core evaluation rubrics for all metrics.
The prompts are shared between different metric implementations (bedrock_claude_sonnet, litellm_structured_output, etc.)
which add their own format-specific instructions.
"""


def get_json_schema_format_suffix(possible_responses: list[str]) -> str:
    """
    Generate the JSON schema format suffix for litellm_structured_output metrics.
    
    Args:
        possible_responses: List of possible response values for the enum
        
    Returns:
        JSON schema format suffix string
    """
    enum_values_str = ", ".join([f'`{resp}`' for resp in possible_responses])
    enum_json = str(possible_responses).replace("'", '"')
    
    # Build the JSON schema string with proper escaping for .format()
    # Each {{ in the string will become { after .format() is called
    return """
        The output should be a well-formatted JSON instance that conforms to the JSON schema below.

        As an example, for the schema {{"properties": {{"foo": {{"title": "Foo", "description": "a list of strings", "type": "array", "items": {{"type": "string"}}}}}}, "required": ["foo"]}}
        the object {{"foo": ["bar", "baz"]}} is a well-formatted instance of the schema. The object {{"properties": {{"foo": ["bar", "baz"]}}}} is not well-formatted.

        Here is the output JSON schema:
        ```
        {{"properties": {{"reasoning": {{"description": "step by step reasoning to derive the final answer", "title": "Reasoning", "type": "string"}}, "answer": {{"description": "answer should be one of """ + enum_values_str + """", "enum": """ + enum_json + """, "title": "Answer", "type": "string"}}}}, "required": ["reasoning", "answer"]}}
        ```

        Do not return any preamble or explanations, return only a pure JSON string surrounded by triple backticks (```).
        """
