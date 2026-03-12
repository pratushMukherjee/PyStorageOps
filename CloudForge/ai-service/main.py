"""
FastAPI AI Deployment Assistant Service.

Provides REST endpoints for the AI-powered deployment assistant,
including chat, project analysis, Dockerfile generation, and error diagnosis.
"""

import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

try:
    from .tools import execute_tool
except ImportError:
    from tools import execute_tool

app = FastAPI(
    title="CloudForge AI Assistant",
    description="AI-powered deployment assistant for CloudForge PaaS",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str
    context: dict | None = None


class ChatResponse(BaseModel):
    reply: str
    tool_calls: list[dict] = []


class AnalyzeRequest(BaseModel):
    files: list[str]


class DockerfileRequest(BaseModel):
    language: str
    framework: str = ""
    entrypoint: str = ""
    port: int = 8000


class DiagnoseRequest(BaseModel):
    error_message: str
    build_log: str = ""
    language: str = ""


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "CloudForge AI"}


@app.post("/api/v1/ai/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    """Chat with the AI deployment assistant."""
    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key:
        # Fallback: use tools directly without LLM
        return ChatResponse(
            reply=_fallback_response(req.message),
            tool_calls=[],
        )

    try:
        try:
            from .agent import DeploymentAgent
        except ImportError:
            from agent import DeploymentAgent

        agent = DeploymentAgent(api_key)
        result = agent.chat(req.message)
        return ChatResponse(reply=result.message, tool_calls=result.tool_calls)
    except Exception as e:
        return ChatResponse(
            reply=f"AI service error: {str(e)}. Using fallback analysis.",
            tool_calls=[],
        )


@app.post("/api/v1/ai/analyze")
async def analyze_project(req: AnalyzeRequest):
    """Analyze project files to detect language and configuration."""
    result = execute_tool("analyze_project", {"files": req.files})
    return {"analysis": result}


@app.post("/api/v1/ai/dockerfile")
async def generate_dockerfile(req: DockerfileRequest):
    """Generate a Dockerfile for a given language and framework."""
    result = execute_tool("generate_dockerfile", {
        "language": req.language,
        "framework": req.framework,
        "entrypoint": req.entrypoint,
        "port": req.port,
    })
    return {"dockerfile": result}


@app.post("/api/v1/ai/diagnose")
async def diagnose_error(req: DiagnoseRequest):
    """Diagnose a deployment error and suggest fixes."""
    result = execute_tool("diagnose_error", {
        "error_message": req.error_message,
        "build_log": req.build_log,
        "language": req.language,
    })
    return {"diagnosis": result}


@app.post("/api/v1/ai/optimize")
async def optimize(req: dict):
    """Suggest deployment optimizations."""
    result = execute_tool("optimize_config", req)
    return {"recommendations": result}


def _fallback_response(message: str) -> str:
    """Simple keyword-based fallback when no API key is configured."""
    msg_lower = message.lower()
    if "deploy" in msg_lower:
        return "To deploy an app: 1) Create an app with POST /api/v1/apps 2) Trigger deployment with POST /api/v1/apps/{id}/deploy. CloudForge auto-detects your language and builds a container."
    if "error" in msg_lower or "fail" in msg_lower:
        return "Common deployment issues: missing dependencies (check requirements.txt/package.json), wrong entry point, port mismatch. Check logs with GET /api/v1/apps/{id}/logs."
    if "dockerfile" in msg_lower or "docker" in msg_lower:
        return "CloudForge auto-generates Dockerfiles via buildpacks. Supported: Python, Node.js, Go, Java. Or provide your own Dockerfile in the project root."
    return "I'm the CloudForge AI assistant. I can help with: deploying apps, diagnosing errors, generating Dockerfiles, and optimizing configurations. What do you need help with?"
