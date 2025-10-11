"""
CloudEvents JSON format implementation.

This module implements JSON serialization and deserialization for CloudEvents
following the JSON Event Format specification.

Reference: https://github.com/cloudevents/spec/blob/v1.0.2/cloudevents/formats/json-format.md
"""

import base64
import json
import re
from collections.abc import Callable, Mapping
from datetime import datetime
from json import JSONEncoder
from typing import Any, Final, Pattern

from pyeventcloud.core.event import CloudEvent, from_dict
from pyeventcloud.core.exceptions import SerializationError
from pyeventcloud.utils.types import CloudEventDict


class _CloudEventJSONEncoder(JSONEncoder):
    """
    Custom JSON encoder for CloudEvents.

    Handles datetime objects by converting them to RFC 3339 format
    with proper UTC offset notation (Z for +00:00).
    """

    def default(self, o: Any) -> Any:
        """
        Encode datetime objects to RFC 3339 format.

        Args:
            o: Object to encode

        Returns:
            Encoded representation
        """
        if isinstance(o, datetime):
            dt = o.isoformat()
            # 'Z' denotes a UTC offset of 00:00 per RFC 3339 section 2
            # https://www.rfc-editor.org/rfc/rfc3339#section-2
            if dt.endswith("+00:00"):
                dt = dt.removesuffix("+00:00") + "Z"
            return dt

        return super().default(o)


class JSONFormatter:
    """
    JSON formatter for CloudEvents.

    Handles serialization and deserialization of CloudEvents to/from JSON,
    including proper handling of binary data via base64 encoding.
    Uses custom JSON encoder for datetime serialization and regex pattern
    matching for intelligent content type detection.
    """

    # Content type for CloudEvents JSON format
    content_type: Final[str] = "application/cloudevents+json"

    # Regex pattern to detect JSON content types
    # Matches application/json, text/json, application/*+json, etc.
    JSON_CONTENT_TYPE_PATTERN: Final[Pattern[str]] = re.compile(
        r"^(application|text)/([a-zA-Z0-9\-\.]+\+)?json(;.*)?$"
    )

    def serialize(self, event: CloudEvent) -> str:
        """
        Serialize CloudEvent to JSON string.

        Converts the CloudEvent to a JSON string following the JSON Event Format
        specification. Binary data (data_base64) is properly encoded.

        Args:
            event: CloudEvent to serialize

        Returns:
            JSON string representation

        Raises:
            SerializationError: If serialization fails
        """
        try:
            event_dict = self._event_to_dict(event)
            return json.dumps(
                event_dict,
                cls=_CloudEventJSONEncoder,
                ensure_ascii=False,
                separators=(',', ':')
            )
        except (TypeError, ValueError) as e:
            raise SerializationError(
                f"Failed to serialize CloudEvent to JSON: {e}",
                event_id=event.id
            ) from e

    def deserialize(
        self,
        data: str,
        event_factory: Callable[[dict[str, Any]], CloudEvent] | None = None
    ) -> CloudEvent:
        """
        Deserialize JSON string to CloudEvent.

        Parses a JSON string and creates a CloudEvent instance. Validates
        that the JSON structure is valid and contains required fields.
        Optionally accepts a factory function for custom CloudEvent creation.

        Args:
            data: JSON string to deserialize
            event_factory: Optional factory function to create CloudEvent.
                          Defaults to from_dict if not provided.

        Returns:
            CloudEvent instance

        Raises:
            SerializationError: If deserialization fails
        """
        if not isinstance(data, str):
            raise SerializationError("Input must be a string")

        if not data.strip():
            raise SerializationError("Input cannot be empty")

        try:
            parsed = json.loads(data)
        except json.JSONDecodeError as e:
            raise SerializationError(f"Invalid JSON: {e}") from e

        if not isinstance(parsed, dict):
            raise SerializationError("JSON must be an object (dictionary)")

        try:
            factory = event_factory or from_dict
            return factory(parsed)
        except Exception as e:
            raise SerializationError(f"Failed to create CloudEvent from JSON: {e}") from e

    def serialize_batch(self, events: list[CloudEvent]) -> str:
        """
        Serialize multiple CloudEvents to JSON array.

        Creates a JSON array containing multiple CloudEvents. This is useful
        for batch processing scenarios.

        Args:
            events: List of CloudEvents to serialize

        Returns:
            JSON array string

        Raises:
            SerializationError: If serialization fails
        """
        if not isinstance(events, list):
            raise SerializationError("events must be a list")

        try:
            event_dicts = [self._event_to_dict(event) for event in events]
            return json.dumps(
                event_dicts,
                cls=_CloudEventJSONEncoder,
                ensure_ascii=False,
                separators=(',', ':')
            )
        except (TypeError, ValueError) as e:
            raise SerializationError(f"Failed to serialize batch: {e}") from e

    def deserialize_batch(
        self,
        data: str,
        event_factory: Callable[[dict[str, Any]], CloudEvent] | None = None
    ) -> list[CloudEvent]:
        """
        Deserialize JSON array to list of CloudEvents.

        Parses a JSON array and creates CloudEvent instances for each element.
        Optionally accepts a factory function for custom CloudEvent creation.

        Args:
            data: JSON array string
            event_factory: Optional factory function to create CloudEvent.
                          Defaults to from_dict if not provided.

        Returns:
            List of CloudEvent instances

        Raises:
            SerializationError: If deserialization fails
        """
        if not isinstance(data, str):
            raise SerializationError("Input must be a string")

        if not data.strip():
            raise SerializationError("Input cannot be empty")

        try:
            parsed = json.loads(data)
        except json.JSONDecodeError as e:
            raise SerializationError(f"Invalid JSON: {e}") from e

        if not isinstance(parsed, list):
            raise SerializationError("JSON must be an array for batch deserialization")

        try:
            factory = event_factory or from_dict
            return [factory(item) for item in parsed]
        except Exception as e:
            raise SerializationError(f"Failed to deserialize batch: {e}") from e

    def _event_to_dict(self, event: CloudEvent) -> dict[str, Any]:
        """
        Convert CloudEvent to dictionary for serialization.

        Args:
            event: CloudEvent to convert

        Returns:
            Dictionary representation suitable for JSON serialization
        """
        result: dict[str, Any] = {
            "id": event.id,
            "source": event.source,
            "type": event.type,
            "specversion": event.specversion,
        }

        # Add optional attributes if present
        if event.datacontenttype:
            result["datacontenttype"] = event.datacontenttype

        if event.dataschema:
            result["dataschema"] = event.dataschema

        if event.subject:
            result["subject"] = event.subject

        if event.time:
            # Custom encoder will handle datetime serialization
            result["time"] = event.time

        # Handle data with intelligent content type detection
        if event.data is not None:
            # Check if data should be serialized as JSON or string
            datacontenttype = event.datacontenttype or "application/json"

            # If data is bytes/bytearray, encode as base64
            if isinstance(event.data, (bytes, bytearray)):
                result["data_base64"] = base64.b64encode(event.data).decode("utf-8")
            # If content type is JSON-compatible, serialize as-is
            elif self.JSON_CONTENT_TYPE_PATTERN.match(datacontenttype):
                result["data"] = event.data
            # Otherwise, convert to string
            else:
                result["data"] = str(event.data)

        # Handle explicit data_base64 field
        if event.data_base64 is not None:
            result["data_base64"] = event.data_base64

        # Add extensions
        if event.extensions:
            result.update(event.extensions)

        return result


def to_json(event: CloudEvent) -> str:
    """
    Convenience function to serialize CloudEvent to JSON.

    Args:
        event: CloudEvent to serialize

    Returns:
        JSON string representation
    """
    formatter = JSONFormatter()
    return formatter.serialize(event)


def from_json(data: str) -> CloudEvent:
    """
    Convenience function to deserialize JSON to CloudEvent.

    Args:
        data: JSON string to deserialize

    Returns:
        CloudEvent instance
    """
    formatter = JSONFormatter()
    return formatter.deserialize(data)


def to_json_batch(events: list[CloudEvent]) -> str:
    """
    Convenience function to serialize multiple CloudEvents to JSON array.

    Args:
        events: List of CloudEvents to serialize

    Returns:
        JSON array string
    """
    formatter = JSONFormatter()
    return formatter.serialize_batch(events)


def from_json_batch(data: str) -> list[CloudEvent]:
    """
    Convenience function to deserialize JSON array to CloudEvents.

    Args:
        data: JSON array string

    Returns:
        List of CloudEvent instances
    """
    formatter = JSONFormatter()
    return formatter.deserialize_batch(data)
