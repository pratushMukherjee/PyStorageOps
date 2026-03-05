"""Tests for performance analysis module."""

import pytest

from src.core.block_device import BlockDevice
from src.monitoring.performance import PerformanceAnalyzer


@pytest.fixture
def analyzer():
    return PerformanceAnalyzer()


@pytest.fixture
def bench_device():
    return BlockDevice("bench", block_size=4096, block_count=500)


class TestPerformanceAnalyzer:
    def test_sequential_write(self, analyzer, bench_device):
        result = analyzer.benchmark_sequential_write(bench_device, 50)
        assert result.operation == "sequential_write"
        assert result.total_ops == 50
        assert result.iops > 0
        assert result.throughput_mb_s > 0

    def test_sequential_read(self, analyzer, bench_device):
        result = analyzer.benchmark_sequential_read(bench_device, 50)
        assert result.operation == "sequential_read"
        assert result.total_ops == 50
        assert result.avg_latency_us > 0

    def test_random_write(self, analyzer, bench_device):
        result = analyzer.benchmark_random_write(bench_device, 50)
        assert result.operation == "random_write"
        assert result.total_bytes == 50 * 4096

    def test_random_read(self, analyzer, bench_device):
        result = analyzer.benchmark_random_read(bench_device, 50)
        assert result.operation == "random_read"
        assert result.min_latency_us <= result.avg_latency_us
        assert result.avg_latency_us <= result.max_latency_us
