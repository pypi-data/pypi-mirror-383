"""
CloudEvent core implementation.

This module provides the CloudEvent class, factory functions, and type guards
for creating and manipulating CloudEvents following the CloudEvents specification.

The CloudEvent class is final and cannot be subclassed. Use composition and
extensions for custom behavior.
"""

from typing import Any, final, TypeGuard
from datetime import datetime
from collections.abc import Mapping
import uuid

from pyeventcloud.core.exceptions import ValidationError, UnsupportedVersionError
from pyeventcloud.utils.types import (
    SpecVersion,
    EventData,
    TimestampAttribute,
    CloudEventDict,
)
from pyeventcloud.specs import CloudEventSpecV10
from pyeventcloud.validation.validators import ValidatorRegistry


def get_spec(specversion: SpecVersion) -> CloudEventSpecV10:
    """
    Get spec validator for the given version.

    Args:
        specversion: CloudEvents spec version

    Returns:
        Spec validator instance

    Raises:
        UnsupportedVersionError: If version is not supported
    """
    validator_registry = ValidatorRegistry()

    if specversion == "1.0":
        return CloudEventSpecV10(validator_registry)
    else:
        raise UnsupportedVersionError(specversion)


@final
class CloudEvent:
    """
    CloudEvent representation with spec-agnostic interface.

    Validation is performed during initialization to ensure
    all events are valid when constructed.

    This class is final and cannot be subclassed. Use composition
    and extensions for custom behavior.

    Attributes:
        id: Unique event identifier
        source: Event source URI-reference
        type: Event type
        specversion: CloudEvents spec version
        datacontenttype: Content type of data attribute
        dataschema: URI of data schema
        subject: Subject of the event
        time: Timestamp as datetime object
        data: Event payload
        data_base64: Base64-encoded binary data
        extensions: Extension attributes
    """

    # Type-annotated instance attributes
    id: str
    source: str
    type: str
    specversion: str  # SpecVersion at runtime, but Protocol expects str
    datacontenttype: str | None
    dataschema: str | None
    subject: str | None
    time: datetime | None
    data: EventData
    data_base64: str | None
    extensions: dict[str, Any]

    def __init__(
        self,
        *,  # Force keyword-only arguments
        id: str,
        source: str,
        type: str,
        specversion: SpecVersion = "1.0",
        datacontenttype: str | None = None,
        dataschema: str | None = None,
        subject: str | None = None,
        time: TimestampAttribute | None = None,
        data: EventData = None,
        data_base64: str | None = None,
        # Extensions via **kwargs
        **extensions: Any,
    ) -> None:
        """
        Initialize CloudEvent with validation.

        Args:
            id: Unique event identifier
            source: Event source URI-reference
            type: Event type (reverse-DNS naming recommended)
            specversion: CloudEvents spec version (default "1.0")
            datacontenttype: Content type of data attribute
            dataschema: URI of data schema
            subject: Subject of the event
            time: Timestamp as datetime or RFC 3339 string
            data: Event payload
            data_base64: Base64-encoded binary data
            **extensions: Extension attributes

        Raises:
            ValidationError: If required attributes are missing or invalid
            UnsupportedVersionError: If specversion is not supported
        """
        # Validate required attributes first (fail-fast)
        if not id or not isinstance(id, str):
            raise ValidationError("id must be a non-empty string", attribute="id")
        if not source or not isinstance(source, str):
            raise ValidationError(
                "source must be a non-empty string", attribute="source"
            )
        if not type or not isinstance(type, str):
            raise ValidationError("type must be a non-empty string", attribute="type")

        # Validate mutual exclusivity
        if data is not None and data_base64 is not None:
            raise ValidationError("Cannot specify both 'data' and 'data_base64'")

        # Normalize time to datetime if string provided
        normalized_time: datetime | None = None
        if isinstance(time, str):
            try:
                # Handle RFC 3339 timestamps with 'Z' suffix
                normalized_time = datetime.fromisoformat(time.replace("Z", "+00:00"))
            except ValueError as e:
                raise ValidationError(
                    f"Invalid timestamp format: {e}", attribute="time"
                )
        elif isinstance(time, datetime):
            normalized_time = time

        # Assign attributes
        self.id = id
        self.source = source
        self.type = type
        self.specversion = specversion
        self.datacontenttype = datacontenttype
        self.dataschema = dataschema
        self.subject = subject
        self.time = normalized_time
        self.data = data
        self.data_base64 = data_base64
        self.extensions = extensions

        # Validate against spec version
        spec = get_spec(self.specversion)
        spec.validate(self)

    def get_attribute(self, name: str, default: Any = None) -> Any:
        """
        Get attribute value, checking extensions if not in standard attributes.

        Args:
            name: Attribute name to get
            default: Default value if attribute not found

        Returns:
            Attribute value or default
        """
        if hasattr(self, name):
            return getattr(self, name)
        return self.extensions.get(name, default)

    def set_extension(self, name: str, value: Any) -> None:
        """
        Set extension attribute.

        Args:
            name: Extension attribute name
            value: Extension attribute value
        """
        self.extensions[name] = value

    def to_dict(self) -> CloudEventDict:
        """
        Convert to type-safe dictionary representation.

        Returns:
            CloudEventDict with all attributes
        """
        # Start with required attributes
        result: CloudEventDict = {
            "id": self.id,
            "source": self.source,
            "type": self.type,
            "specversion": self.specversion,
        }

        # Add optional attributes if present
        if self.datacontenttype is not None:
            result["datacontenttype"] = self.datacontenttype
        if self.dataschema is not None:
            result["dataschema"] = self.dataschema
        if self.subject is not None:
            result["subject"] = self.subject
        if self.time is not None:
            result["time"] = self.time.isoformat()
        if self.data is not None:
            result["data"] = self.data
        if self.data_base64 is not None:
            result["data_base64"] = self.data_base64

        # Add extensions (bypasses TypedDict checking for dynamic keys)
        for key, value in self.extensions.items():
            result[key] = value  # type: ignore[literal-required]

        return result

    def __repr__(self) -> str:
        """
        Return unambiguous string representation.

        Returns:
            String representation showing key attributes
        """
        return (
            f"CloudEvent(id={self.id!r}, source={self.source!r}, "
            f"type={self.type!r}, specversion={self.specversion!r})"
        )

    def __eq__(self, other: object) -> bool:
        """
        Check equality with another CloudEvent.

        Two CloudEvents are equal if all their attributes match,
        including extensions.

        Args:
            other: Object to compare with

        Returns:
            True if events are equal
        """
        if not isinstance(other, CloudEvent):
            return NotImplemented
        return (
            self.id == other.id
            and self.source == other.source
            and self.type == other.type
            and self.specversion == other.specversion
            and self.datacontenttype == other.datacontenttype
            and self.dataschema == other.dataschema
            and self.subject == other.subject
            and self.time == other.time
            and self.data == other.data
            and self.data_base64 == other.data_base64
            and self.extensions == other.extensions
        )

    def __hash__(self) -> int:
        """
        Return hash for use in sets/dicts.

        Returns:
            Hash based on id, source, type, and specversion
        """
        return hash((self.id, self.source, self.type, self.specversion))


def from_dict(data: CloudEventDict | Mapping[str, Any]) -> CloudEvent:
    """
    Create CloudEvent from dictionary.

    Accepts both TypedDict (CloudEventDict) and generic mappings.
    Automatically separates known attributes from extensions.

    Args:
        data: Dictionary containing event attributes

    Returns:
        CloudEvent instance

    Raises:
        ValidationError: If required attributes are missing or invalid

    Example:
        >>> event = from_dict({
        ...     "id": "123",
        ...     "source": "https://example.com",
        ...     "type": "com.example.event",
        ...     "customext": "value"
        ... })
    """
    # Separate known attributes from extensions
    known_attrs: frozenset[str] = frozenset(
        {
            "id",
            "source",
            "type",
            "specversion",
            "datacontenttype",
            "dataschema",
            "subject",
            "time",
            "data",
            "data_base64",
        }
    )

    event_attrs: dict[str, Any] = {}
    extensions: dict[str, Any] = {}

    for key, value in data.items():
        if key in known_attrs:
            event_attrs[key] = value
        else:
            extensions[key] = value

    return CloudEvent(**event_attrs, **extensions)


def create_event(
    source: str,
    type: str,
    *,
    id: str | None = None,
    data: EventData = None,
    specversion: SpecVersion = "1.0",
    **kwargs: Any,
) -> CloudEvent:
    """
    Convenience function to create CloudEvent with auto-generated ID.

    This is the recommended way to create events when you don't want
    to manually generate UUIDs.

    Args:
        source: Event source URI-reference
        type: Event type (reverse-DNS naming recommended)
        id: Event ID (auto-generated UUID if not provided)
        data: Event payload
        specversion: CloudEvents spec version (default "1.0")
        **kwargs: Additional attributes and extensions

    Returns:
        CloudEvent instance

    Raises:
        ValidationError: If validation fails

    Example:
        >>> event = create_event(
        ...     source="https://example.com/orders",
        ...     type="com.example.order.created",
        ...     data={"order_id": 123},
        ...     partitionkey="order-123"
        ... )
    """
    if id is None:
        id = str(uuid.uuid4())

    return CloudEvent(
        id=id, source=source, type=type, specversion=specversion, data=data, **kwargs
    )


def is_cloudevent_dict(data: Mapping[str, Any]) -> TypeGuard[CloudEventDict]:
    """
    Type guard to check if mapping has required CloudEvent attributes.

    Args:
        data: Mapping to check

    Returns:
        True if data has required CloudEvent attributes
    """
    required = {"id", "source", "type", "specversion"}
    return all(key in data and isinstance(data[key], str) for key in required)


def is_valid_spec_version(version: str) -> TypeGuard[SpecVersion]:
    """
    Type guard to check if string is a valid SpecVersion.

    Args:
        version: String to check

    Returns:
        True if version is "1.0"
    """
    return version == "1.0"
