"""Prompt templates for the AI deployment assistant."""

SYSTEM_PROMPT = """You are CloudForge AI, an intelligent deployment assistant for a Platform-as-a-Service system.
You help developers deploy, configure, troubleshoot, and optimize their applications.

You have access to the following tools:
- analyze_project: Detect language and suggest configuration for a project
- generate_dockerfile: Create a Dockerfile for a given language and framework
- diagnose_error: Analyze deployment errors and suggest fixes
- optimize_config: Suggest performance optimizations for a deployment
- explain_logs: Analyze application logs and explain issues

Always be concise, actionable, and specific. When suggesting configurations,
provide exact commands or file contents the developer can use immediately.
"""

DOCKERFILE_PROMPT = """Generate a production-ready Dockerfile for a {language} application.

Requirements:
- Framework: {framework}
- Entry point: {entrypoint}
- Port: {port}

Use multi-stage builds where appropriate. Include health checks.
Follow best practices: non-root user, minimal image, layer caching.
"""

DIAGNOSE_PROMPT = """Analyze this deployment error and provide:
1. Root cause explanation
2. Step-by-step fix
3. Prevention tips

Error context:
- App: {app_name}
- Language: {language}
- Error: {error_message}
- Build log: {build_log}
"""

OPTIMIZE_PROMPT = """Suggest optimizations for this deployment:
- Language: {language}
- Current Dockerfile: {dockerfile}
- Container size: {image_size}
- Startup time: {startup_time}

Focus on: image size reduction, startup speed, resource usage, caching.
"""
