"""
CloudEvents HTTP protocol binding.

This module implements the CloudEvents HTTP protocol binding for both
structured and binary content modes. The binding is format-agnostic and
uses a Protocol-based interface for serialization.

Reference: https://github.com/cloudevents/spec/blob/v1.0.2/cloudevents/bindings/http-protocol-binding.md
"""

from collections.abc import Mapping
from typing import Protocol, Any

from pyeventcloud.core.event import CloudEvent, from_dict
from pyeventcloud.core.exceptions import BindingError


class EventSerializer(Protocol):
    """
    Protocol for event serializers.

    This defines the interface that any format implementation must provide
    to be used with the HTTP binding. This decouples the binding from
    specific format implementations.
    """

    def serialize(self, event: CloudEvent) -> str:
        """
        Serialize a CloudEvent to string format.

        Args:
            event: CloudEvent to serialize

        Returns:
            Serialized event as string
        """
        ...

    def deserialize(self, data: str) -> CloudEvent:
        """
        Deserialize string data to CloudEvent.

        Args:
            data: Serialized event data

        Returns:
            CloudEvent instance
        """
        ...


class HTTPBinding:
    """
    CloudEvents HTTP protocol binding.

    Implements both structured and binary content modes for HTTP transport.
    The binding is format-agnostic through the EventSerializer protocol.
    """

    # HTTP header prefix for binary mode
    BINARY_HEADERS_PREFIX = "ce-"

    # CloudEvents content type for structured mode (format-specific)
    STRUCTURED_CONTENT_TYPE_PREFIX = "application/cloudevents"

    def to_structured(
        self,
        event: CloudEvent,
        serializer: EventSerializer,
    ) -> tuple[bytes, dict[str, str]]:
        """
        Convert CloudEvent to HTTP structured content mode.

        In structured mode, the event is serialized in the request body with
        a content-type indicating CloudEvents format (e.g., application/cloudevents+json).

        Args:
            event: CloudEvent to convert
            serializer: Serializer to use for event serialization

        Returns:
            Tuple of (body bytes, headers dict)

        Raises:
            BindingError: If conversion fails
        """
        try:
            serialized = serializer.serialize(event)
            body = serialized.encode("utf-8")

            # Infer content type from serializer
            content_type = self._get_content_type(serializer)

            headers = {
                "Content-Type": content_type,
            }

            return body, headers

        except Exception as e:
            raise BindingError(
                f"Failed to convert event to structured mode: {e}",
                event_id=event.id,
            ) from e

    def from_structured(
        self,
        body: bytes | str,
        headers: Mapping[str, str],
        serializer: EventSerializer,
    ) -> CloudEvent:
        """
        Parse CloudEvent from HTTP structured content mode.

        Args:
            body: HTTP request body
            headers: HTTP request headers
            serializer: Serializer to use for deserialization

        Returns:
            CloudEvent instance

        Raises:
            BindingError: If parsing fails
        """
        # Validate content type
        content_type = headers.get("Content-Type") or headers.get("content-type")
        if not content_type:
            raise BindingError("Content-Type header is required for structured mode")

        if not self._is_cloudevents_content_type(content_type):
            raise BindingError(
                f"Invalid Content-Type for structured mode: {content_type}. "
                f"Expected application/cloudevents+*"
            )

        # Decode body if bytes
        if isinstance(body, bytes):
            try:
                body_str = body.decode("utf-8")
            except UnicodeDecodeError as e:
                raise BindingError(f"Failed to decode body as UTF-8: {e}") from e
        else:
            body_str = body

        try:
            return serializer.deserialize(body_str)
        except Exception as e:
            raise BindingError(f"Failed to parse event from structured mode: {e}") from e

    def to_binary(self, event: CloudEvent) -> tuple[bytes, dict[str, str]]:
        """
        Convert CloudEvent to HTTP binary content mode.

        In binary mode, CloudEvents attributes are mapped to HTTP headers with
        the "ce-" prefix, and the event data is placed in the request body.

        Args:
            event: CloudEvent to convert

        Returns:
            Tuple of (body bytes, headers dict)

        Raises:
            BindingError: If conversion fails
        """
        try:
            headers: dict[str, str] = {}

            # Required attributes
            headers[f"{self.BINARY_HEADERS_PREFIX}id"] = event.id
            headers[f"{self.BINARY_HEADERS_PREFIX}source"] = event.source
            headers[f"{self.BINARY_HEADERS_PREFIX}type"] = event.type
            headers[f"{self.BINARY_HEADERS_PREFIX}specversion"] = event.specversion

            # Optional attributes
            if event.datacontenttype:
                headers["Content-Type"] = event.datacontenttype

            if event.dataschema:
                headers[f"{self.BINARY_HEADERS_PREFIX}dataschema"] = event.dataschema

            if event.subject:
                headers[f"{self.BINARY_HEADERS_PREFIX}subject"] = event.subject

            if event.time:
                # Format as RFC 3339
                time_str = event.time.isoformat().replace("+00:00", "Z")
                headers[f"{self.BINARY_HEADERS_PREFIX}time"] = time_str

            # Extensions
            for ext_name, ext_value in event.extensions.items():
                headers[f"{self.BINARY_HEADERS_PREFIX}{ext_name}"] = str(ext_value)

            # Handle body (data or data_base64)
            body = b""
            if event.data_base64:
                # Binary data - decode from base64
                import base64

                body = base64.b64decode(event.data_base64)
            elif event.data is not None:
                # Text/structured data - serialize to JSON
                import json

                if isinstance(event.data, (str, int, float, bool)):
                    # Scalar values - convert to string
                    body = str(event.data).encode("utf-8")
                else:
                    # Complex data - JSON serialize
                    body = json.dumps(event.data, ensure_ascii=False).encode("utf-8")
                    if not event.datacontenttype:
                        headers["Content-Type"] = "application/json"

            return body, headers

        except Exception as e:
            raise BindingError(
                f"Failed to convert event to binary mode: {e}",
                event_id=event.id,
            ) from e

    def from_binary(
        self,
        body: bytes | str,
        headers: Mapping[str, str],
    ) -> CloudEvent:
        """
        Parse CloudEvent from HTTP binary content mode.

        Args:
            body: HTTP request body
            headers: HTTP request headers

        Returns:
            CloudEvent instance

        Raises:
            BindingError: If parsing fails
        """
        try:
            # Extract CloudEvents attributes from headers
            event_attrs: dict[str, Any] = {}
            extensions: dict[str, str] = {}

            # Normalize header names (case-insensitive)
            normalized_headers = {k.lower(): v for k, v in headers.items()}

            # Required attributes
            ce_id = normalized_headers.get(f"{self.BINARY_HEADERS_PREFIX}id")
            if not ce_id:
                raise BindingError("Missing required header: ce-id")
            event_attrs["id"] = ce_id

            ce_source = normalized_headers.get(f"{self.BINARY_HEADERS_PREFIX}source")
            if not ce_source:
                raise BindingError("Missing required header: ce-source")
            event_attrs["source"] = ce_source

            ce_type = normalized_headers.get(f"{self.BINARY_HEADERS_PREFIX}type")
            if not ce_type:
                raise BindingError("Missing required header: ce-type")
            event_attrs["type"] = ce_type

            ce_specversion = normalized_headers.get(
                f"{self.BINARY_HEADERS_PREFIX}specversion"
            )
            if not ce_specversion:
                raise BindingError("Missing required header: ce-specversion")
            event_attrs["specversion"] = ce_specversion

            # Optional attributes
            ce_datacontenttype = normalized_headers.get("content-type")
            if ce_datacontenttype:
                event_attrs["datacontenttype"] = ce_datacontenttype

            ce_dataschema = normalized_headers.get(
                f"{self.BINARY_HEADERS_PREFIX}dataschema"
            )
            if ce_dataschema:
                event_attrs["dataschema"] = ce_dataschema

            ce_subject = normalized_headers.get(f"{self.BINARY_HEADERS_PREFIX}subject")
            if ce_subject:
                event_attrs["subject"] = ce_subject

            ce_time = normalized_headers.get(f"{self.BINARY_HEADERS_PREFIX}time")
            if ce_time:
                event_attrs["time"] = ce_time

            # Extract extensions (any ce-* header not already processed)
            known_ce_headers = {
                f"{self.BINARY_HEADERS_PREFIX}id",
                f"{self.BINARY_HEADERS_PREFIX}source",
                f"{self.BINARY_HEADERS_PREFIX}type",
                f"{self.BINARY_HEADERS_PREFIX}specversion",
                f"{self.BINARY_HEADERS_PREFIX}dataschema",
                f"{self.BINARY_HEADERS_PREFIX}subject",
                f"{self.BINARY_HEADERS_PREFIX}time",
            }

            for header_name, header_value in normalized_headers.items():
                if (
                    header_name.startswith(self.BINARY_HEADERS_PREFIX)
                    and header_name not in known_ce_headers
                ):
                    # Extension attribute
                    ext_name = header_name[len(self.BINARY_HEADERS_PREFIX) :]
                    extensions[ext_name] = header_value

            # Handle body
            if body:
                if isinstance(body, str):
                    body_bytes = body.encode("utf-8")
                else:
                    body_bytes = body

                # Try to parse as JSON if content type suggests it
                if ce_datacontenttype and "json" in ce_datacontenttype.lower():
                    import json

                    try:
                        event_attrs["data"] = json.loads(body_bytes.decode("utf-8"))
                    except (json.JSONDecodeError, UnicodeDecodeError):
                        # Fall back to string
                        event_attrs["data"] = body_bytes.decode("utf-8", errors="replace")
                else:
                    # Treat as string
                    event_attrs["data"] = body_bytes.decode("utf-8", errors="replace")

            # Create CloudEvent - merge attributes and extensions
            merged_attrs: Mapping[str, Any] = {**event_attrs, **extensions}
            return from_dict(merged_attrs)

        except BindingError:
            raise
        except Exception as e:
            raise BindingError(f"Failed to parse event from binary mode: {e}") from e

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

    def _is_cloudevents_content_type(self, content_type: str) -> bool:
        """
        Check if content type is a valid CloudEvents structured mode type.

        Args:
            content_type: Content-Type header value

        Returns:
            True if valid CloudEvents content type
        """
        # Remove parameters (e.g., charset)
        base_type = content_type.split(";")[0].strip().lower()

        return base_type.startswith("application/cloudevents")
