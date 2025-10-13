"""
ObjectId implementation for NeoSQLite that follows MongoDB's specification.

Based on MongoDB's ObjectId specification:
- 4 bytes: timestamp (seconds since Unix epoch)
- 5 bytes: random value (generated once per process)
- 3 bytes: counter (incrementing from a random value)

This implementation provides full compatibility with MongoDB ObjectIds
while being optimized for NeoSQLite's local-only architecture.
"""

from __future__ import annotations
from typing import Any, TYPE_CHECKING
import os
import random
import threading
import time

if TYPE_CHECKING:
    pass


class ObjectId:
    """
    A MongoDB-compatible ObjectId implementation for NeoSQLite.

    This class generates 12-byte identifiers following MongoDB's specification:
    - 4 bytes: timestamp (seconds since Unix epoch)
    - 5 bytes: random value (generated once per process)
    - 3 bytes: counter (incrementing from a random value)

    Provides full compatibility with MongoDB ObjectIds while working with NeoSQLite.
    """

    _random_bytes: bytes | None = None
    _counter: int | None = None
    _counter_lock = threading.Lock()

    def __init__(self, oid: str | bytes | ObjectId | int | None = None):
        """
        Initialize a new ObjectId.

        Args:
            oid: Can be a 12-byte binary representation, a 24-character hex string,
                 another ObjectId instance, an integer (which replaces the timestamp),
                 or None to generate a new ObjectId.

        Raises:
            TypeError: If the input type is not supported
            ValueError: If the input format is invalid
        """
        if oid is None:
            # Generate a new ObjectId
            self._id = self._generate_new_id()
        elif isinstance(oid, ObjectId):
            self._id = oid.binary
        elif isinstance(oid, str):
            if len(oid) != 24:
                raise ValueError(
                    "ObjectId hex string must be exactly 24 characters"
                )
            try:
                self._id = bytes.fromhex(oid)
            except ValueError:
                raise ValueError(
                    "ObjectId hex string contains invalid characters"
                )
        elif isinstance(oid, bytes):
            if len(oid) != 12:
                raise ValueError("ObjectId must be exactly 12 bytes")
            self._id = oid
        elif isinstance(oid, int):
            # If an integer is provided, it replaces the timestamp part
            # according to MongoDB specification
            if oid < 0 or oid > 0xFFFFFFFF:
                raise ValueError(
                    "Integer timestamp must be between 0 and 0xFFFFFFFF"
                )
            # Generate a new ObjectId but with the provided timestamp
            self._id = self._generate_new_id_with_timestamp(oid)
        else:
            raise TypeError(
                "ObjectId must be a string, bytes, ObjectId, int, or None"
            )

    @classmethod
    def _generate_new_id(cls) -> bytes:
        """
        Generate a new 12-byte ObjectId value according to MongoDB specification.

        This method creates a unique 12-byte identifier consisting of:
        - 4 bytes: timestamp (seconds since Unix epoch)
        - 5 bytes: random value (generated once per process)
        - 3 bytes: counter (incrementing from a random value)

        The method ensures thread safety by using a lock when accessing shared
        random bytes and counter values. The random bytes are generated once
        per process, and the counter is incremented for each new ObjectId.

        Returns:
            bytes: A new 12-byte ObjectId value
        """
        # Ensure thread safety for random bytes and counter
        with cls._counter_lock:
            if cls._random_bytes is None:
                # Generate random bytes once (5 bytes), as per MongoDB spec
                cls._random_bytes = os.urandom(5)

            if cls._counter is None:
                # Initialize counter with a random value
                cls._counter = random.randint(0, 0xFFFFFF)

            # Increment counter and keep only 3 bytes
            cls._counter = (cls._counter + 1) % 0x1000000

        # Build the 12-byte ObjectId according to MongoDB specification:
        # 4 bytes: timestamp (Unix timestamp, big-endian)
        timestamp = int(time.time()).to_bytes(4, "big")

        # 5 bytes: random value (big-endian)
        random_bytes = cls._random_bytes

        # 3 bytes: counter (big-endian)
        counter = cls._counter.to_bytes(3, "big")

        return timestamp + random_bytes + counter

    @classmethod
    def _generate_new_id_with_timestamp(cls, timestamp: int) -> bytes:
        """
        Generate a new 12-byte ObjectId value with a specific timestamp according to MongoDB specification.

        This method creates a unique 12-byte identifier with the provided timestamp and following MongoDB's format:
        - 4 bytes: provided timestamp (instead of current time)
        - 5 bytes: random value (generated once per process)
        - 3 bytes: counter (incrementing from a random value)

        The method ensures thread safety by using a lock when accessing shared
        random bytes and counter values. The random bytes are generated once
        per process, and the counter is incremented for each new ObjectId.

        Args:
            timestamp: An integer representing the Unix timestamp to use for the ObjectId

        Returns:
            bytes: A new 12-byte ObjectId value with the specified timestamp
        """
        # Ensure thread safety for random bytes and counter
        with cls._counter_lock:
            if cls._random_bytes is None:
                # Generate random bytes once (5 bytes), as per MongoDB spec
                cls._random_bytes = os.urandom(5)

            if cls._counter is None:
                # Initialize counter with a random value
                cls._counter = random.randint(0, 0xFFFFFF)

            # Increment counter and keep only 3 bytes
            cls._counter = (cls._counter + 1) % 0x1000000

        # Build the 12-byte ObjectId according to MongoDB specification:
        # 4 bytes: provided timestamp (big-endian)
        timestamp_bytes = timestamp.to_bytes(4, "big")

        # 5 bytes: random value (big-endian)
        random_bytes = cls._random_bytes

        # 3 bytes: counter (big-endian)
        counter = cls._counter.to_bytes(3, "big")

        return timestamp_bytes + random_bytes + counter

    @classmethod
    def is_valid(cls, oid: Any) -> bool:
        """
        Check if the given value is a valid ObjectId.

        Args:
            oid: Value to validate

        Returns:
            True if the value is a valid ObjectId, False otherwise
        """
        try:
            if isinstance(oid, ObjectId):
                return True
            elif isinstance(oid, str):
                if len(oid) != 24:
                    return False
                int(oid, 16)  # Try to parse as hex
                return True
            elif isinstance(oid, bytes):
                return len(oid) == 12
            elif isinstance(oid, int):
                return 0 <= oid <= 0xFFFFFFFF
            else:
                return False
        except (TypeError, ValueError):
            return False

    @property
    def binary(self) -> bytes:
        """Get the binary representation of this ObjectId."""
        return self._id

    @property
    def hex(self) -> str:
        """Get the hexadecimal string representation of this ObjectId."""
        return self._id.hex()

    def __str__(self) -> str:
        """Return the hexadecimal string representation."""
        return self.hex

    def __repr__(self) -> str:
        """Return a string representation of this ObjectId."""
        return f"ObjectId('{self.hex}')"

    def __bytes__(self) -> bytes:
        """Return the binary representation of this ObjectId."""
        return self._id

    def __eq__(self, other: Any) -> bool:
        """Check equality with another ObjectId."""
        if isinstance(other, ObjectId):
            return self._id == other._id
        elif isinstance(other, bytes):
            return self._id == other
        elif isinstance(other, str):
            try:
                return self._id == bytes.fromhex(other)
            except ValueError:
                return False
        return False

    def __ne__(self, other: Any) -> bool:
        """Check inequality with another ObjectId."""
        return not self.__eq__(other)

    def __hash__(self) -> int:
        """Return a hash value for this ObjectId."""
        return hash(self._id)

    def generation_time(self) -> float:
        """
        Get the generation time of this ObjectId as a Unix timestamp.

        Returns:
            Unix timestamp of when this ObjectId was created
        """
        # First 4 bytes contain the timestamp
        timestamp_bytes = self._id[:4]
        return int.from_bytes(timestamp_bytes, "big")

    def encode_for_storage(self) -> dict:
        """
        Encode the ObjectId for JSON storage compatibility with NeoSQLite.

        Returns:
            A dictionary representation for JSON storage
        """
        return {
            "__neosqlite_objectid__": True,
            "id": self.hex,
        }

    @classmethod
    def decode_from_storage(cls, encoded_data: dict) -> ObjectId:
        """
        Decode an ObjectId from JSON storage format.

        Args:
            encoded_data: Dictionary representation from JSON storage

        Returns:
            An ObjectId instance
        """
        if (
            not isinstance(encoded_data, dict)
            or "__neosqlite_objectid__" not in encoded_data
        ):
            raise ValueError("Invalid encoded ObjectId data")

        if "id" not in encoded_data:
            raise ValueError(
                "Invalid encoded ObjectId data: missing 'id' field"
            )

        return cls(encoded_data["id"])
