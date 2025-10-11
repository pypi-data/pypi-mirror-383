"""
CloudEvents Kafka protocol binding.

This module implements the CloudEvents Kafka protocol binding for both
structured and binary content modes. The binding is format-agnostic and
uses the EventSerializer protocol for serialization.

Reference: https://github.com/cloudevents/spec/blob/v1.0.2/cloudevents/bindings/kafka-protocol-binding.md
"""

from collections.abc import Mapping
from typing import Any, TypedDict

from pyeventcloud.bindings.http import EventSerializer
from pyeventcloud.core.event import CloudEvent, from_dict
from pyeventcloud.core.exceptions import BindingError


class KafkaMessage(TypedDict, total=False):
    """
    Kafka message structure.

    Attributes:
        value: Message payload (bytes)
        headers: Message headers (list of tuples)
        key: Partition key (bytes, optional)
    """

    value: bytes
    headers: list[tuple[str, bytes]]
    key: bytes | None


class KafkaBinding:
    """
    CloudEvents Kafka protocol binding.

    Implements both structured and binary content modes for Kafka transport.
    The binding is format-agnostic through the EventSerializer protocol.

    In Kafka, headers are represented as a list of (key, value) tuples where
    values are bytes. The partitionkey extension is mapped to the Kafka
    message key for proper partitioning.
    """

    # Kafka header prefix for binary mode
    HEADER_PREFIX = "ce_"

    def to_structured(
        self,
        event: CloudEvent,
        serializer: EventSerializer,
    ) -> KafkaMessage:
        """
        Convert CloudEvent to Kafka structured content mode.

        In structured mode, the event is serialized in the message value with
        a content-type header indicating CloudEvents format.

        Args:
            event: CloudEvent to convert
            serializer: Serializer to use for event serialization

        Returns:
            KafkaMessage dict with value, headers, and optional key

        Raises:
            BindingError: If conversion fails
        """
        try:
            serialized = serializer.serialize(event)
            value = serialized.encode("utf-8")

            # Infer content type from serializer
            content_type = self._get_content_type(serializer)

            headers: list[tuple[str, bytes]] = [
                ("content-type", content_type.encode("utf-8")),
            ]

            # Extract partition key from partitionkey extension
            key: bytes | None = None
            if "partitionkey" in event.extensions:
                partition_key = event.extensions["partitionkey"]
                key = str(partition_key).encode("utf-8")

            return KafkaMessage(value=value, headers=headers, key=key)

        except Exception as e:
            raise BindingError(
                f"Failed to convert event to Kafka structured mode: {e}",
                event_id=event.id,
            ) from e

    def from_structured(
        self,
        message: Mapping[str, Any],
        serializer: EventSerializer,
    ) -> CloudEvent:
        """
        Parse CloudEvent from Kafka structured content mode.

        Args:
            message: Kafka message dict with 'value' and 'headers' keys
            serializer: Serializer to use for deserialization

        Returns:
            CloudEvent instance

        Raises:
            BindingError: If parsing fails
        """
        # Extract value
        value = message.get("value")
        if value is None:
            raise BindingError("Kafka message missing 'value' field")

        # Decode value if bytes
        if isinstance(value, bytes):
            try:
                value_str = value.decode("utf-8")
            except UnicodeDecodeError as e:
                raise BindingError(f"Failed to decode value as UTF-8: {e}") from e
        else:
            value_str = value

        # Validate content type from headers
        headers = message.get("headers", [])
        self._validate_structured_headers(headers)

        try:
            return serializer.deserialize(value_str)
        except Exception as e:
            raise BindingError(
                f"Failed to parse event from Kafka structured mode: {e}"
            ) from e

    def to_binary(self, event: CloudEvent) -> KafkaMessage:
        """
        Convert CloudEvent to Kafka binary content mode.

        In binary mode, CloudEvents attributes are mapped to Kafka headers with
        the "ce_" prefix, and the event data is placed in the message value.

        Args:
            event: CloudEvent to convert

        Returns:
            KafkaMessage dict with value, headers, and optional key

        Raises:
            BindingError: If conversion fails
        """
        try:
            headers: list[tuple[str, bytes]] = []

            # Required attributes
            headers.append((f"{self.HEADER_PREFIX}id", event.id.encode("utf-8")))
            headers.append(
                (f"{self.HEADER_PREFIX}source", event.source.encode("utf-8"))
            )
            headers.append((f"{self.HEADER_PREFIX}type", event.type.encode("utf-8")))
            headers.append(
                (
                    f"{self.HEADER_PREFIX}specversion",
                    event.specversion.encode("utf-8"),
                )
            )

            # Optional attributes
            if event.datacontenttype:
                headers.append(
                    ("content-type", event.datacontenttype.encode("utf-8"))
                )

            if event.dataschema:
                headers.append(
                    (
                        f"{self.HEADER_PREFIX}dataschema",
                        event.dataschema.encode("utf-8"),
                    )
                )

            if event.subject:
                headers.append(
                    (f"{self.HEADER_PREFIX}subject", event.subject.encode("utf-8"))
                )

            if event.time:
                # Format as RFC 3339
                time_str = event.time.isoformat().replace("+00:00", "Z")
                headers.append(
                    (f"{self.HEADER_PREFIX}time", time_str.encode("utf-8"))
                )

            # Extensions (excluding partitionkey which goes to message key)
            for ext_name, ext_value in event.extensions.items():
                if ext_name != "partitionkey":
                    headers.append(
                        (
                            f"{self.HEADER_PREFIX}{ext_name}",
                            str(ext_value).encode("utf-8"),
                        )
                    )

            # Handle message value (data or data_base64)
            value = b""
            if event.data_base64:
                # Binary data - decode from base64
                import base64

                value = base64.b64decode(event.data_base64)
            elif event.data is not None:
                # Text/structured data
                import json

                if isinstance(event.data, (str, int, float, bool)):
                    # Scalar values - convert to string
                    value = str(event.data).encode("utf-8")
                else:
                    # Complex data - JSON serialize
                    value = json.dumps(event.data, ensure_ascii=False).encode("utf-8")
                    # Set content-type if not already set
                    if not event.datacontenttype:
                        headers.append(("content-type", b"application/json"))

            # Extract partition key from partitionkey extension
            key: bytes | None = None
            if "partitionkey" in event.extensions:
                partition_key = event.extensions["partitionkey"]
                key = str(partition_key).encode("utf-8")

            return KafkaMessage(value=value, headers=headers, key=key)

        except Exception as e:
            raise BindingError(
                f"Failed to convert event to Kafka binary mode: {e}",
                event_id=event.id,
            ) from e

    def from_binary(self, message: Mapping[str, Any]) -> CloudEvent:
        """
        Parse CloudEvent from Kafka binary content mode.

        Args:
            message: Kafka message dict with 'value' and 'headers' keys

        Returns:
            CloudEvent instance

        Raises:
            BindingError: If parsing fails
        """
        try:
            # Extract headers
            headers = message.get("headers", [])
            if not isinstance(headers, list):
                raise BindingError("Kafka message headers must be a list")

            # Convert headers list to dict (lowercase keys)
            headers_dict: dict[str, bytes] = {}
            for header in headers:
                if not isinstance(header, (tuple, list)) or len(header) != 2:
                    raise BindingError("Each Kafka header must be a (key, value) tuple")
                key, value = header
                if isinstance(value, str):
                    value = value.encode("utf-8")
                headers_dict[key.lower()] = value

            # Extract CloudEvents attributes
            event_attrs: dict[str, Any] = {}
            extensions: dict[str, str] = {}

            # Required attributes
            ce_id = headers_dict.get(f"{self.HEADER_PREFIX}id")
            if not ce_id:
                raise BindingError(f"Missing required header: {self.HEADER_PREFIX}id")
            event_attrs["id"] = ce_id.decode("utf-8")

            ce_source = headers_dict.get(f"{self.HEADER_PREFIX}source")
            if not ce_source:
                raise BindingError(
                    f"Missing required header: {self.HEADER_PREFIX}source"
                )
            event_attrs["source"] = ce_source.decode("utf-8")

            ce_type = headers_dict.get(f"{self.HEADER_PREFIX}type")
            if not ce_type:
                raise BindingError(f"Missing required header: {self.HEADER_PREFIX}type")
            event_attrs["type"] = ce_type.decode("utf-8")

            ce_specversion = headers_dict.get(f"{self.HEADER_PREFIX}specversion")
            if not ce_specversion:
                raise BindingError(
                    f"Missing required header: {self.HEADER_PREFIX}specversion"
                )
            event_attrs["specversion"] = ce_specversion.decode("utf-8")

            # Optional attributes
            ce_datacontenttype = headers_dict.get("content-type")
            if ce_datacontenttype:
                event_attrs["datacontenttype"] = ce_datacontenttype.decode("utf-8")

            ce_dataschema = headers_dict.get(f"{self.HEADER_PREFIX}dataschema")
            if ce_dataschema:
                event_attrs["dataschema"] = ce_dataschema.decode("utf-8")

            ce_subject = headers_dict.get(f"{self.HEADER_PREFIX}subject")
            if ce_subject:
                event_attrs["subject"] = ce_subject.decode("utf-8")

            ce_time = headers_dict.get(f"{self.HEADER_PREFIX}time")
            if ce_time:
                event_attrs["time"] = ce_time.decode("utf-8")

            # Extract extensions (any ce_* header not already processed)
            known_ce_headers = {
                f"{self.HEADER_PREFIX}id",
                f"{self.HEADER_PREFIX}source",
                f"{self.HEADER_PREFIX}type",
                f"{self.HEADER_PREFIX}specversion",
                f"{self.HEADER_PREFIX}dataschema",
                f"{self.HEADER_PREFIX}subject",
                f"{self.HEADER_PREFIX}time",
            }

            for header_name, header_value in headers_dict.items():
                if (
                    header_name.startswith(self.HEADER_PREFIX)
                    and header_name not in known_ce_headers
                ):
                    # Extension attribute
                    ext_name = header_name[len(self.HEADER_PREFIX) :]
                    extensions[ext_name] = header_value.decode("utf-8")

            # Handle message value (data)
            value = message.get("value")
            if value:
                if isinstance(value, str):
                    value_bytes = value.encode("utf-8")
                else:
                    value_bytes = value

                # Try to parse as JSON if content type suggests it
                datacontenttype = event_attrs.get("datacontenttype", "")
                if "json" in datacontenttype.lower():
                    import json

                    try:
                        event_attrs["data"] = json.loads(
                            value_bytes.decode("utf-8")
                        )
                    except (json.JSONDecodeError, UnicodeDecodeError):
                        # Fall back to string
                        event_attrs["data"] = value_bytes.decode(
                            "utf-8", errors="replace"
                        )
                else:
                    # Treat as string
                    event_attrs["data"] = value_bytes.decode(
                        "utf-8", errors="replace"
                    )

            # Create CloudEvent
            merged_attrs: Mapping[str, Any] = {**event_attrs, **extensions}
            return from_dict(merged_attrs)

        except BindingError:
            raise
        except Exception as e:
            raise BindingError(
                f"Failed to parse event from Kafka binary mode: {e}"
            ) from e

    def _get_content_type(self, serializer: EventSerializer) -> str:
        """
        Determine the content type for structured mode.

        Args:
            serializer: Event serializer

        Returns:
            Content type string (e.g., "application/cloudevents+json")
        """
        # Check if serializer has a content_type attribute
        if hasattr(serializer, "content_type"):
            return serializer.content_type  # type: ignore

        # Default to JSON if we can't determine
        return "application/cloudevents+json"

    def _validate_structured_headers(
        self, headers: list[tuple[str, bytes]] | list[tuple[str, str]]
    ) -> None:
        """
        Validate headers for structured mode.

        Args:
            headers: List of (key, value) tuples

        Raises:
            BindingError: If headers are invalid
        """
        # Convert to dict for lookup
        headers_dict: dict[str, str] = {}
        for header in headers:
            if not isinstance(header, (tuple, list)) or len(header) != 2:
                raise BindingError("Each header must be a (key, value) tuple")
            key, value = header
            if isinstance(value, bytes):
                value = value.decode("utf-8")
            headers_dict[key.lower()] = value

        # Check for content-type
        content_type = headers_dict.get("content-type")
        if not content_type:
            raise BindingError("content-type header is required for structured mode")

        # Validate it's a CloudEvents content type
        if not content_type.startswith("application/cloudevents"):
            raise BindingError(
                f"Invalid content-type for structured mode: {content_type}. "
                f"Expected application/cloudevents+*"
            )
