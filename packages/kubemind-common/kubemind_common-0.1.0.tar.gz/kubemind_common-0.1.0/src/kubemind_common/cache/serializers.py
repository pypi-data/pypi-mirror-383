"""Cache value serializers."""
from __future__ import annotations

import json
import pickle
from abc import ABC, abstractmethod
from typing import Any


class Serializer(ABC):
    """Base serializer interface."""

    @abstractmethod
    def serialize(self, value: Any) -> bytes:
        """Serialize value to bytes.

        Args:
            value: Value to serialize

        Returns:
            Serialized bytes
        """
        pass

    @abstractmethod
    def deserialize(self, data: bytes) -> Any:
        """Deserialize bytes to value.

        Args:
            data: Serialized bytes

        Returns:
            Deserialized value
        """
        pass


class JSONSerializer(Serializer):
    """JSON serializer (human-readable, language-agnostic).

    Best for: Simple data types, cross-language compatibility.
    Limitations: Cannot serialize arbitrary Python objects.
    """

    def serialize(self, value: Any) -> bytes:
        """Serialize value to JSON bytes.

        Args:
            value: Value to serialize (must be JSON-serializable)

        Returns:
            JSON bytes
        """
        return json.dumps(value).encode("utf-8")

    def deserialize(self, data: bytes) -> Any:
        """Deserialize JSON bytes to value.

        Args:
            data: JSON bytes

        Returns:
            Deserialized value
        """
        return json.loads(data.decode("utf-8"))


class PickleSerializer(Serializer):
    """Pickle serializer (Python-specific, supports complex objects).

    Best for: Complex Python objects, faster than JSON.
    Limitations: Python-only, security concerns with untrusted data.
    """

    def serialize(self, value: Any) -> bytes:
        """Serialize value using pickle.

        Args:
            value: Value to serialize

        Returns:
            Pickled bytes
        """
        return pickle.dumps(value)

    def deserialize(self, data: bytes) -> Any:
        """Deserialize pickled bytes to value.

        Args:
            data: Pickled bytes

        Returns:
            Deserialized value
        """
        return pickle.loads(data)


class StringSerializer(Serializer):
    """String serializer (no transformation, for string-only values)."""

    def serialize(self, value: Any) -> bytes:
        """Serialize string to bytes.

        Args:
            value: String value

        Returns:
            UTF-8 encoded bytes
        """
        if not isinstance(value, str):
            raise ValueError(f"StringSerializer requires str, got {type(value)}")
        return value.encode("utf-8")

    def deserialize(self, data: bytes) -> str:
        """Deserialize bytes to string.

        Args:
            data: UTF-8 bytes

        Returns:
            String value
        """
        return data.decode("utf-8")
