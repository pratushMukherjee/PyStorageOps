"""
Data integrity verification module.

Provides checksum computation and verification using CRC32 and SHA-256.
Supports per-block integrity tracking for storage devices.
"""

import hashlib
import struct
import zlib


class DataIntegrity:
    """Checksum computation and verification for storage data."""

    @staticmethod
    def crc32(data: bytes) -> int:
        """Compute CRC32 checksum."""
        return zlib.crc32(data) & 0xFFFFFFFF

    @staticmethod
    def sha256(data: bytes) -> str:
        """Compute SHA-256 hex digest."""
        return hashlib.sha256(data).hexdigest()

    @staticmethod
    def verify_crc32(data: bytes, expected: int) -> bool:
        """Verify data against an expected CRC32 checksum."""
        return DataIntegrity.crc32(data) == expected

    @staticmethod
    def verify_sha256(data: bytes, expected: str) -> bool:
        """Verify data against an expected SHA-256 hex digest."""
        return DataIntegrity.sha256(data) == expected


class BlockIntegrityTracker:
    """Tracks per-block checksums for a block device to detect corruption."""

    def __init__(self):
        # block_index -> (crc32, sha256)
        self._checksums: dict[int, tuple[int, str]] = {}

    def record(self, block_index: int, data: bytes) -> None:
        """Record checksums for a block after a write."""
        self._checksums[block_index] = (
            DataIntegrity.crc32(data),
            DataIntegrity.sha256(data),
        )

    def verify(self, block_index: int, data: bytes) -> bool:
        """Verify a block's data matches its recorded checksums."""
        if block_index not in self._checksums:
            return True  # No checksum recorded, assume valid

        expected_crc, expected_sha = self._checksums[block_index]
        return (
            DataIntegrity.verify_crc32(data, expected_crc)
            and DataIntegrity.verify_sha256(data, expected_sha)
        )

    def remove(self, block_index: int) -> None:
        """Remove checksum tracking for a block."""
        self._checksums.pop(block_index, None)

    def scan(self, device) -> list[int]:
        """Scan a device and return list of corrupted block indices."""
        corrupted = []
        for block_index in self._checksums:
            data = device.read_block(block_index)
            if not self.verify(block_index, data):
                corrupted.append(block_index)
        return corrupted

    @property
    def tracked_blocks(self) -> int:
        return len(self._checksums)
