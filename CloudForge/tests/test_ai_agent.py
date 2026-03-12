"""Tests for AI service tools and endpoints."""

import os
import sys

import pytest
from fastapi.testclient import TestClient

# Add ai-service directory to path so its modules import directly
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "ai-service"))
sys.path.insert(0, PROJECT_ROOT)

from tools import execute_tool
from main import app


@pytest.fixture
def client():
    return TestClient(app)


class TestAITools:
    def test_analyze_python_project(self):
        result = execute_tool("analyze_project", {"files": ["requirements.txt", "main.py"]})
        assert "python" in result.lower()

    def test_analyze_node_project(self):
        result = execute_tool("analyze_project", {"files": ["package.json", "index.js"]})
        assert "node" in result.lower()

    def test_analyze_unknown_project(self):
        result = execute_tool("analyze_project", {"files": ["random.xyz"]})
        assert "could not" in result.lower() or "specify" in result.lower()

    def test_generate_python_dockerfile(self):
        result = execute_tool("generate_dockerfile", {
            "language": "python",
            "framework": "fastapi",
            "entrypoint": "main.py",
            "port": 8000,
        })
        assert "FROM python" in result
        assert "8000" in result

    def test_generate_go_dockerfile(self):
        result = execute_tool("generate_dockerfile", {
            "language": "go",
            "port": 8080,
        })
        assert "FROM golang" in result

    def test_diagnose_module_error(self):
        result = execute_tool("diagnose_error", {
            "error_message": "ModuleNotFoundError: No module named 'flask'",
            "language": "python",
        })
        assert "requirements.txt" in result.lower() or "dependency" in result.lower()

    def test_diagnose_port_error(self):
        result = execute_tool("diagnose_error", {
            "error_message": "port already in use",
        })
        assert "port" in result.lower()

    def test_optimize_config(self):
        result = execute_tool("optimize_config", {
            "language": "python",
            "image_size_mb": 800,
        })
        assert "multi-stage" in result.lower()

    def test_unknown_tool(self):
        result = execute_tool("nonexistent", {})
        assert "unknown" in result.lower()


class TestAIEndpoints:
    def test_health(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "healthy"

    def test_chat_fallback(self, client):
        resp = client.post("/api/v1/ai/chat", json={"message": "how do I deploy an app?"})
        assert resp.status_code == 200
        assert len(resp.json()["reply"]) > 0

    def test_chat_docker_question(self, client):
        resp = client.post("/api/v1/ai/chat", json={"message": "help with dockerfile"})
        assert resp.status_code == 200
        assert "docker" in resp.json()["reply"].lower()

    def test_analyze_endpoint(self, client):
        resp = client.post("/api/v1/ai/analyze", json={"files": ["requirements.txt"]})
        assert resp.status_code == 200
        assert "python" in resp.json()["analysis"].lower()

    def test_dockerfile_endpoint(self, client):
        resp = client.post("/api/v1/ai/dockerfile", json={
            "language": "node",
            "port": 3000,
        })
        assert resp.status_code == 200
        assert "node" in resp.json()["dockerfile"].lower()

    def test_diagnose_endpoint(self, client):
        resp = client.post("/api/v1/ai/diagnose", json={
            "error_message": "connection refused",
            "language": "python",
        })
        assert resp.status_code == 200
        assert len(resp.json()["diagnosis"]) > 0

    def test_optimize_endpoint(self, client):
        resp = client.post("/api/v1/ai/optimize", json={
            "language": "go",
        })
        assert resp.status_code == 200
        assert len(resp.json()["recommendations"]) > 0
