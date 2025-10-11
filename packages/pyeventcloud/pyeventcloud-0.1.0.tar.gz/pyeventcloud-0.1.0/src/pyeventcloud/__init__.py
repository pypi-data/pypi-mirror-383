"""
PyEventCloud - CloudEvents SDK for Python.

This library provides a complete implementation of the CloudEvents specification
for Python, including support for multiple spec versions, formats, and protocol bindings.
"""

# Core
from pyeventcloud.core.event import CloudEvent, create_event, from_dict
from pyeventcloud.core.exceptions import (
    BindingError,
    CloudEventError,
    DeserializationError,
    ExtensionError,
    SerializationError,
    UnsupportedFormatError,
    UnsupportedVersionError,
    ValidationError,
)

# Formats
from pyeventcloud.formats.json import (
    JSONFormatter,
    from_json,
    from_json_batch,
    to_json,
    to_json_batch,
)

# Bindings
from pyeventcloud.bindings.http import EventSerializer, HTTPBinding
from pyeventcloud.bindings.kafka import KafkaBinding, KafkaMessage

# Extensions
from pyeventcloud.extensions.partitionkey import PartitioningExtension
from pyeventcloud.extensions.registry import (
    Extension,
    ExtensionRegistry,
    get_extension,
    get_global_registry,
    has_extension,
    list_extensions,
    register_extension,
    unregister_extension,
)

# Specs
from pyeventcloud.specs.spec_v10 import CloudEventSpecV10

# Validation
from pyeventcloud.validation.validators import ValidatorRegistry

# Types
from pyeventcloud.utils.types import CloudEventDict, SpecVersion

__version__ = "0.1.0"

__all__ = [
    # Core
    "CloudEvent",
    "create_event",
    "from_dict",
    # Exceptions
    "CloudEventError",
    "ValidationError",
    "SerializationError",
    "DeserializationError",
    "UnsupportedVersionError",
    "UnsupportedFormatError",
    "ExtensionError",
    "BindingError",
    # Formats
    "JSONFormatter",
    "to_json",
    "from_json",
    "to_json_batch",
    "from_json_batch",
    # Bindings
    "HTTPBinding",
    "KafkaBinding",
    "EventSerializer",
    "KafkaMessage",
    # Extensions
    "Extension",
    "ExtensionRegistry",
    "PartitioningExtension",
    "register_extension",
    "unregister_extension",
    "get_extension",
    "has_extension",
    "list_extensions",
    "get_global_registry",
    # Specs
    "CloudEventSpecV10",
    # Validation
    "ValidatorRegistry",
    # Types
    "CloudEventDict",
    "SpecVersion",
]
