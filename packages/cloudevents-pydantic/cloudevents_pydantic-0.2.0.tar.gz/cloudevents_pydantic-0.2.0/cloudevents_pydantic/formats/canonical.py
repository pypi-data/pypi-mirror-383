# ==============================================================================
#  Copyright (c) 2025 Federico Busetti                                         =
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
from typing import Dict, List, TypeVar

from pydantic import TypeAdapter

from cloudevents_pydantic.events import CloudEvent

_T = TypeVar("_T", bound=CloudEvent)


def serialize(event: CloudEvent) -> Dict[str, str]:
    """
    Serializes an event to a dictionary with canonical values representations.

    :param event: The event object to serialize
    :type event: CloudEvent
    :return: The headers and the body representation of the event
    :rtype: Dict[str, str]
    """
    return event.model_dump()


def deserialize(
    data: Dict[str, str], event_adapter: TypeAdapter[_T] = TypeAdapter(CloudEvent)
) -> _T:
    """
    Deserializes an event from a dictionary with canonical values representations.

    :param data: the canonical dictionary representation of the event
    :type data: Dict[str, str]
    :param event_adapter: The event class to build
    :type event_adapter: Type[CloudEvent]
    :return: The deserialized event
    :rtype: CloudEvent
    """
    return event_adapter.validate_python(data)


def serialize_batch(
    events: List[_T],
    batch_adapter: TypeAdapter[List[_T]] = TypeAdapter(List[CloudEvent]),
) -> List[Dict[str, str]]:
    """
    Serializes a list of events to dictionaries with canonical values representations.

    :param events: The event object to serialize
    :type events: List[CloudEvent]
    :param batch_adapter: The pydantic TypeAdapter to use
    :type: TypeAdapter[List[CloudEvent]]
    :return: The serialized event batch
    :rtype: List[Dict[str, str]]
    """
    return batch_adapter.dump_python(events)


def deserialize_batch(
    data: List[Dict[str, str]],
    batch_adapter: TypeAdapter[List[_T]] = TypeAdapter(List[CloudEvent]),
) -> List[_T]:
    """
    Deserializes a list of events from a list of dictionaries with
    canonical values representations.

    :param data: the list of canonical dictionary representations of the events
    :type data: List[Dict[str, str]]
    :param batch_adapter: The pydantic TypeAdapter to use
    :type: TypeAdapter[List[CloudEvent]]
    :return: The deserialized event batch
    :rtype: List[CloudEvent]
    """
    return batch_adapter.validate_python(data)
