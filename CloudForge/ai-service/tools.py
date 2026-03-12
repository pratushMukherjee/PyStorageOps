"""Tool definitions for the AI deployment agent (OpenAI function calling)."""

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "analyze_project",
            "description": "Detect the programming language and suggest deployment configuration for a project",
            "parameters": {
                "type": "object",
                "properties": {
                    "files": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of files in the project root",
                    },
                },
                "required": ["files"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "generate_dockerfile",
            "description": "Generate a Dockerfile for a given language and framework",
            "parameters": {
                "type": "object",
                "properties": {
                    "language": {"type": "string", "description": "Programming language"},
                    "framework": {"type": "string", "description": "Web framework"},
                    "entrypoint": {"type": "string", "description": "Application entry point file"},
                    "port": {"type": "integer", "description": "Port the app listens on"},
                },
                "required": ["language"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "diagnose_error",
            "description": "Analyze a deployment error and suggest fixes",
            "parameters": {
                "type": "object",
                "properties": {
                    "error_message": {"type": "string", "description": "The error message"},
                    "build_log": {"type": "string", "description": "Build/deployment log output"},
                    "language": {"type": "string", "description": "App language"},
                },
                "required": ["error_message"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "optimize_config",
            "description": "Suggest performance optimizations for a deployment",
            "parameters": {
                "type": "object",
                "properties": {
                    "language": {"type": "string"},
                    "dockerfile": {"type": "string", "description": "Current Dockerfile contents"},
                    "image_size_mb": {"type": "number"},
                },
                "required": ["language"],
            },
        },
    },
]


def execute_tool(name: str, args: dict) -> str:
    """Execute a tool call and return the result as a string."""
    if name == "analyze_project":
        return _analyze_project(args.get("files", []))
    elif name == "generate_dockerfile":
        return _generate_dockerfile(args)
    elif name == "diagnose_error":
        return _diagnose_error(args)
    elif name == "optimize_config":
        return _optimize_config(args)
    return f"Unknown tool: {name}"


def _analyze_project(files: list[str]) -> str:
    """Detect language from file list."""
    markers = {
        "requirements.txt": ("python", "pip"),
        "Pipfile": ("python", "pipenv"),
        "package.json": ("node", "npm"),
        "go.mod": ("go", "go modules"),
        "pom.xml": ("java", "maven"),
        "build.gradle": ("java", "gradle"),
        "Cargo.toml": ("rust", "cargo"),
        "Gemfile": ("ruby", "bundler"),
    }

    detected = []
    for f in files:
        if f in markers:
            lang, mgr = markers[f]
            detected.append(f"Detected {lang} project (package manager: {mgr})")

    if not detected:
        return "Could not auto-detect language. Please specify the language and framework."

    return "\n".join(detected) + "\n\nRecommendation: Use the CloudForge buildpack for automatic containerization."


def _generate_dockerfile(args: dict) -> str:
    """Generate a Dockerfile template."""
    lang = args.get("language", "python")
    framework = args.get("framework", "")
    entry = args.get("entrypoint", "main.py" if lang == "python" else "index.js")
    port = args.get("port", 8000 if lang == "python" else 3000)

    templates = {
        "python": f"""FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE {port}
CMD ["python", "{entry}"]""",
        "node": f"""FROM node:20-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --production
COPY . .
EXPOSE {port}
CMD ["node", "{entry}"]""",
        "go": f"""FROM golang:1.21-alpine AS builder
WORKDIR /app
COPY go.* ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 go build -o server .
FROM alpine:latest
COPY --from=builder /app/server /server
EXPOSE {port}
CMD ["/server"]""",
    }

    dockerfile = templates.get(lang, templates["python"])
    return f"Generated Dockerfile for {lang}:\n\n```dockerfile\n{dockerfile}\n```"


def _diagnose_error(args: dict) -> str:
    """Provide error diagnosis."""
    error = args.get("error_message", "")
    lang = args.get("language", "unknown")

    common_fixes = {
        "ModuleNotFoundError": "Missing dependency. Add the module to requirements.txt and rebuild.",
        "ENOENT": "File not found. Check that your entry point file exists and paths are correct.",
        "port already in use": "Port conflict. Set a different PORT environment variable.",
        "permission denied": "File permission issue. Ensure files are readable in the container.",
        "OOMKilled": "Out of memory. Increase the memory limit for the container.",
        "connection refused": "The app isn't listening on the expected port. Check PORT env var.",
    }

    for pattern, fix in common_fixes.items():
        if pattern.lower() in error.lower():
            return f"Diagnosis: {fix}\n\nFull error: {error}"

    return f"Error in {lang} app: {error}\n\nGeneral steps:\n1. Check the build log for the first error\n2. Verify all dependencies are listed\n3. Ensure the entry point file exists\n4. Check environment variables"


def _optimize_config(args: dict) -> str:
    """Suggest optimizations."""
    lang = args.get("language", "unknown")
    size = args.get("image_size_mb", 0)

    tips = [
        f"Language: {lang}",
        "Optimization suggestions:",
        "1. Use multi-stage builds to reduce final image size",
        "2. Use alpine-based images where possible",
        "3. Combine RUN commands to reduce layers",
        "4. Add .dockerignore to exclude unnecessary files",
        "5. Pin dependency versions for reproducible builds",
    ]

    if size > 500:
        tips.append(f"6. Current image ({size}MB) is large. Target < 200MB with multi-stage build.")

    return "\n".join(tips)
