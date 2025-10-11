"""CloudEvents extensions."""

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

__all__ = [
    "Extension",
    "ExtensionRegistry",
    "PartitioningExtension",
    "register_extension",
    "unregister_extension",
    "get_extension",
    "has_extension",
    "list_extensions",
    "get_global_registry",
]
