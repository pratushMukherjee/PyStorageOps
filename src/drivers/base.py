"""
Abstract base class for storage device drivers.

Defines the interface that all storage drivers (NVMe, SCSI, etc.) must implement.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum


class DeviceStatus(Enum):
    READY = "ready"
    BUSY = "busy"
    ERROR = "error"
    OFFLINE = "offline"


@dataclass
class DeviceInfo:
    vendor: str
    model: str
    serial: str
    firmware_rev: str
    capacity_bytes: int
    block_size: int
    protocol: str


class StorageDriver(ABC):
    """Abstract interface for storage device drivers."""

    @abstractmethod
    def identify(self) -> DeviceInfo:
        """Return device identification information."""

    @abstractmethod
    def read(self, lba: int, block_count: int) -> bytes:
        """Read blocks starting at logical block address (LBA)."""

    @abstractmethod
    def write(self, lba: int, data: bytes) -> int:
        """Write data starting at LBA. Returns number of blocks written."""

    @abstractmethod
    def flush(self) -> bool:
        """Flush volatile write cache to persistent storage."""

    @abstractmethod
    def get_status(self) -> DeviceStatus:
        """Return current device status."""

    @abstractmethod
    def get_capacity(self) -> tuple[int, int]:
        """Return (total_blocks, block_size)."""
