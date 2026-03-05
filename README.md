# PyStorageOps

A Python-based storage management, monitoring, and automation toolkit that simulates enterprise-grade storage operations. Built to demonstrate proficiency in storage systems, hardware protocols, REST APIs, CI/CD, containerization, and observability.

![CI](https://github.com/YOUR_USERNAME/PyStorageOps/actions/workflows/ci.yml/badge.svg)
![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)

## Architecture

```
PyStorageOps
├── src/
│   ├── core/           # Storage engine (block device, RAID 0/1/5, filesystem)
│   ├── drivers/        # NVMe & SCSI protocol simulation
│   ├── api/            # FastAPI REST API with Pydantic models
│   ├── monitoring/     # Prometheus metrics, health checks, performance analysis
│   └── serialization/  # JSON, YAML, Protocol Buffers support
├── c_extensions/       # High-performance C code (CRC32, block ops) via ctypes
├── scripts/            # Bash automation (setup, benchmark, deploy)
├── tests/              # Comprehensive pytest test suite
├── config/             # YAML config, Prometheus/Grafana configs
├── k8s/                # Kubernetes deployment manifests
├── Dockerfile          # Multi-stage Docker build
└── docker-compose.yml  # Full observability stack (App + Prometheus + Grafana)
```

## Features

### Core Storage Engine
- **Block Device Simulation** — Fixed-size block storage with read/write/zero operations and I/O statistics
- **RAID 0/1/5** — Striping, mirroring, and distributed parity with rebuild support
- **File System** — Inode-based filesystem with create, read, write, delete, and metadata serialization
- **Data Integrity** — CRC32 and SHA-256 checksums with per-block corruption detection

### Hardware Protocol Drivers
- **NVMe Driver** — Simulates NVMe command set: Identify, Read, Write, Flush, SMART log, Format
- **SCSI Driver** — Simulates SCSI commands: INQUIRY, READ CAPACITY, READ(10), WRITE(10), TEST UNIT READY

### REST API
- Volume management (CRUD) via FastAPI with OpenAPI documentation
- Block-level read/write endpoints with integrity verification
- Health check and Prometheus-compatible metrics endpoints

### Monitoring & Observability
- Prometheus metrics: IOPS, latency histograms, throughput, capacity utilization
- Configurable health checker with warning/critical thresholds
- Performance benchmarking: sequential and random I/O analysis
- Grafana dashboard configuration included

### C Extensions
- High-performance CRC32 using lookup table (callable via ctypes)
- Fast block copy with XOR mode for RAID parity computation
- Block compare, zero-fill, and pattern-fill operations

## Quick Start

```bash
# Clone and setup
git clone https://github.com/YOUR_USERNAME/PyStorageOps.git
cd PyStorageOps
bash scripts/setup.sh

# Run tests
make test

# Start the API server
make run
# -> http://localhost:8000/docs

# Run benchmarks
make benchmark

# Deploy full stack with Docker
make docker-up
# -> API: localhost:8000 | Prometheus: localhost:9090 | Grafana: localhost:3000
```

## API Examples

```bash
# Create a storage volume
curl -X POST http://localhost:8000/api/v1/storage/volumes \
  -H "Content-Type: application/json" \
  -d '{"name": "production-vol", "size_blocks": 10000, "block_size": 4096}'

# List volumes
curl http://localhost:8000/api/v1/storage/volumes

# Write a block
curl -X POST http://localhost:8000/api/v1/storage/volumes/1/blocks \
  -H "Content-Type: application/json" \
  -d '{"block_index": 0, "data_hex": "deadbeef"}'

# Read a block (returns data + CRC32)
curl http://localhost:8000/api/v1/storage/volumes/1/blocks/0

# Health check
curl http://localhost:8000/health

# Prometheus metrics
curl http://localhost:8000/metrics
```

## Technology Stack

| Category | Technologies |
|----------|-------------|
| **Languages** | Python 3.11, C, Bash, SQL |
| **Storage** | Block storage, RAID 0/1/5, inode filesystem, CRC32/SHA-256 |
| **Protocols** | NVMe, SCSI (simulated command sets) |
| **API** | FastAPI, Pydantic, OpenAPI/Swagger |
| **Data Formats** | JSON, YAML, Protocol Buffers |
| **Database** | SQLite |
| **Testing** | pytest, httpx, coverage |
| **CI/CD** | GitHub Actions (lint, test, build, Docker) |
| **Containers** | Docker (multi-stage), docker-compose, Kubernetes |
| **Monitoring** | Prometheus, Grafana |

## Testing

```bash
# Run all tests with coverage
python -m pytest tests/ -v --cov=src --cov-report=term-missing

# Run specific test modules
python -m pytest tests/test_raid.py -v
python -m pytest tests/test_api.py -v
```

## Project Structure

- `src/core/` — Block device, RAID, filesystem, data integrity
- `src/drivers/` — NVMe and SCSI driver simulation
- `src/api/` — FastAPI REST API with routes and models
- `src/monitoring/` — Prometheus collector, health checker, benchmarking
- `src/serialization/` — Multi-format data serialization
- `c_extensions/` — Performance-critical C code with Makefile
- `scripts/` — Bash automation scripts
- `tests/` — Comprehensive test suite (70+ test cases)
- `config/` — Application, Prometheus, and Grafana configuration
- `k8s/` — Kubernetes deployment manifests

## License

MIT
