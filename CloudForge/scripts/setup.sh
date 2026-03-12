#!/usr/bin/env bash
# CloudForge — Development Environment Setup
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "=== CloudForge Setup ==="
cd "$PROJECT_ROOT"

# Python dependencies for AI service, CLI, and tests
echo "Installing Python dependencies..."
python3 -m pip install -r ai-service/requirements.txt
python3 -m pip install -r cli/requirements.txt
python3 -m pip install pytest httpx

# Go dependencies
if command -v go &>/dev/null; then
    echo "Installing Go dependencies..."
    cd server && go mod download && cd ..
else
    echo "WARNING: Go not found. Install Go 1.21+ for the API server."
fi

# Verify Docker
if command -v docker &>/dev/null; then
    echo "Docker: $(docker --version)"
else
    echo "WARNING: Docker not found. Install Docker for container deployment."
fi

echo ""
echo "=== Setup Complete ==="
echo "Start API server:  cd server && go run ."
echo "Start AI service:  uvicorn ai-service.main:app --port 8081"
echo "Run tests:         python -m pytest tests/ -v"
echo "Full stack:        docker-compose up -d"
