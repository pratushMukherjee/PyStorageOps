"""
Block storage device simulation.

Simulates a fixed-size block device with configurable block size and count.
Supports read, write, and zero-fill operations at the block level.
"""

import threading
from dataclasses import dataclass, field


@dataclass
class BlockDeviceStats:
    reads: int = 0
    writes: int = 0
    bytes_read: int = 0
    bytes_written: int = 0


class BlockDevice:
    """Simulates a block storage device with fixed-size blocks."""

    def __init__(self, name: str, block_size: int = 4096, block_count: int = 1024):
        if block_size <= 0 or block_count <= 0:
            raise ValueError("block_size and block_count must be positive")

        self.name = name
        self.block_size = block_size
        self.block_count = block_count
        self.total_capacity = block_size * block_count

        # Storage backing: dict of block_index -> bytes
        self._blocks: dict[int, bytes] = {}
        self._lock = threading.Lock()
        self.stats = BlockDeviceStats()

    def _validate_block_index(self, block_index: int) -> None:
        if not (0 <= block_index < self.block_count):
            raise IndexError(
                f"Block index {block_index} out of range [0, {self.block_count})"
            )

    def read_block(self, block_index: int) -> bytes:
        """Read a single block. Returns zero-filled bytes if never written."""
        self._validate_block_index(block_index)
        with self._lock:
            self.stats.reads += 1
            self.stats.bytes_read += self.block_size
            return self._blocks.get(block_index, b"\x00" * self.block_size)

    def write_block(self, block_index: int, data: bytes) -> None:
        """Write data to a block. Data is padded or truncated to block_size."""
        self._validate_block_index(block_index)
        if len(data) > self.block_size:
            data = data[: self.block_size]
        elif len(data) < self.block_size:
            data = data + b"\x00" * (self.block_size - len(data))

        with self._lock:
            self._blocks[block_index] = data
            self.stats.writes += 1
            self.stats.bytes_written += self.block_size

    def read_blocks(self, start: int, count: int) -> bytes:
        """Read a contiguous range of blocks."""
        result = bytearray()
        for i in range(start, start + count):
            result.extend(self.read_block(i))
        return bytes(result)

    def write_blocks(self, start: int, data: bytes) -> None:
        """Write data across multiple contiguous blocks starting at start."""
        blocks_needed = (len(data) + self.block_size - 1) // self.block_size
        for i in range(blocks_needed):
            offset = i * self.block_size
            chunk = data[offset : offset + self.block_size]
            self.write_block(start + i, chunk)

    def zero_block(self, block_index: int) -> None:
        """Zero-fill a block (TRIM/discard)."""
        self._validate_block_index(block_index)
        with self._lock:
            self._blocks.pop(block_index, None)

    def zero_all(self) -> None:
        """Zero-fill the entire device."""
        with self._lock:
            self._blocks.clear()

    @property
    def used_blocks(self) -> int:
        return len(self._blocks)

    @property
    def free_blocks(self) -> int:
        return self.block_count - self.used_blocks

    @property
    def utilization(self) -> float:
        return self.used_blocks / self.block_count if self.block_count > 0 else 0.0

    def __repr__(self) -> str:
        return (
            f"BlockDevice(name='{self.name}', block_size={self.block_size}, "
            f"blocks={self.used_blocks}/{self.block_count})"
        )
