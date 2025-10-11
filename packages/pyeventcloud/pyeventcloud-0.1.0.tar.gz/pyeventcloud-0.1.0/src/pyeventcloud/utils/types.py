"""
Type definitions for PyEventCloud.

This module contains all type aliases and TypedDict classes used throughout
the PyEventCloud library, following the CloudEvents specification.

The types defined here ensure type safety and provide clear documentation
for the structure of CloudEvents and related protocol messages.
"""

from typing import Any, TypedDict, Literal, Union, NotRequired
from datetime import datetime

# Spec version literals
SpecVersion = Literal["1.0"]
"""
CloudEvents specification version.

Currently supports:
- "1.0": CloudEvents 1.0 specification
"""

# Attribute value types
StringAttribute = str
"""String attribute type for CloudEvent attributes."""

URIAttribute = str
"""URI-reference as per RFC 3986."""

TimestampAttribute = Union[datetime, str]
"""
Timestamp attribute type.

Can be either:
- datetime object: Will be converted to RFC 3339 string
- str: Must be a valid RFC 3339 timestamp string
"""

BinaryAttribute = bytes
"""Binary attribute type for CloudEvent data."""

IntegerAttribute = int
"""Integer attribute type for CloudEvent attributes."""

BooleanAttribute = bool
"""Boolean attribute type for CloudEvent attributes."""

# Type for event data (can be anything JSON-serializable)
EventData = Union[
    None,
    str,
    int,
    float,
    bool,
    list[Any],
    dict[str, Any],
]
"""
Type for CloudEvent data field.

The data field can contain any JSON-serializable value:
- None: No data
- str: String data
- int: Integer data
- float: Floating point data
- bool: Boolean data
- list[Any]: Array data
- dict[str, Any]: Object data
"""


# TypedDict for CloudEvent dictionary representation
class CloudEventDict(TypedDict, total=False):
    """
    Type-safe dictionary representation of CloudEvent.

    This TypedDict represents a CloudEvent in dictionary form, including
    both required and optional fields as per the CloudEvents specification.

    Required fields (must be present):
    - id: Unique identifier for the event
    - source: Context in which the event happened
    - type: Type of event related to the originating occurrence
    - specversion: CloudEvents specification version

    Optional fields:
    - datacontenttype: Content type of data value
    - dataschema: Schema that data adheres to
    - subject: Subject of the event in context of event producer
    - time: Timestamp of when the occurrence happened
    - data: Event payload
    - data_base64: Base64 encoded event payload

    Extension attributes are also allowed but not explicitly defined here.
    """
    # Required
    id: str
    source: str
    type: str
    specversion: str

    # Optional
    datacontenttype: NotRequired[str]
    dataschema: NotRequired[str]
    subject: NotRequired[str]
    time: NotRequired[str]
    data: NotRequired[Any]
    data_base64: NotRequired[str]

    # Extensions (any additional keys)


# TypedDict for HTTP headers
class HTTPHeaders(TypedDict, total=False):
    """
    Type-safe HTTP headers for CloudEvents binary content mode.

    In binary content mode, CloudEvent attributes are mapped to HTTP headers
    with the 'ce-' prefix. This TypedDict defines common headers used in
    CloudEvents over HTTP transport.

    Fields:
    - ce_id: CloudEvent id attribute
    - ce_source: CloudEvent source attribute
    - ce_type: CloudEvent type attribute
    - ce_specversion: CloudEvent specversion attribute
    - Content_Type: HTTP Content-Type header

    Note: Additional ce-* headers can be present for extension attributes.
    """
    ce_id: NotRequired[str]
    ce_source: NotRequired[str]
    ce_type: NotRequired[str]
    ce_specversion: NotRequired[str]
    Content_Type: NotRequired[str]


# TypedDict for Kafka message
class KafkaMessage(TypedDict):
    """
    Type-safe Kafka message structure for CloudEvents.

    Represents a Kafka message containing a CloudEvent. CloudEvents can be
    transmitted via Kafka in both structured and binary content modes.

    Fields:
    - value: Message payload as bytes
    - headers: List of (key, value) tuples for message headers
    - key: Optional message key for partitioning
    """
    value: bytes
    headers: list[tuple[str, bytes]]
    key: bytes | None


# TypedDict for AMQP message
class AMQPMessage(TypedDict):
    """
    Type-safe AMQP message structure for CloudEvents.

    Represents an AMQP message containing a CloudEvent. CloudEvents can be
    transmitted via AMQP (e.g., RabbitMQ) in both structured and binary
    content modes.

    Fields:
    - body: Message body as bytes
    - properties: AMQP message properties (e.g., content_type, message_id)
    - application_properties: Custom application-level properties
    """
    body: bytes
    properties: dict[str, Any]
    application_properties: dict[str, Any]
