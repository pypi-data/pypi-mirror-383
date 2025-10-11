"""
CloudEvents 1.0 specification implementation.

This module provides the CloudEventSpecV10 class that validates CloudEvents
against the CloudEvents 1.0 specification. It ensures compliance with required
and optional attributes as defined in the spec.

Specification Reference:
    https://github.com/cloudevents/spec/blob/v1.0.2/cloudevents/spec.md
"""

from typing import Any, Protocol

from pyeventcloud.core.exceptions import ValidationError
from pyeventcloud.utils.types import SpecVersion
from pyeventcloud.validation.validators import ValidatorRegistry


class CloudEvent(Protocol):
    """
    Protocol defining the CloudEvent interface.

    This protocol allows type-safe validation without requiring
    a concrete CloudEvent class implementation.
    """

    id: str
    source: str
    specversion: str
    type: str
    datacontenttype: str | None
    dataschema: str | None
    subject: str | None
    time: Any  # Can be str or datetime
    data: Any
    data_base64: str | None


class CloudEventSpecV10:
    """
    CloudEvents 1.0 specification implementation.

    Validates CloudEvents against the CloudEvents 1.0 specification,
    ensuring all required attributes are present and correctly formatted,
    and that optional attributes (when present) are valid.

    Attributes:
        version: CloudEvents specification version ("1.0")
        REQUIRED_ATTRIBUTES: Set of required attribute names
        OPTIONAL_ATTRIBUTES: Set of optional attribute names
    """

    version: SpecVersion = "1.0"
    REQUIRED_ATTRIBUTES: frozenset[str] = frozenset({
        "id", "source", "specversion", "type"
    })
    OPTIONAL_ATTRIBUTES: frozenset[str] = frozenset({
        "datacontenttype", "dataschema", "subject", "time", "data", "data_base64"
    })

    def __init__(self, validator_registry: ValidatorRegistry) -> None:
        """
        Initialize the CloudEvents 1.0 spec validator.

        Args:
            validator_registry: Registry containing attribute validators
        """
        self.validators = validator_registry

    def validate(self, event: CloudEvent) -> None:
        """
        Validate event against CloudEvents 1.0 spec.

        Performs fail-fast validation, raising ValidationError on the first
        error encountered. Validates:
        - All required attributes are present and non-empty
        - specversion is exactly "1.0"
        - Required attributes have correct types and formats
        - Optional attributes (when present) have correct types and formats
        - Mutual exclusivity of data and data_base64

        Args:
            event: CloudEvent to validate

        Raises:
            ValidationError: If validation fails (fail-fast on first error)
        """
        # Check all required attributes are present and non-empty
        for attr in self.REQUIRED_ATTRIBUTES:
            value = getattr(event, attr, None)
            if value is None or (isinstance(value, str) and not value):
                raise ValidationError(
                    f"Required attribute '{attr}' is missing or empty",
                    attribute=attr,
                    spec_version="1.0"
                )

        # Validate specversion
        if event.specversion != "1.0":
            raise ValidationError(
                f"specversion must be '1.0', got '{event.specversion}'",
                attribute="specversion",
                spec_version="1.0"
            )

        # Validate required attribute types
        self.validators.validate("string", event.id, "id")
        self.validators.validate("uri", event.source, "source")
        self.validators.validate("string", event.type, "type")

        # Validate optional attributes if present
        if event.datacontenttype:
            self.validators.validate(
                "mediatype", event.datacontenttype, "datacontenttype"
            )

        if event.dataschema:
            self.validators.validate("uri", event.dataschema, "dataschema")

        if event.time:
            self.validators.validate("timestamp", event.time, "time")

        # Validate mutual exclusivity of data and data_base64
        if event.data is not None and event.data_base64 is not None:
            raise ValidationError(
                "Cannot specify both 'data' and 'data_base64'",
                spec_version="1.0"
            )

    def get_required_attributes(self) -> frozenset[str]:
        """
        Get the set of required attributes for CloudEvents 1.0.

        Returns:
            Immutable set of required attribute names
        """
        return self.REQUIRED_ATTRIBUTES

    def get_optional_attributes(self) -> frozenset[str]:
        """
        Get the set of optional attributes for CloudEvents 1.0.

        Returns:
            Immutable set of optional attribute names
        """
        return self.OPTIONAL_ATTRIBUTES
