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
from typing import List, TypeVar

from pydantic import TypeAdapter

from ..events import CloudEvent

_T = TypeVar("_T", bound=CloudEvent)


def serialize(event: CloudEvent) -> str:
    """
    Serializes an event in JSON format.

    :param event: The event object to serialize
    :type event: CloudEvent
    :return: The headers and the body representation of the event
    :rtype: str
    """
    # It seems that TypeAdapter is slightly faster than using the event,
    # maybe we should replace this...
    return event.model_dump_json()


def deserialize(
    data: str, event_adapter: TypeAdapter[_T] = TypeAdapter(CloudEvent)
) -> _T:
    """
    Deserializes an event from JSON format.

    :param data: the JSON representation of the event
    :type data: str
    :param event_adapter: The event class to build
    :type event_adapter: Type[CloudEvent]
    :return: The deserialized event
    :rtype: CloudEvent
    """
    return event_adapter.validate_json(data)


def serialize_batch(
    events: List[_T],
    batch_adapter: TypeAdapter[List[_T]] = TypeAdapter(List[CloudEvent]),
) -> str:
    """
    Serializes a list of events in JSON batch format.

    :param events: The event object to serialize
    :type events: List[CloudEvent]
    :param batch_adapter: The pydantic TypeAdapter to use
    :type: TypeAdapter[List[CloudEvent]]
    :return: The serialized event batch
    :rtype: str
    """
    return batch_adapter.dump_json(events).decode()


def deserialize_batch(
    data: str,
    batch_adapter: TypeAdapter[List[_T]] = TypeAdapter(List[CloudEvent]),
) -> List[_T]:
    """
    Deserializes a list of events from JSON batch format.

    :param data: The JSON representation of the event batch
    :type data: str
    :param batch_adapter: The pydantic TypeAdapter to use
    :type: TypeAdapter[List[CloudEvent]]
    :return: The deserialized event batch
    :rtype: List[CloudEvent]
    """
    return batch_adapter.validate_json(data)
