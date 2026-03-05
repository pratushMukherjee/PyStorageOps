"""Shared test fixtures for PyStorageOps."""

import pytest

from src.core.block_device import BlockDevice


@pytest.fixture
def small_device():
    """A small block device for unit tests (16 blocks, 512 bytes each)."""
    return BlockDevice("test-small", block_size=512, block_count=16)


@pytest.fixture
def medium_device():
    """A medium block device (256 blocks, 4096 bytes each)."""
    return BlockDevice("test-medium", block_size=4096, block_count=256)


@pytest.fixture
def raid_devices():
    """Four identical block devices for RAID tests."""
    return [
        BlockDevice(f"raid-disk-{i}", block_size=4096, block_count=64)
        for i in range(4)
    ]
