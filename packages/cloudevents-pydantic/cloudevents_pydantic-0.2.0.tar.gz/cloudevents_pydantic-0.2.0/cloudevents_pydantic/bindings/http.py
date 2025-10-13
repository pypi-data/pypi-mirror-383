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
from typing import (
    Any,
    Dict,
    Generic,
    List,
    NamedTuple,
    Optional,
    Type,
    TypeVar,
    cast,
)
from urllib.parse import quote, unquote

from pydantic import TypeAdapter

from cloudevents_pydantic.events import CloudEvent
from cloudevents_pydantic.formats import canonical, json

_T = TypeVar("_T", bound=CloudEvent)


class HTTPComponents(NamedTuple):
    headers: Dict[str, str]
    body: Optional[str]


_HTTP_safe_chars = "".join(
    [
        x
        for x in list(map(chr, range(ord("\u0021"), ord("\u007e") + 1)))
        if x not in [" ", '"', "%"]
    ]
)
"""
Characters NOT to be percent encoded in http headers.
https://github.com/cloudevents/spec/blob/v1.0.2/cloudevents/bindings/http-protocol-binding.md#3132-http-header-values
"""


class HTTPHandler(Generic[_T]):
    event_adapter: TypeAdapter[_T]
    batch_adapter: TypeAdapter[List[_T]]

    def __init__(self, event_class: Type[_T] = cast(Type[_T], CloudEvent)) -> None:
        super().__init__()
        self.event_adapter = TypeAdapter(event_class)
        self.batch_adapter = TypeAdapter(List[event_class])  # type: ignore[valid-type]

    def to_json(self, event: _T) -> HTTPComponents:
        """
        Serializes an event in JSON format.

        :param event: The event object to serialize
        :type event: CloudEvent
        :return: The headers and the body representation of the event
        :rtype: HTTPComponents
        """
        headers = {"content-type": "application/cloudevents+json; charset=UTF-8"}
        body = json.serialize(event)
        return HTTPComponents(headers, body)

    def to_json_batch(self, events: List[_T]) -> HTTPComponents:
        """
        Serializes a list of events in JSON batch format.

        :param events: The event object to serialize
        :type events: List[CloudEvent]
        :return: The headers and the body representation of the event batch
        :rtype: HTTPComponents
        """
        headers = {"content-type": "application/cloudevents-batch+json; charset=UTF-8"}
        body = json.serialize_batch(events, self.batch_adapter)
        return HTTPComponents(headers, body)

    def from_json(
        self,
        body: str,
    ) -> CloudEvent:
        """
        Deserializes an event from JSON format.

        :param body: The JSON representation of the event
        :type body: str
        :return: The deserialized event
        :rtype: CloudEvent
        """
        return json.deserialize(body, self.event_adapter)

    def from_json_batch(
        self,
        body: str,
    ) -> List[_T]:
        """
        Deserializes a list of events from JSON batch format.

        :param body: The JSON representation of the event batch
        :type body: str
        :return: The deserialized event batch
        :rtype: List[CloudEvent]
        """
        return json.deserialize_batch(body, self.batch_adapter)

    def to_binary(self, event: _T) -> HTTPComponents:
        """
        Serializes an event in HTTP binary format.

        :param event: The event object to serialize
        :type event: CloudEvent
        :return: The headers and the body representation of the event
        :rtype: HTTPComponents
        """
        if event.datacontenttype is None:
            raise ValueError("Can't serialize event without datacontenttype")

        serialized = canonical.serialize(event)

        body = serialized.get("data")
        headers = {
            f"ce-{k}": self._header_encode(v)
            for k, v in serialized.items()
            if k not in ["data", "datacontenttype"] and v is not None
        }
        headers["content-type"] = self._header_encode(serialized["datacontenttype"])

        return HTTPComponents(headers, body)

    def from_binary(self, headers: Dict[str, str], body: Any) -> CloudEvent:
        """
        Deserializes an event from HTTP binary format.

        :param headers: The request headers
        :type headers: Dict[str, str]
        :param body: The request body
        :type body: Any
        :return:
        """
        if not headers.get("content-type"):
            raise ValueError("content-type not found in headers")

        canonical_data = {
            k[3:]: self._header_decode(v)
            for k, v in headers.items()
            if k.startswith("ce-")
        }
        canonical_data["datacontenttype"] = self._header_decode(headers["content-type"])
        canonical_data["data"] = body
        return canonical.deserialize(canonical_data, self.event_adapter)

    def _header_encode(self, value: str) -> str:
        return quote(value, safe=_HTTP_safe_chars)

    def _header_decode(self, value: str) -> str:
        return unquote(value, errors="strict")
