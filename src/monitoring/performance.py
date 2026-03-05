"""
I/O performance analysis and benchmarking module.

Measures IOPS, throughput, and latency for storage operations.
"""

import os
import time
from dataclasses import dataclass

from ..core.block_device import BlockDevice


@dataclass
class BenchmarkResult:
    operation: str
    total_ops: int
    total_bytes: int
    elapsed_seconds: float
    iops: float
    throughput_mb_s: float
    avg_latency_us: float
    min_latency_us: float
    max_latency_us: float


class PerformanceAnalyzer:
    """Benchmarks and analyzes storage I/O performance."""

    def benchmark_sequential_write(
        self, device: BlockDevice, block_count: int = 100
    ) -> BenchmarkResult:
        """Benchmark sequential write performance."""
        block_count = min(block_count, device.block_count)
        latencies = []

        for i in range(block_count):
            data = os.urandom(device.block_size)
            start = time.perf_counter()
            device.write_block(i, data)
            elapsed = time.perf_counter() - start
            latencies.append(elapsed)

        return self._compile_result("sequential_write", device.block_size, latencies)

    def benchmark_sequential_read(
        self, device: BlockDevice, block_count: int = 100
    ) -> BenchmarkResult:
        """Benchmark sequential read performance."""
        block_count = min(block_count, device.block_count)
        latencies = []

        for i in range(block_count):
            start = time.perf_counter()
            device.read_block(i)
            elapsed = time.perf_counter() - start
            latencies.append(elapsed)

        return self._compile_result("sequential_read", device.block_size, latencies)

    def benchmark_random_write(
        self, device: BlockDevice, op_count: int = 100
    ) -> BenchmarkResult:
        """Benchmark random write performance."""
        import random
        latencies = []

        for _ in range(op_count):
            block_idx = random.randint(0, device.block_count - 1)
            data = os.urandom(device.block_size)
            start = time.perf_counter()
            device.write_block(block_idx, data)
            elapsed = time.perf_counter() - start
            latencies.append(elapsed)

        return self._compile_result("random_write", device.block_size, latencies)

    def benchmark_random_read(
        self, device: BlockDevice, op_count: int = 100
    ) -> BenchmarkResult:
        """Benchmark random read performance."""
        import random
        latencies = []

        for _ in range(op_count):
            block_idx = random.randint(0, device.block_count - 1)
            start = time.perf_counter()
            device.read_block(block_idx)
            elapsed = time.perf_counter() - start
            latencies.append(elapsed)

        return self._compile_result("random_read", device.block_size, latencies)

    def _compile_result(
        self, operation: str, block_size: int, latencies: list[float]
    ) -> BenchmarkResult:
        total_ops = len(latencies)
        total_bytes = total_ops * block_size
        total_time = sum(latencies)
        avg_lat = total_time / total_ops if total_ops else 0

        return BenchmarkResult(
            operation=operation,
            total_ops=total_ops,
            total_bytes=total_bytes,
            elapsed_seconds=total_time,
            iops=total_ops / total_time if total_time > 0 else 0,
            throughput_mb_s=(total_bytes / (1024 * 1024)) / total_time if total_time > 0 else 0,
            avg_latency_us=avg_lat * 1_000_000,
            min_latency_us=min(latencies) * 1_000_000 if latencies else 0,
            max_latency_us=max(latencies) * 1_000_000 if latencies else 0,
        )
