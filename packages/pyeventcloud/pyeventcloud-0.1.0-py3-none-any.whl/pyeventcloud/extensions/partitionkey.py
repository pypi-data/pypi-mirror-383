"""
CloudEvents Partitioning extension.

This module implements the partitionkey extension as defined in the
CloudEvents Partitioning Extension specification.

The partitionkey extension allows events to be partitioned for distributed
processing systems like Kafka or Kinesis.
"""

from typing import Any, Mapping

from pyeventcloud.core.exceptions import ValidationError


class PartitioningExtension:
    """
    CloudEvents Partitioning extension (partitionkey).

    The partitionkey extension is optional and provides a hint for routing
    and partitioning events in distributed systems.

    Attributes:
        name: Extension name ("partitionkey")
        attributes: Mapping of extension attribute names to their types
    """

    name: str = "partitionkey"
    attributes: Mapping[str, type] = {"partitionkey": str}

    def validate(self, event: Any) -> None:
        """
        Validate partitionkey extension on an event.

        Args:
            event: CloudEvent object to validate

        Raises:
            ValidationError: If partitionkey is present but invalid
        """
        partitionkey = event.extensions.get("partitionkey")

        if partitionkey is None:
            return  # Optional extension

        if not isinstance(partitionkey, str):
            raise ValidationError("partitionkey must be a string")

        if not partitionkey:
            raise ValidationError("partitionkey cannot be empty")

    def get_attributes(self, event: Any) -> Mapping[str, Any]:
        """
        Get partitionkey attribute from event.

        Args:
            event: CloudEvent object

        Returns:
            Dictionary with partitionkey if present, empty dict otherwise
        """
        partitionkey = event.extensions.get("partitionkey")
        return {"partitionkey": partitionkey} if partitionkey else {}

    def set_partitionkey(self, event: Any, key: str) -> None:
        """
        Set partitionkey on event.

        Args:
            event: CloudEvent object
            key: Partition key value

        Raises:
            ValueError: If key is not a non-empty string
        """
        if not isinstance(key, str) or not key:
            raise ValueError("partitionkey must be a non-empty string")
        event.extensions["partitionkey"] = key
