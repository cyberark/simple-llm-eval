import logging
import xml.etree.ElementTree as ET
import xml.sax.saxutils

from simpleval.consts import LOGGER_NAME
from simpleval.evaluation.metrics.parsers.parsed_output_schema import JudgeParsedOutput

RESPONSE_TAG_NAME = 'response'
RESPONSE_TAG_TEMP_REPLACEMENT = 'RESPONSE_ELEMENT_TEMP_REPLACEMENT'
RESPONSE_END_TAG_TEMP_REPLACEMENT = 'RESPONSE_END_ELEMENT_TEMP_REPLACEMENT'

REASONINGS_TAG_NAME = 'reasonings'
REASONINGS_TAG_TEMP_REPLACEMENT = 'REASONINGS_ELEMENT_TEMP_REPLACEMENT'
REASONINGS_END_TAG_TEMP_REPLACEMENT = 'REASONINGS_END_ELEMENT_TEMP_REPLACEMENT'

ANSWER_TAG_NAME = 'answer'
ANSWER_TAG_TEMP_REPLACEMENT = 'ANSWER_ELEMENT_TEMP_REPLACEMENT'
ANSWER_END_TAG_TEMP_REPLACEMENT = 'ANSWER_END_ELEMENT_TEMP_REPLACEMENT'


def get_xml_tag(tag_name: str) -> str:
    return f'<{tag_name}>'


def get_xml_end_tag(tag_name: str) -> str:
    return f'</{tag_name}>'


def replace_all_tags_for_escape(xml_string: str) -> str:
    xml_string = xml_string.replace(get_xml_tag(RESPONSE_TAG_NAME), RESPONSE_TAG_TEMP_REPLACEMENT)
    xml_string = xml_string.replace(get_xml_end_tag(RESPONSE_TAG_NAME), RESPONSE_END_TAG_TEMP_REPLACEMENT)

    xml_string = xml_string.replace(get_xml_tag(REASONINGS_TAG_NAME), REASONINGS_TAG_TEMP_REPLACEMENT)
    xml_string = xml_string.replace(get_xml_end_tag(REASONINGS_TAG_NAME), REASONINGS_END_TAG_TEMP_REPLACEMENT)

    xml_string = xml_string.replace(get_xml_tag(ANSWER_TAG_NAME), ANSWER_TAG_TEMP_REPLACEMENT)
    xml_string = xml_string.replace(get_xml_end_tag(ANSWER_TAG_NAME), ANSWER_END_TAG_TEMP_REPLACEMENT)
    return xml_string


def revert_all_tags_after_escape(xml_string: str) -> str:
    xml_string = xml_string.replace(RESPONSE_TAG_TEMP_REPLACEMENT, get_xml_tag(RESPONSE_TAG_NAME))
    xml_string = xml_string.replace(RESPONSE_END_TAG_TEMP_REPLACEMENT, get_xml_end_tag(RESPONSE_TAG_NAME))

    xml_string = xml_string.replace(REASONINGS_TAG_TEMP_REPLACEMENT, get_xml_tag(REASONINGS_TAG_NAME))
    xml_string = xml_string.replace(REASONINGS_END_TAG_TEMP_REPLACEMENT, get_xml_end_tag(REASONINGS_TAG_NAME))

    xml_string = xml_string.replace(ANSWER_TAG_TEMP_REPLACEMENT, get_xml_tag(ANSWER_TAG_NAME))
    xml_string = xml_string.replace(ANSWER_END_TAG_TEMP_REPLACEMENT, get_xml_end_tag(ANSWER_TAG_NAME))
    return xml_string


def parse_xml_response(xml_string: str) -> JudgeParsedOutput:
    """
    Parses the given XML string and extracts the reasoning and answer.

    Args:
        xml_string (str): The XML string to parse.

    Returns:
        dict: A dictionary with 'reasonings' and 'answer' keys.
    """
    start_tag = f'<{RESPONSE_TAG_NAME}>'
    end_tag = f'</{RESPONSE_TAG_NAME}>'
    start_index = xml_string.find(start_tag)
    end_index = xml_string.rfind(end_tag) + len(end_tag)

    if start_index == -1 or end_index == -1:
        raise ValueError(f'XML string is missing required tags ({RESPONSE_TAG_NAME}), XML string: {xml_string}')

    xml_string = xml_string[start_index:end_index]

    xml_string = replace_all_tags_for_escape(xml_string)
    xml_string = xml.sax.saxutils.escape(xml_string)
    xml_string = revert_all_tags_after_escape(xml_string)

    logger = logging.getLogger(LOGGER_NAME)
    try:
        root = ET.fromstring(xml_string)  # noqa - xml sanitized prior to this
        reasonings = root.find(REASONINGS_TAG_NAME).text
        reasonings = xml.sax.saxutils.unescape(reasonings)

        answer = root.find(ANSWER_TAG_NAME).text
        answer = xml.sax.saxutils.unescape(answer)

        return JudgeParsedOutput(reasonings=reasonings, answer=answer)
    except Exception as e:
        logger.error(f'Error parsing XML: `{xml_string}`, Error: {e}')
        raise e
