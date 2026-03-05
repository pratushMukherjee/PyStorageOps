#!/usr/bin/env bash
# PyStorageOps - Environment Setup Script
# Sets up Python virtual environment, installs dependencies, and initializes the database.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "=== PyStorageOps Setup ==="
echo "Project root: $PROJECT_ROOT"

# Check Python version
PYTHON=${PYTHON:-python3}
if ! command -v "$PYTHON" &>/dev/null; then
    echo "ERROR: $PYTHON not found. Install Python 3.9+."
    exit 1
fi

PY_VERSION=$("$PYTHON" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "Python version: $PY_VERSION"

# Create virtual environment
VENV_DIR="$PROJECT_ROOT/.venv"
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    "$PYTHON" -m venv "$VENV_DIR"
fi

# Activate venv
if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    source "$VENV_DIR/Scripts/activate"
else
    source "$VENV_DIR/bin/activate"
fi

echo "Virtual environment activated: $VIRTUAL_ENV"

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r "$PROJECT_ROOT/requirements.txt"
pip install -e "$PROJECT_ROOT[dev]"

# Initialize database
echo "Initializing database..."
DB_PATH="$PROJECT_ROOT/storage.db"
if [ -f "$PROJECT_ROOT/db/schema.sql" ]; then
    sqlite3 "$DB_PATH" < "$PROJECT_ROOT/db/schema.sql" 2>/dev/null || \
        python3 -c "
import sqlite3
conn = sqlite3.connect('$DB_PATH')
with open('$PROJECT_ROOT/db/schema.sql') as f:
    conn.executescript(f.read())
conn.close()
print('Database initialized.')
"
fi

# Build C extensions (if gcc available)
if command -v gcc &>/dev/null; then
    echo "Building C extensions..."
    cd "$PROJECT_ROOT/c_extensions"
    make clean && make
    echo "C extensions built successfully."
else
    echo "WARNING: gcc not found. Skipping C extensions build."
fi

echo ""
echo "=== Setup Complete ==="
echo "Activate venv: source $VENV_DIR/bin/activate"
echo "Run tests:     make test"
echo "Start API:     make run"
