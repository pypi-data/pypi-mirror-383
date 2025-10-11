"""
Validator implementations for PyEventCloud.

This module provides validators for CloudEvents attributes according to
the CloudEvents specification. All validators follow the fail-fast principle,
raising ValidationError immediately when validation fails.

Validators:
    - StringValidator: Validates non-empty strings
    - URIValidator: Validates URI-references per RFC 3986
    - RFC3339Validator: Validates RFC 3339 timestamps
    - MediaTypeValidator: Validates RFC 2046 media types
    - AttributeNameValidator: Validates extension attribute names
"""

import re
from datetime import datetime
from typing import Any, Dict, Optional
from urllib.parse import urlparse

from pyeventcloud.core.exceptions import ValidationError


class StringValidator:
    """
    Validates string attributes.

    Ensures the value is a non-empty string.
    """

    def validate(self, value: Any, attribute_name: str) -> None:
        """
        Validate that value is a non-empty string.

        Args:
            value: Value to validate
            attribute_name: Name of the attribute being validated

        Raises:
            ValidationError: If value is not a string or is empty
        """
        if not isinstance(value, str):
            raise ValidationError(
                f"{attribute_name} must be a string",
                attribute=attribute_name
            )
        if not value:
            raise ValidationError(
                f"{attribute_name} cannot be empty",
                attribute=attribute_name
            )


class URIValidator:
    """
    Validates URI-reference attributes per RFC 3986.

    A URI-reference can be an absolute URI or a relative reference.
    Uses urllib.parse.urlparse for validation.
    """

    def validate(self, value: Any, attribute_name: str) -> None:
        """
        Validate that value is a valid URI-reference.

        Args:
            value: Value to validate
            attribute_name: Name of the attribute being validated

        Raises:
            ValidationError: If value is not a valid URI-reference
        """
        if not isinstance(value, str):
            raise ValidationError(
                f"{attribute_name} must be a string",
                attribute=attribute_name
            )

        # Basic URI validation using urllib
        try:
            result = urlparse(value)
            # URI-reference can be relative, so we don't require scheme
            # But it must have at least a path or netloc component
            if not result.path and not result.netloc:
                raise ValidationError(
                    f"{attribute_name} must be a valid URI-reference",
                    attribute=attribute_name
                )
        except Exception as e:
            raise ValidationError(
                f"{attribute_name} is not a valid URI-reference: {e}",
                attribute=attribute_name
            )


class RFC3339Validator:
    """
    Validates RFC 3339 timestamp attributes.

    Accepts both datetime objects and RFC 3339 formatted strings.
    RFC 3339 format: YYYY-MM-DDTHH:MM:SS[.fraction](Z|+HH:MM|-HH:MM)
    """

    # Regex pattern for RFC 3339 timestamps
    # Matches: 2024-03-15T14:30:00Z or 2024-03-15T14:30:00.123456+01:00
    RFC3339_PATTERN = re.compile(
        r'^\d{4}-\d{2}-\d{2}[T\s]\d{2}:\d{2}:\d{2}(\.\d+)?(Z|[+-]\d{2}:\d{2})$'
    )

    def validate(self, value: Any, attribute_name: str) -> None:
        """
        Validate that value is a valid RFC 3339 timestamp.

        Args:
            value: Value to validate (datetime object or string)
            attribute_name: Name of the attribute being validated

        Raises:
            ValidationError: If value is not a valid RFC 3339 timestamp
        """
        if isinstance(value, datetime):
            return  # datetime objects are valid

        if not isinstance(value, str):
            raise ValidationError(
                f"{attribute_name} must be a string or datetime",
                attribute=attribute_name
            )

        if not self.RFC3339_PATTERN.match(value):
            raise ValidationError(
                f"{attribute_name} must be a valid RFC 3339 timestamp",
                attribute=attribute_name
            )


class MediaTypeValidator:
    """
    Validates RFC 2046 media type attributes.

    Validates media types (MIME types) in the format: type/subtype[; param=value]*
    Examples: application/json, text/plain; charset=utf-8
    """

    # Regex pattern for RFC 2046 media types
    # Matches: type/subtype with optional parameters
    MEDIA_TYPE_PATTERN = re.compile(
        r'^[a-zA-Z0-9][a-zA-Z0-9!#$&\-^_+.]*/'
        r'[a-zA-Z0-9][a-zA-Z0-9!#$&\-^_+.]*'
        r'(\s*;\s*[a-zA-Z0-9\-]+=[^\s;]+)*$'
    )

    def validate(self, value: Any, attribute_name: str) -> None:
        """
        Validate that value is a valid media type.

        Args:
            value: Value to validate
            attribute_name: Name of the attribute being validated

        Raises:
            ValidationError: If value is not a valid media type
        """
        if not isinstance(value, str):
            raise ValidationError(
                f"{attribute_name} must be a string",
                attribute=attribute_name
            )

        if not self.MEDIA_TYPE_PATTERN.match(value):
            raise ValidationError(
                f"{attribute_name} must be a valid media type",
                attribute=attribute_name
            )


class AttributeNameValidator:
    """
    Validates extension attribute names.

    Version 0.3 rules:
        - Only lowercase letters and digits
        - Recommended maximum length of 20 characters

    Version 1.0 rules:
        - More relaxed naming (currently same validation as 0.3 for consistency)
    """

    def __init__(self, max_length: int = 20, version: str = "1.0") -> None:
        """
        Initialize the attribute name validator.

        Args:
            max_length: Maximum recommended length for attribute names
            version: CloudEvents spec version ("0.3" or "1.0")
        """
        self.max_length = max_length
        self.version = version

    def validate(self, value: Any, attribute_name: str) -> None:
        """
        Validate that value is a valid attribute name.

        Args:
            value: Value to validate (the attribute name itself)
            attribute_name: Context name for error messages

        Raises:
            ValidationError: If value is not a valid attribute name
        """
        if not isinstance(value, str):
            raise ValidationError("Attribute name must be a string")

        # Version 0.3 specific rules
        if self.version == "0.3":
            if not re.match(r'^[a-z0-9]+$', value):
                raise ValidationError(
                    f"Attribute name '{value}' must contain only lowercase "
                    f"letters and digits (v0.3)"
                )
            if len(value) > self.max_length:
                raise ValidationError(
                    f"Attribute name '{value}' exceeds recommended length "
                    f"of {self.max_length}"
                )
        # Version 1.0 uses similar rules for consistency
        else:
            if not re.match(r'^[a-z0-9]+$', value):
                raise ValidationError(
                    f"Attribute name '{value}' must contain only lowercase "
                    f"letters and digits"
                )
            if len(value) > self.max_length:
                raise ValidationError(
                    f"Attribute name '{value}' exceeds recommended length "
                    f"of {self.max_length}"
                )


class ValidatorRegistry:
    """
    Registry for attribute validators.

    Provides a centralized registry for managing validators and
    validating values using named validators.
    """

    def __init__(self) -> None:
        """Initialize the validator registry with default validators."""
        self._validators: Dict[str, Any] = {}
        self._register_defaults()

    def _register_defaults(self) -> None:
        """Register default validators for common attribute types."""
        self.register("string", StringValidator())
        self.register("uri", URIValidator())
        self.register("timestamp", RFC3339Validator())
        self.register("mediatype", MediaTypeValidator())

    def register(self, name: str, validator: Any) -> None:
        """
        Register a validator with a given name.

        Args:
            name: Name to register the validator under
            validator: Validator instance (must have validate method)
        """
        self._validators[name] = validator

    def get(self, name: str) -> Optional[Any]:
        """
        Get a validator by name.

        Args:
            name: Name of the validator to retrieve

        Returns:
            Validator instance or None if not found
        """
        return self._validators.get(name)

    def validate(self, validator_name: str, value: Any, attribute_name: str) -> None:
        """
        Validate a value using a named validator.

        Convenience method that looks up the validator and calls its validate method.

        Args:
            validator_name: Name of the validator to use
            value: Value to validate
            attribute_name: Name of the attribute being validated

        Raises:
            ValueError: If validator is not found
            ValidationError: If validation fails
        """
        validator = self.get(validator_name)
        if validator is None:
            raise ValueError(f"Unknown validator: {validator_name}")
        validator.validate(value, attribute_name)
