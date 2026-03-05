# Multi-stage build for PyStorageOps
# Stage 1: Build C extensions
FROM gcc:latest AS c-builder
WORKDIR /build
COPY c_extensions/ .
RUN make

# Stage 2: Python application
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Copy C shared library
COPY --from=c-builder /build/libstorageops.so /app/c_extensions/

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY config/ ./config/
COPY db/ ./db/
COPY setup.py .

# Install the package
RUN pip install -e .

# Initialize database
RUN python -c "import sqlite3; conn = sqlite3.connect('storage.db'); \
    f = open('db/schema.sql'); conn.executescript(f.read()); conn.close()"

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD python -c "import httpx; r = httpx.get('http://localhost:8000/health'); r.raise_for_status()" || exit 1

CMD ["uvicorn", "src.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
