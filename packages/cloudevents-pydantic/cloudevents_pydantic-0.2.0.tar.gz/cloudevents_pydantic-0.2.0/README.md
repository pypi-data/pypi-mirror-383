# cloudevents-pydantic

![Static Badge](https://img.shields.io/badge/Python-3.9_%7C_3.10_%7C_3.11_%7C_3.12_%7C_3.13-blue?logo=python&logoColor=white)
[![Stable Version](https://img.shields.io/pypi/v/cloudevents-pydantic?color=blue)](https://pypi.org/project/cloudevents-pydantic/)
[![stability-beta](https://img.shields.io/badge/stability-beta-33bbff.svg)](https://github.com/mkenney/software-guides/blob/master/STABILITY-BADGES.md#beta)

[![Python tests](https://github.com/febus982/cloudevents-pydantic/actions/workflows/python-tests.yml/badge.svg?branch=main)](https://github.com/febus982/cloudevents-pydantic/actions/workflows/python-tests.yml)
[![Maintainability](https://qlty.sh/badges/9abc9122-bfd4-4ad1-bdbd-cb2e8324180b/maintainability.svg)](https://qlty.sh/gh/febus982/projects/cloudevents-pydantic)
[![Code Coverage](https://qlty.sh/badges/9abc9122-bfd4-4ad1-bdbd-cb2e8324180b/test_coverage.svg)](https://qlty.sh/gh/febus982/projects/cloudevents-pydantic)

[![Checked with mypy](https://www.mypy-lang.org/static/mypy_badge.svg)](https://mypy-lang.org/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v1.json)](https://github.com/charliermarsh/ruff)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![security: bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)
[![Pydantic v2](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/pydantic/pydantic/main/docs/badge/v2.json)](https://pydantic.dev)

This is an implementation of the [CloudEvents spec](https://github.com/cloudevents/spec/tree/main) using
[Pydantic V2](https://docs.pydantic.dev/latest/) for high performance during validation and serialization.

It is meant to support natively [FastAPI](https://fastapi.tiangolo.com/)
and [FastStream](https://faststream.airt.ai/latest/) (WIP)

## How to use

```shell
pip install cloudevents-pydantic
```

```python
from cloudevents_pydantic.bindings.http import HTTPHandler
from cloudevents_pydantic.events import CloudEvent

handler = HTTPHandler()
minimal_attributes = {
    "type": "com.example.string",
    "source": "https://example.com/event-producer",
}

# `CloudEvent` is a Pydantic model to handle validation and serialization
# `event_factory` is a helper method to autogenerate some of the mandatory 
# such as id, time, specversion
event = CloudEvent.event_factory(**minimal_attributes)

# Single event HTTP serialization
headers, single_event_as_json = handler.to_json(event)

# Batch of events HTTP serialization
headers, batch_of_events_as_json = handler.to_json_batch([event])

# Parsing a JSON string for a single event
parsed_event = handler.from_json(single_event_as_json)

# Parsing a JSON string for a single event
parsed_event_list = handler.from_json(batch_of_events_as_json)
```

Refer to the [docs](https://febus982.github.io/cloudevents-pydantic/) for more advanced use cases and
for details on how to create custom events.

## Performance

Using pydantic gives a great performance boost if compared to the official SDK. (there's obviously
some performance issue in the official serialization using pydantic)

These results come from a Macbook Pro M4 Pro on python 3.13. Feel free to run the `benchmark.py`
script yourself.

```
==== 1M iterations benchmark ====
Timings for HTTP JSON deserialization:
This package: 2.3955996250006137
Official SDK using pydantic model: 11.389213957998436
Official SDK using http model: 10.174893917006557

Timings for HTTP JSON serialization:
This package: 3.497491959002218
Official SDK using pydantic model: 31.92037604199868
Official SDK using http model: 6.780242209002608
```

## Supported specification features

| Core Specification | [v1.0](https://github.com/cloudevents/spec/blob/v1.0.2/spec.md) |
|--------------------|:---------------------------------------------------------------:|
| CloudEvents Core   |                                ✅                                |

---

| Event Formats     | [v1.0](https://github.com/cloudevents/spec/blob/v1.0.2/spec.md#event-format) |
|-------------------|:----------------------------------------------------------------------------:|
| AVRO Event Format |                                      ❌                                       |
| JSON Event Format |                                      ✅                                       |

---

| Protocol Bindings      | [v1.0](https://github.com/cloudevents/spec/blob/v1.0.2/spec.md#protocol-binding) |
|------------------------|:--------------------------------------------------------------------------------:|
| HTTP Protocol Binding  |                                        ✅                                         |
| Kafka Protocol Binding |                                        ❌                                         |

---

| Content Modes    | [v1.0](https://github.com/cloudevents/spec/blob/v1.0.2/http-protocol-binding.md#13-content-modes) |
|------------------|:-------------------------------------------------------------------------------------------------:|
| HTTP Binary      |                                                 ✅                                                 |
| HTTP Structured  |                                                 ✅                                                 |
| HTTP Batch       |                                                 ✅                                                 |
| Kafka Binary     |                                                 ❌                                                 |
| Kafka Structured |                                                 ❌                                                 |
| Kafka Batch      |                                                 ❌                                                 |

## Commands for development

All the common commands used during development can be run using make targets:

* `make dev-dependencies`: Install dev requirements
* `make fix`: Run code style and lint automatic fixes (where possible)
* `make test`: Run test suite against system python version
* `make check`: Run tests against all available python versions, code style and lint checks
* `make type`, `make format`, `make lint`, `make bandit`: Run the relevant check
* `make docs`: Render the mkdocs website locally
