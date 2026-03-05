"""Tests for BlockDevice core module."""

import pytest

from src.core.block_device import BlockDevice


class TestBlockDevice:
    def test_create_device(self):
        dev = BlockDevice("test", block_size=512, block_count=10)
        assert dev.name == "test"
        assert dev.block_size == 512
        assert dev.block_count == 10
        assert dev.total_capacity == 5120

    def test_invalid_params(self):
        with pytest.raises(ValueError):
            BlockDevice("bad", block_size=0, block_count=10)
        with pytest.raises(ValueError):
            BlockDevice("bad", block_size=512, block_count=-1)

    def test_read_unwritten_block_returns_zeros(self, small_device):
        data = small_device.read_block(0)
        assert data == b"\x00" * 512
        assert len(data) == small_device.block_size

    def test_write_and_read_block(self, small_device):
        payload = b"Hello, IBM Storage!" + b"\x00" * (512 - 19)
        small_device.write_block(0, payload)
        assert small_device.read_block(0) == payload

    def test_write_truncates_oversized_data(self, small_device):
        big_data = b"\xFF" * 1024
        small_device.write_block(0, big_data)
        data = small_device.read_block(0)
        assert len(data) == 512
        assert data == b"\xFF" * 512

    def test_write_pads_undersized_data(self, small_device):
        small_device.write_block(0, b"\xAB" * 10)
        data = small_device.read_block(0)
        assert len(data) == 512
        assert data[:10] == b"\xAB" * 10
        assert data[10:] == b"\x00" * 502

    def test_out_of_range_block(self, small_device):
        with pytest.raises(IndexError):
            small_device.read_block(16)
        with pytest.raises(IndexError):
            small_device.write_block(-1, b"data")

    def test_zero_block(self, small_device):
        small_device.write_block(5, b"\xFF" * 512)
        small_device.zero_block(5)
        assert small_device.read_block(5) == b"\x00" * 512

    def test_used_and_free_blocks(self, small_device):
        assert small_device.used_blocks == 0
        assert small_device.free_blocks == 16
        small_device.write_block(0, b"data")
        small_device.write_block(1, b"data")
        assert small_device.used_blocks == 2
        assert small_device.free_blocks == 14

    def test_utilization(self, small_device):
        assert small_device.utilization == 0.0
        for i in range(8):
            small_device.write_block(i, b"data")
        assert small_device.utilization == 0.5

    def test_write_blocks_multi(self, small_device):
        data = b"\xAA" * 1024  # 2 blocks worth
        small_device.write_blocks(0, data)
        assert small_device.read_block(0) == b"\xAA" * 512
        assert small_device.read_block(1) == b"\xAA" * 512

    def test_read_blocks_multi(self, small_device):
        small_device.write_block(0, b"\x11" * 512)
        small_device.write_block(1, b"\x22" * 512)
        data = small_device.read_blocks(0, 2)
        assert len(data) == 1024
        assert data[:512] == b"\x11" * 512
        assert data[512:] == b"\x22" * 512

    def test_stats_tracking(self, small_device):
        small_device.write_block(0, b"data")
        small_device.read_block(0)
        small_device.read_block(0)
        assert small_device.stats.writes == 1
        assert small_device.stats.reads == 2
        assert small_device.stats.bytes_written == 512
        assert small_device.stats.bytes_read == 1024

    def test_zero_all(self, small_device):
        for i in range(10):
            small_device.write_block(i, b"\xFF" * 512)
        assert small_device.used_blocks == 10
        small_device.zero_all()
        assert small_device.used_blocks == 0
