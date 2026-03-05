#!/usr/bin/env bash
# PyStorageOps - Performance Benchmark Script
# Runs storage I/O benchmarks and generates a report.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "============================================"
echo "  PyStorageOps Performance Benchmark"
echo "============================================"
echo ""

cd "$PROJECT_ROOT"

# Activate venv if present
if [ -d ".venv" ]; then
    if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
        source .venv/Scripts/activate
    else
        source .venv/bin/activate
    fi
fi

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
REPORT_FILE="benchmark_report_${TIMESTAMP}.txt"

python3 -c "
from src.core.block_device import BlockDevice
from src.monitoring.performance import PerformanceAnalyzer

analyzer = PerformanceAnalyzer()

print('Block Size: 4096 bytes')
print('Block Count: 10000')
print('')

device = BlockDevice('bench-device', block_size=4096, block_count=10000)

tests = [
    ('Sequential Write', analyzer.benchmark_sequential_write),
    ('Sequential Read',  analyzer.benchmark_sequential_read),
    ('Random Write',     analyzer.benchmark_random_write),
    ('Random Read',      analyzer.benchmark_random_read),
]

for name, bench_fn in tests:
    result = bench_fn(device, 1000)
    print(f'--- {name} ---')
    print(f'  Operations:   {result.total_ops}')
    print(f'  IOPS:         {result.iops:,.0f}')
    print(f'  Throughput:   {result.throughput_mb_s:,.2f} MB/s')
    print(f'  Avg Latency:  {result.avg_latency_us:,.1f} us')
    print(f'  Min Latency:  {result.min_latency_us:,.1f} us')
    print(f'  Max Latency:  {result.max_latency_us:,.1f} us')
    print('')
" | tee "$REPORT_FILE"

echo "Report saved to: $REPORT_FILE"
