import json
import xml
import xml.etree.ElementTree

from pydantic import ValidationError

RETRYABLE_PARSING_ERRORS = (
    ValueError,
    ValidationError,
    xml.etree.ElementTree.ParseError,
    json.decoder.JSONDecodeError,
)
