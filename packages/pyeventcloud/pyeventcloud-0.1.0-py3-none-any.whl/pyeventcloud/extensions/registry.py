"""
CloudEvents extension registry.

This module provides a registry for managing CloudEvents extensions.
Extensions can be registered, validated, and queried through the registry.
"""

from collections.abc import Mapping
from typing import Any, Protocol

from pyeventcloud.core.exceptions import ExtensionError


class Extension(Protocol):
    """
    Protocol defining the Extension interface.

    Extensions must implement this protocol to be registered and used
    with CloudEvents.
    """

    name: str
    attributes: Mapping[str, type]

    def validate(self, event: Any) -> None:
        """
        Validate extension attributes on an event.

        Args:
            event: CloudEvent to validate

        Raises:
            ValidationError: If extension attributes are invalid
        """
        ...

    def get_attributes(self, event: Any) -> Mapping[str, Any]:
        """
        Get extension attributes from an event.

        Args:
            event: CloudEvent to extract attributes from

        Returns:
            Dictionary of extension attributes
        """
        ...


class ExtensionRegistry:
    """
    Registry for CloudEvents extensions.

    Manages registration and retrieval of extensions. Ensures extension
    names are unique and provides validation capabilities.
    """

    def __init__(self) -> None:
        """Initialize an empty extension registry."""
        self._extensions: dict[str, Extension] = {}

    def register(self, extension: Extension) -> None:
        """
        Register an extension.

        Args:
            extension: Extension to register

        Raises:
            ExtensionError: If extension name is already registered or invalid
        """
        if not hasattr(extension, "name") or not extension.name:
            raise ExtensionError("Extension must have a non-empty name")

        if not isinstance(extension.name, str):
            raise ExtensionError("Extension name must be a string")

        if extension.name in self._extensions:
            raise ExtensionError(f"Extension '{extension.name}' is already registered")

        if not hasattr(extension, "attributes"):
            raise ExtensionError(f"Extension '{extension.name}' must define attributes")

        if not hasattr(extension, "validate"):
            raise ExtensionError(f"Extension '{extension.name}' must implement validate method")

        if not hasattr(extension, "get_attributes"):
            raise ExtensionError(f"Extension '{extension.name}' must implement get_attributes method")

        self._extensions[extension.name] = extension

    def unregister(self, name: str) -> None:
        """
        Unregister an extension by name.

        Args:
            name: Extension name to unregister

        Raises:
            ExtensionError: If extension is not registered
        """
        if name not in self._extensions:
            raise ExtensionError(f"Extension '{name}' is not registered")

        del self._extensions[name]

    def get(self, name: str) -> Extension:
        """
        Get extension by name.

        Args:
            name: Extension name

        Returns:
            Extension instance

        Raises:
            ExtensionError: If extension is not found
        """
        if name not in self._extensions:
            raise ExtensionError(f"Extension '{name}' is not registered")

        return self._extensions[name]

    def has(self, name: str) -> bool:
        """
        Check if extension is registered.

        Args:
            name: Extension name

        Returns:
            True if extension is registered, False otherwise
        """
        return name in self._extensions

    def list_extensions(self) -> list[str]:
        """
        Get list of registered extension names.

        Returns:
            List of extension names (sorted alphabetically)
        """
        return sorted(self._extensions.keys())

    def validate_event(self, event: Any) -> None:
        """
        Validate all registered extensions on an event.

        Validates each registered extension against the event. Uses fail-fast
        approach: stops at first validation error.

        Args:
            event: CloudEvent to validate

        Raises:
            ValidationError: If any extension validation fails
        """
        if not hasattr(event, "extensions") or not event.extensions:
            return  # No extensions to validate

        for ext_name, extension in self._extensions.items():
            # Only validate if extension attributes are present on the event
            if any(attr in event.extensions for attr in extension.attributes.keys()):
                extension.validate(event)

    def get_event_extensions(self, event: Any) -> dict[str, Mapping[str, Any]]:
        """
        Get all extension attributes from an event.

        Args:
            event: CloudEvent to extract extensions from

        Returns:
            Dictionary mapping extension names to their attributes
        """
        result: dict[str, Mapping[str, Any]] = {}

        for ext_name, extension in self._extensions.items():
            attrs = extension.get_attributes(event)
            if attrs:
                result[ext_name] = attrs

        return result


# Global registry instance
_global_registry = ExtensionRegistry()


def register_extension(extension: Extension) -> None:
    """
    Register extension in the global registry.

    Args:
        extension: Extension to register

    Raises:
        ExtensionError: If registration fails
    """
    _global_registry.register(extension)


def unregister_extension(name: str) -> None:
    """
    Unregister extension from the global registry.

    Args:
        name: Extension name to unregister

    Raises:
        ExtensionError: If extension is not registered
    """
    _global_registry.unregister(name)


def get_extension(name: str) -> Extension:
    """
    Get extension from the global registry.

    Args:
        name: Extension name

    Returns:
        Extension instance

    Raises:
        ExtensionError: If extension is not found
    """
    return _global_registry.get(name)


def has_extension(name: str) -> bool:
    """
    Check if extension is registered in the global registry.

    Args:
        name: Extension name

    Returns:
        True if extension is registered, False otherwise
    """
    return _global_registry.has(name)


def list_extensions() -> list[str]:
    """
    Get list of registered extension names from the global registry.

    Returns:
        List of extension names (sorted alphabetically)
    """
    return _global_registry.list_extensions()


def get_global_registry() -> ExtensionRegistry:
    """
    Get the global extension registry instance.

    Returns:
        Global ExtensionRegistry instance
    """
    return _global_registry


# Auto-register built-in extensions
def _register_builtin_extensions() -> None:
    """Register built-in extensions on module import."""
    from pyeventcloud.extensions.partitionkey import PartitioningExtension

    try:
        register_extension(PartitioningExtension())
    except ExtensionError:
        # Already registered, ignore
        pass


# Register built-in extensions when module is imported
_register_builtin_extensions()
