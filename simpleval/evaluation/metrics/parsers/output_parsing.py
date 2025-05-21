import json

from simpleval.evaluation.metrics.models.litellm_structured_output.base.base_metric import StructuredResponse
from simpleval.evaluation.metrics.parsers.parsed_output_schema import JudgeParsedOutput


def parse_explanation_answer_output(output_string: str) -> JudgeParsedOutput:
    """
    Parses the given output string and extracts the explanation and answer.

    Args:
        output_string (str): The output string to parse.

    Returns:
        dict: A dictionary with 'explanation' and 'answer' keys.
    """
    explanation_prefix = 'Explanation: '
    answer_prefix = 'Answer: '

    if explanation_prefix not in output_string or answer_prefix not in output_string:
        raise ValueError(f'Output string is missing required prefixes, {explanation_prefix=}, {answer_prefix=}, {output_string=}')

    explanation_start = output_string.find(explanation_prefix) + len(explanation_prefix)
    answer_start = output_string.find(answer_prefix)

    explanation = output_string[explanation_start:answer_start].strip().strip(',')
    answer = output_string[answer_start + len(answer_prefix) :].strip()

    return JudgeParsedOutput(reasonings=explanation, answer=answer)


def parse_json_output(output_string: str) -> JudgeParsedOutput:
    """
    Parses the given JSON string and extracts the reasoning and answer.

    Args:
        output_string (str): The JSON string to parse.

    Returns:
        dict: A dictionary with 'reasoning' and 'answer' keys.
    """
    start_index = output_string.find('{')
    end_index = output_string.rfind('}') + 1

    if start_index == -1 or end_index == -1:
        raise ValueError(f'Invalid JSON string: {output_string}')

    output_string = output_string[start_index:end_index]
    output_string = output_string.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')

    data = json.loads(output_string)
    reasoning = data.get('reasoning')
    answer = data.get('answer')
    return JudgeParsedOutput(reasonings=reasoning, answer=answer)


def litellm_structured_output_parser(output_string: str) -> JudgeParsedOutput:
    """
    Return the expected value assuming a LiteLLM response.

    See

    Args:
        output_string (str): The output string to parse.

    Returns:
        dict: A dictionary with 'reasoning' and 'answer' keys.
    """

    structured_response = StructuredResponse.model_validate_json(output_string)
    return JudgeParsedOutput(
        reasonings=structured_response.reasoning,
        answer=structured_response.answer,
    )
