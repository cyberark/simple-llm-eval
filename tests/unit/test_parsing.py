import pytest
import tenacity
from pydantic import ValidationError

from simpleval.evaluation.metrics.parsers.output_parsing import parse_explanation_answer_output, parse_json_output
from simpleval.evaluation.metrics.parsers.parsed_output_schema import JudgeParsedOutput
from simpleval.evaluation.metrics.parsers.xml_output_parsing import get_xml_end_tag, get_xml_tag, parse_xml_response, \
    replace_all_tags_for_escape, revert_all_tags_after_escape


def test_xml_parsing_with_trailing_chars():
    xml_to_parse = """<response>
<reasonings>
a
</reasonings>
<answer>Not generally</answer>
</response>
```
"""

    parsed_output: JudgeParsedOutput = parse_xml_response(xml_to_parse)
    assert parsed_output.answer == 'Not generally'
    assert len(parsed_output.reasonings) > 0


def test_xml_parsing_with_leading_chars():
    xml_to_parse = """```<response>
<reasonings>
a
</reasonings>
<answer>Not generally</answer>
</response>
```
"""

    parsed_output: JudgeParsedOutput = parse_xml_response(xml_to_parse)
    assert parsed_output.answer == 'Not generally'
    assert len(parsed_output.reasonings) > 0


def test_xml_parsing_with_leading_and_trailing_chars():
    xml_to_parse = """```<response>
<reasonings>
a
</reasonings>
<answer>Not generally</answer>
</response>```
```
"""

    parsed_output: JudgeParsedOutput = parse_xml_response(xml_to_parse)
    assert parsed_output.answer == 'Not generally'
    assert len(parsed_output.reasonings) > 0


def test_explanation_answer_parsing_with_extra_leading_chars():
    explanation_answer_to_parse = """```Explanation: The reference response states "The user clicked on the enter key".
Answer: The user clicked some buttons.
    """

    parsed_output: JudgeParsedOutput = parse_explanation_answer_output(explanation_answer_to_parse)
    assert parsed_output.reasonings == "The reference response states \"The user clicked on the enter key\"."
    assert parsed_output.answer == 'The user clicked some buttons.'


def test_explanation_answer_missing_expl_parsing():
    explanation_answer_to_parse = """```The reference response states "The user clicked on the enter key".
Answer: The user clicked some buttons.
    """

    with pytest.raises(ValueError) as ex:
        parse_explanation_answer_output(explanation_answer_to_parse)


def test_explanation_answer_missing_ans_parsing():
    explanation_answer_to_parse = """```Explanation: The reference response states "The user clicked on the enter key".
The user clicked some buttons.
    """

    with pytest.raises(ValueError) as ex:
        parse_explanation_answer_output(explanation_answer_to_parse)


def test_explanation_answer_missing_prefixes_parsing():
    explanation_answer_to_parse = """```The reference response states "The user clicked on the enter key".
The user clicked some buttons.
    """

    with pytest.raises(ValueError) as ex:
        parse_explanation_answer_output(explanation_answer_to_parse)


def test_json_parsing():
    json_to_parse = """{
        "reasoning": "The user clicked on the enter key.",
        "answer": "The user clicked some buttons."
    }"""

    parsed_output: JudgeParsedOutput = parse_json_output(json_to_parse)
    assert parsed_output.reasonings == 'The user clicked on the enter key.'
    assert parsed_output.answer == 'The user clicked some buttons.'


def test_json_parsing_with_trailing_chars():
    json_to_parse = """{
        "reasoning": "The user clicked on the enter key.",
        "answer": "The user clicked some buttons."
    }```
    """

    parsed_output: JudgeParsedOutput = parse_json_output(json_to_parse)
    assert parsed_output.reasonings == 'The user clicked on the enter key.'
    assert parsed_output.answer == 'The user clicked some buttons.'


def test_json_parsing_with_leading_chars():
    json_to_parse = """```{
        "reasoning": "The user clicked on the enter key.",
        "answer": "The user clicked some buttons."
    }
    """

    parsed_output: JudgeParsedOutput = parse_json_output(json_to_parse)
    assert parsed_output.reasonings == 'The user clicked on the enter key.'
    assert parsed_output.answer == 'The user clicked some buttons.'


def test_json_parsing_with_leading_and_trailing_chars():
    json_to_parse = """```{
        "reasoning": "The user clicked on the enter key.",
        "answer": "The user clicked some buttons."
    }```
    """

    parsed_output: JudgeParsedOutput = parse_json_output(json_to_parse)
    assert parsed_output.reasonings == 'The user clicked on the enter key.'
    assert parsed_output.answer == 'The user clicked some buttons.'


def test_json_parsing_missing_reasoning():
    json_to_parse = """{
        "answer": "The user clicked some buttons."
    }
    """

    with pytest.raises(ValidationError) as ex:
        parse_json_output(json_to_parse)


def test_json_parsing_missing_answer():
    json_to_parse = """{
        "reasoning": "The user clicked on the enter key."
    }
    """

    with pytest.raises(ValidationError) as ex:
        parse_json_output(json_to_parse)


@pytest.mark.parametrize('invalid_chars', ['<<', '<', '>>', '>', '&', '"', "'"])
def test_xml_parsing_with_invalid_xml_chars(invalid_chars):
    xml_to_parse = f"""<response>
<reasonings>
a{invalid_chars}
</reasonings>
<answer>Not generally</answer>
</response>
```
"""

    parsed_output: JudgeParsedOutput = parse_xml_response(xml_to_parse)
    assert parsed_output.answer == 'Not generally'
    assert len(parsed_output.reasonings) > 0


def test_get_xml_tag():
    assert get_xml_tag('test') == '<test>'


def test_get_xml_end_tag():
    assert get_xml_end_tag('test') == '</test>'


def test_replace_all_tags_for_escape():
    xml_string = '<response><reasonings>a</reasonings><answer>Not generally</answer></response>'
    expected_output = 'RESPONSE_ELEMENT_TEMP_REPLACEMENTREASONINGS_ELEMENT_TEMP_REPLACEMENTaREASONINGS_END_ELEMENT_TEMP_REPLACEMENTANSWER_ELEMENT_TEMP_REPLACEMENTNot generallyANSWER_END_ELEMENT_TEMP_REPLACEMENTRESPONSE_END_ELEMENT_TEMP_REPLACEMENT'
    assert replace_all_tags_for_escape(xml_string) == expected_output


def test_revert_all_tags_after_escape():
    xml_string = 'RESPONSE_ELEMENT_TEMP_REPLACEMENTREASONINGS_ELEMENT_TEMP_REPLACEMENTaREASONINGS_END_ELEMENT_TEMP_REPLACEMENTANSWER_ELEMENT_TEMP_REPLACEMENTNot generallyANSWER_END_ELEMENT_TEMP_REPLACEMENTRESPONSE_END_ELEMENT_TEMP_REPLACEMENT'
    expected_output = '<response><reasonings>a</reasonings><answer>Not generally</answer></response>'
    assert revert_all_tags_after_escape(xml_string) == expected_output
