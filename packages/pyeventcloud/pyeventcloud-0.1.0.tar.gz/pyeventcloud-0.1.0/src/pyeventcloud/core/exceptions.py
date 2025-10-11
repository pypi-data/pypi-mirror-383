"""
Exception hierarchy for PyEventCloud.

This module defines all exceptions raised by the PyEventCloud library.
All exceptions inherit from CloudEventError, making it easy to catch
all library-specific errors.

Following the fail-fast philosophy, exceptions are raised immediately
when errors are detected, with clear messages about what went wrong.
"""


class CloudEventError(Exception):
    """
    Base exception for all CloudEvents library errors.

    All exceptions from this library inherit from this base class,
    making it easy to catch all library-specific errors.
    """

    pass


class ValidationError(CloudEventError):
    """
    Raised when event validation fails.

    This includes:
    - Missing required attributes
    - Invalid attribute values
    - Spec version compliance failures
    - Extension validation failures

    Attributes:
        attribute: Name of the attribute that failed validation (if applicable)
        spec_version: CloudEvents spec version being validated against
    """

    def __init__(
        self,
        message: str,
        *,
        attribute: str | None = None,
        spec_version: str | None = None
    ) -> None:
        super().__init__(message)
        self.attribute = attribute
        self.spec_version = spec_version


class SerializationError(CloudEventError):
    """
    Raised when event serialization fails.

    This includes:
    - JSON encoding failures
    - Unsupported data types in event data
    - Format-specific serialization issues

    Attributes:
        event_id: ID of the event that failed to serialize (for debugging)
    """

    def __init__(self, message: str, *, event_id: str | None = None) -> None:
        super().__init__(message)
        self.event_id = event_id


class DeserializationError(CloudEventError):
    """
    Raised when event deserialization fails.

    This includes:
    - Invalid JSON/format data
    - Missing required fields in serialized data
    - Format-specific deserialization issues
    """

    pass


class UnsupportedVersionError(CloudEventError):
    """
    Raised when an unsupported spec version is requested.

    Only versions "0.3" and "1.0" are supported.
    """

    def __init__(self, version: str) -> None:
        super().__init__(f"Unsupported CloudEvents spec version: {version}")
        self.version = version


class UnsupportedFormatError(CloudEventError):
    """
    Raised when an unsupported format is requested.

    Check available formats with FormatRegistry.
    """

    def __init__(self, format_name: str) -> None:
        super().__init__(f"Unsupported format: {format_name}")
        self.format_name = format_name


class ExtensionError(CloudEventError):
    """
    Raised when extension operations fail.

    This includes:
    - Extension validation failures
    - Invalid extension registration
    """

    pass


class BindingError(CloudEventError):
    """
    Raised when protocol binding operations fail.

    This includes:
    - HTTP binding conversion failures
    - Invalid headers or content in structured/binary modes
    - Protocol-specific binding issues

    Attributes:
        event_id: ID of the event that failed (for debugging)
    """

    def __init__(self, message: str, *, event_id: str | None = None) -> None:
        super().__init__(message)
        self.event_id = event_id
