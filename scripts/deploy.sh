#!/usr/bin/env bash
# PyStorageOps - Docker Deployment Script
# Builds and deploys the application stack using docker-compose.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

ACTION=${1:-up}

echo "=== PyStorageOps Deployment ==="
cd "$PROJECT_ROOT"

case "$ACTION" in
    build)
        echo "Building Docker images..."
        docker-compose build
        echo "Build complete."
        ;;
    up)
        echo "Starting services..."
        docker-compose up -d --build
        echo ""
        echo "Services started:"
        echo "  API:        http://localhost:8000"
        echo "  API Docs:   http://localhost:8000/docs"
        echo "  Prometheus: http://localhost:9090"
        echo "  Grafana:    http://localhost:3000 (admin/admin)"
        ;;
    down)
        echo "Stopping services..."
        docker-compose down
        echo "Services stopped."
        ;;
    logs)
        docker-compose logs -f
        ;;
    status)
        docker-compose ps
        ;;
    restart)
        echo "Restarting services..."
        docker-compose restart
        ;;
    *)
        echo "Usage: $0 {build|up|down|logs|status|restart}"
        exit 1
        ;;
esac
