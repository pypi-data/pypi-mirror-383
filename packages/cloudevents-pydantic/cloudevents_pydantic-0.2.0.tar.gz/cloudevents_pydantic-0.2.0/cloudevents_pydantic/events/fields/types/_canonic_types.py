# ==============================================================================
#  Copyright (c) 2024 Federico Busetti                                         =
#  <729029+febus982@users.noreply.github.com>                                  =
#                                                                              =
#  Permission is hereby granted, free of charge, to any person obtaining a     =
#  copy of this software and associated documentation files (the "Software"),  =
#  to deal in the Software without restriction, including without limitation   =
#  the rights to use, copy, modify, merge, publish, distribute, sublicense,    =
#  and/or sell copies of the Software, and to permit persons to whom the       =
#  Software is furnished to do so, subject to the following conditions:        =
#                                                                              =
#  The above copyright notice and this permission notice shall be included in  =
#  all copies or substantial portions of the Software.                         =
#                                                                              =
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR  =
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,    =
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL     =
#  THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER  =
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING     =
#  FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER         =
#  DEALINGS IN THE SOFTWARE.                                                   =
# ==============================================================================
import base64
from datetime import datetime
from enum import Enum
from typing import Annotated, Union
from urllib.parse import ParseResult, urlparse, urlunparse

from annotated_types import Ge, Le
from pydantic import (
    PlainSerializer,
    PlainValidator,
    StringConstraints,
)


def bool_serializer(value: bool) -> str:
    return str(value).lower()


bool_validation_mapping = {
    "true": True,
    True: True,
    "false": False,
    False: False,
}


def bool_validator(value: Union[str, bool]) -> bool:
    if not isinstance(value, (str, bool)):
        raise ValueError(f"Value {value} is not a valid boolean value")

    try:
        return bool_validation_mapping[value]
    except KeyError:
        raise ValueError(f"Value {value} is not a valid boolean value")


def binary_serializer(value: bytes) -> str:
    return base64.b64encode(value).decode()


def time_serializer(value: datetime) -> str:
    return value.isoformat()


def binary_validator(value: Union[str, bytes, bytearray, memoryview]) -> bytes:
    if isinstance(value, (bytes, bytearray, memoryview)):
        return value

    if isinstance(value, str):
        return base64.b64decode(value, validate=True)

    raise ValueError(f"Unsupported value type: {type(value)} - {value}")


def url_serializer(value: ParseResult) -> str:
    return urlunparse(value)


def absolute_uri_validator(value: str) -> ParseResult:
    url = generic_uri_validator(value)
    if not url.scheme:
        raise ValueError("Can't validate absolute URI without scheme")

    return url


def generic_uri_validator(value: str) -> ParseResult:
    if value is None:
        raise ValueError("Field is required")

    return urlparse(value)


"""
Prevents values specified on: https://github.com/cloudevents/spec/blob/v1.0.2/cloudevents/spec.md#type-system
- U+0000-U+001F and U+007F-U+009F ranges - control characters
- non characters specified at: https://www.unicode.org/faq/private_use.html#noncharacters
    - U+FDD0-U+FDEF range
    - U+FFFE and U+FFFF
    - U+1FFFE, U+1FFFF, U+2FFFE, U+2FFFF, ... U+10FFFE, U+10FFFF

We should also check for U+D800-U+DBFF and U+DC00-U+DFFF unless used in pair
(malformed surrogate characters) but pydantic is unhappy to handle them anyway
so we can avoid the scenario in the regex and make this faster.
"""
class_control = r"\u0000-\u001F\u007F-\u009F"
class_nonchar_utf16_range = r"\uFDD0-\uFDEF\uFFFE\uFFFF"
class_nonchar_utf32_range = (
    r"\u{1FFFE}\u{1FFFF}"
    r"\u{2FFFE}\u{2FFFF}"
    r"\u{3FFFE}\u{3FFFF}"
    r"\u{4FFFE}\u{4FFFF}"
    r"\u{5FFFE}\u{5FFFF}"
    r"\u{6FFFE}\u{6FFFF}"
    r"\u{7FFFE}\u{7FFFF}"
    r"\u{8FFFE}\u{8FFFF}"
    r"\u{9FFFE}\u{9FFFF}"
    r"\u{AFFFE}\u{AFFFF}"
    r"\u{BFFFE}\u{BFFFF}"
    r"\u{CFFFE}\u{CFFFF}"
    r"\u{DFFFE}\u{DFFFF}"
    r"\u{EFFFE}\u{EFFFF}"
    r"\u{FFFFE}\u{FFFFF}"
    r"\u{10FFFE}\u{10FFFF}"
)
str_constraint = (
    r"^"
    r"[^"
    + class_control
    + class_nonchar_utf16_range
    + class_nonchar_utf32_range
    + r"]+"
    r"$"
)

str_constraint_asyncapi_compat = (
    r"^" r"[^" + class_control + class_nonchar_utf16_range + r"]+" r"$"
)

str_constraint_mime_type = (
    r"^"
    r"(application|audio|example|font|haptics|image|message|model|multipart|text|video)"
    r"/"
)
"""
Simplified validation regex for mime types. Uses registries defined on
https://www.iana.org/assignments/media-types/media-types.xhtml
"""


Boolean = Annotated[
    bool,
    PlainSerializer(bool_serializer),
    PlainValidator(bool_validator),
]
"""
A boolean value of "true" or "false"
"""

Integer = Annotated[int, Ge(-2147483648), Le(2147483648)]
"""
A whole number in the range -2,147,483,648 to +2,147,483,647 inclusive
"""

String = Annotated[str, StringConstraints(pattern=str_constraint_asyncapi_compat)]
"""
Sequence of allowable Unicode characters
"""

MimeType = Annotated[str, StringConstraints(pattern=str_constraint_mime_type)]
"""
Sequence of allowable Unicode characters
"""

Binary = Annotated[
    bytes,
    PlainValidator(binary_validator),
    PlainSerializer(binary_serializer),
]
"""
Sequence of bytes that accepts both bytes and base64 encoded strings as input
and is serialized to a base64 encoded string.
"""

URI = Annotated[
    ParseResult, PlainValidator(absolute_uri_validator), PlainSerializer(url_serializer)
]
"""
Absolute uniform resource identifier
"""

URIReference = Annotated[
    ParseResult, PlainValidator(generic_uri_validator), PlainSerializer(url_serializer)
]
"""
Uniform resource identifier reference
"""

Timestamp = Annotated[datetime, PlainSerializer(time_serializer)]
"""
Date and time expression using the Gregorian Calendar
"""


class SpecVersion(str, Enum):
    """
    The version of the CloudEvents specification which an event uses.
    This enables the interpretation of the context.

    Currently, this attribute will only have the 'major' and 'minor' version numbers
    included in it. This allows for 'patch' changes to the specification to be made
    without changing this property's value in the serialization.
    """

    # v0_3 = "0.3"
    v1_0 = "1.0"
