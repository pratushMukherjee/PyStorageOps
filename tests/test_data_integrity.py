"""Tests for data integrity module."""

import pytest

from src.core.block_device import BlockDevice
from src.core.data_integrity import BlockIntegrityTracker, DataIntegrity


class TestDataIntegrity:
    def test_crc32_deterministic(self):
        data = b"IBM Storage Systems"
        assert DataIntegrity.crc32(data) == DataIntegrity.crc32(data)

    def test_crc32_different_data(self):
        assert DataIntegrity.crc32(b"hello") != DataIntegrity.crc32(b"world")

    def test_sha256_deterministic(self):
        data = b"test data"
        assert DataIntegrity.sha256(data) == DataIntegrity.sha256(data)

    def test_sha256_hex_length(self):
        digest = DataIntegrity.sha256(b"anything")
        assert len(digest) == 64  # 256 bits = 64 hex chars

    def test_verify_crc32_valid(self):
        data = b"verify me"
        checksum = DataIntegrity.crc32(data)
        assert DataIntegrity.verify_crc32(data, checksum) is True

    def test_verify_crc32_corrupted(self):
        data = b"original"
        checksum = DataIntegrity.crc32(data)
        assert DataIntegrity.verify_crc32(b"corrupted", checksum) is False

    def test_verify_sha256_valid(self):
        data = b"integrity check"
        digest = DataIntegrity.sha256(data)
        assert DataIntegrity.verify_sha256(data, digest) is True

    def test_verify_sha256_corrupted(self):
        data = b"original"
        digest = DataIntegrity.sha256(data)
        assert DataIntegrity.verify_sha256(b"tampered", digest) is False


class TestBlockIntegrityTracker:
    def test_record_and_verify(self):
        tracker = BlockIntegrityTracker()
        data = b"\xAA" * 512
        tracker.record(0, data)
        assert tracker.verify(0, data) is True

    def test_detect_corruption(self):
        tracker = BlockIntegrityTracker()
        original = b"\xAA" * 512
        corrupted = b"\xBB" * 512
        tracker.record(0, original)
        assert tracker.verify(0, corrupted) is False

    def test_untracked_block_passes(self):
        tracker = BlockIntegrityTracker()
        assert tracker.verify(99, b"anything") is True

    def test_scan_device(self):
        device = BlockDevice("integrity-test", block_size=512, block_count=8)
        tracker = BlockIntegrityTracker()

        # Write and track blocks
        for i in range(4):
            data = bytes([i]) * 512
            device.write_block(i, data)
            tracker.record(i, data)

        # No corruption
        assert tracker.scan(device) == []

        # Corrupt block 2 directly
        device._blocks[2] = b"\xFF" * 512
        corrupted = tracker.scan(device)
        assert corrupted == [2]

    def test_tracked_blocks_count(self):
        tracker = BlockIntegrityTracker()
        assert tracker.tracked_blocks == 0
        tracker.record(0, b"data")
        tracker.record(1, b"data")
        assert tracker.tracked_blocks == 2
        tracker.remove(0)
        assert tracker.tracked_blocks == 1
