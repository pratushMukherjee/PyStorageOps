"""
Simple inode-based file system built on top of BlockDevice.

Supports basic file operations: create, read, write, delete, list.
Metadata is stored in-memory with serialization support.
"""

import time
from dataclasses import dataclass, field

from .block_device import BlockDevice


@dataclass
class Inode:
    """File metadata (inode)."""
    inode_id: int
    name: str
    size: int = 0
    blocks: list[int] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    modified_at: float = field(default_factory=time.time)
    is_directory: bool = False


class SimpleFileSystem:
    """A minimal file system that manages files on a BlockDevice."""

    def __init__(self, device: BlockDevice):
        self.device = device
        self._inodes: dict[str, Inode] = {}
        self._next_inode_id = 1
        self._allocated_blocks: set[int] = set()

    def _allocate_blocks(self, count: int) -> list[int]:
        """Find and allocate free blocks."""
        allocated = []
        for block_idx in range(self.device.block_count):
            if block_idx not in self._allocated_blocks:
                allocated.append(block_idx)
                self._allocated_blocks.add(block_idx)
                if len(allocated) == count:
                    return allocated
        raise OSError("No space left on device")

    def _free_blocks(self, blocks: list[int]) -> None:
        """Release allocated blocks."""
        for b in blocks:
            self._allocated_blocks.discard(b)
            self.device.zero_block(b)

    def create_file(self, name: str, data: bytes = b"") -> Inode:
        """Create a new file with optional initial data."""
        if name in self._inodes:
            raise FileExistsError(f"File '{name}' already exists")

        blocks_needed = max(1, (len(data) + self.device.block_size - 1) // self.device.block_size)
        if blocks_needed > self.device.free_blocks - len(self._allocated_blocks):
            blocks_needed = min(blocks_needed, self.device.block_count - len(self._allocated_blocks))

        allocated = self._allocate_blocks(blocks_needed) if data else []

        inode = Inode(
            inode_id=self._next_inode_id,
            name=name,
            size=len(data),
            blocks=allocated,
        )
        self._next_inode_id += 1

        # Write data to allocated blocks
        for i, block_idx in enumerate(allocated):
            offset = i * self.device.block_size
            chunk = data[offset : offset + self.device.block_size]
            self.device.write_block(block_idx, chunk)

        self._inodes[name] = inode
        return inode

    def read_file(self, name: str) -> bytes:
        """Read the entire contents of a file."""
        if name not in self._inodes:
            raise FileNotFoundError(f"File '{name}' not found")

        inode = self._inodes[name]
        data = bytearray()
        for block_idx in inode.blocks:
            data.extend(self.device.read_block(block_idx))

        return bytes(data[: inode.size])

    def write_file(self, name: str, data: bytes) -> Inode:
        """Overwrite a file's contents."""
        if name not in self._inodes:
            raise FileNotFoundError(f"File '{name}' not found")

        inode = self._inodes[name]

        # Free old blocks
        self._free_blocks(inode.blocks)

        # Allocate new blocks
        blocks_needed = max(1, (len(data) + self.device.block_size - 1) // self.device.block_size)
        allocated = self._allocate_blocks(blocks_needed) if data else []

        for i, block_idx in enumerate(allocated):
            offset = i * self.device.block_size
            chunk = data[offset : offset + self.device.block_size]
            self.device.write_block(block_idx, chunk)

        inode.blocks = allocated
        inode.size = len(data)
        inode.modified_at = time.time()
        return inode

    def delete_file(self, name: str) -> None:
        """Delete a file and free its blocks."""
        if name not in self._inodes:
            raise FileNotFoundError(f"File '{name}' not found")

        inode = self._inodes.pop(name)
        self._free_blocks(inode.blocks)

    def list_files(self) -> list[Inode]:
        """List all files in the filesystem."""
        return list(self._inodes.values())

    def stat(self, name: str) -> Inode:
        """Get file metadata."""
        if name not in self._inodes:
            raise FileNotFoundError(f"File '{name}' not found")
        return self._inodes[name]

    @property
    def used_space(self) -> int:
        return len(self._allocated_blocks) * self.device.block_size

    @property
    def free_space(self) -> int:
        return (self.device.block_count - len(self._allocated_blocks)) * self.device.block_size

    def to_dict(self) -> dict:
        """Serialize filesystem metadata to a dictionary."""
        return {
            "device": self.device.name,
            "block_size": self.device.block_size,
            "block_count": self.device.block_count,
            "files": [
                {
                    "inode_id": inode.inode_id,
                    "name": inode.name,
                    "size": inode.size,
                    "blocks": inode.blocks,
                    "created_at": inode.created_at,
                    "modified_at": inode.modified_at,
                }
                for inode in self._inodes.values()
            ],
        }
