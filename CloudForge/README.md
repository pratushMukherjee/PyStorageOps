# CloudForge

A self-hosted Platform-as-a-Service (PaaS) that deploys containerized applications via REST API and CLI, with an AI-powered deployment assistant for intelligent configuration, troubleshooting, and optimization.

![CI](https://github.com/YOUR_USERNAME/CloudForge/actions/workflows/ci.yml/badge.svg)

## Architecture

```
                    ┌──────────────┐
                    │   Dashboard  │ (HTML/CSS/JS)
                    └──────┬───────┘
                           │
                    ┌──────┴───────┐
                    │  Nginx Proxy │ (Routing + SSL)
                    └──┬───────┬───┘
                       │       │
              ┌────────┴──┐ ┌──┴──────────┐
              │  Go API   │ │ AI Service  │
              │  Server   │ │ (FastAPI)   │
              └────┬──────┘ └─────────────┘
                   │
              ┌────┴──────┐
              │  SQLite   │
              │  Database │
              └───────────┘
                   │
         ┌─────────┴──────────┐
         │   Docker Engine    │
         │ ┌──────┐ ┌──────┐ │
         │ │App 1 │ │App 2 │ │  (Deployed containers)
         │ └──────┘ └──────┘ │
         └────────────────────┘
```

## Features

- **Go API Server** — RESTful app management, deployment lifecycle, env vars, logging
- **Buildpack System** — Auto-detects Python, Node.js, Go, Java and generates Dockerfiles
- **AI Assistant** — OpenAI-powered agent with tool-calling for deployment help, error diagnosis, Dockerfile generation
- **Web Dashboard** — Real-time app management, deployment status, log viewer, AI chat
- **CLI Tool** — `cloudforge deploy`, `cloudforge logs`, `cloudforge ai` commands
- **CI/CD** — Jenkins pipeline + GitHub Actions (lint, test, build, deploy)
- **Reverse Proxy** — Nginx routing to deployed containers with dynamic upstream
- **Database** — SQLite with full schema for apps, deployments, env vars, logs

## Quick Start

```bash
# Setup
bash scripts/setup.sh

# Start full stack
docker-compose up -d

# Or run individually:
cd server && go run .               # API on :8080
uvicorn ai-service.main:app --port 8081  # AI on :8081

# Run tests
python -m pytest tests/ -v

# Use CLI
python cli/cloudforge.py apps
python cli/cloudforge.py create my-app python
python cli/cloudforge.py deploy <app-id>
python cli/cloudforge.py ai "How do I deploy a Flask app?"
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| POST | `/api/v1/apps` | Create app |
| GET | `/api/v1/apps` | List apps |
| GET | `/api/v1/apps/{id}` | Get app details |
| DELETE | `/api/v1/apps/{id}` | Delete app |
| POST | `/api/v1/apps/{id}/deploy` | Trigger deployment |
| GET | `/api/v1/apps/{id}/deployments` | List deployments |
| POST | `/api/v1/apps/{id}/rollback` | Rollback to previous |
| POST | `/api/v1/apps/{id}/env` | Set env variable |
| GET | `/api/v1/apps/{id}/env` | List env variables |
| GET | `/api/v1/apps/{id}/logs` | Get app logs |
| POST | `/api/v1/ai/chat` | AI assistant chat |
| POST | `/api/v1/ai/analyze` | Analyze project |
| POST | `/api/v1/ai/dockerfile` | Generate Dockerfile |
| POST | `/api/v1/ai/diagnose` | Diagnose error |

## Technology Stack

| Category | Technologies |
|----------|-------------|
| **Backend** | Go (chi router), Python (FastAPI) |
| **Frontend** | HTML, CSS, JavaScript |
| **Database** | SQLite |
| **AI** | OpenAI API, function calling, prompt engineering |
| **Containers** | Docker, docker-compose, multi-stage builds |
| **CI/CD** | Jenkins, GitHub Actions |
| **Networking** | Nginx reverse proxy |
| **Testing** | pytest, Go test |
| **CLI** | Python (httpx) |

## Project Structure

```
CloudForge/
├── server/          # Go API server (handlers, models, database, router, middleware)
├── ai-service/      # Python AI assistant (agent, tools, prompts, FastAPI)
├── dashboard/       # Web UI (HTML/CSS/JS)
├── cli/             # CLI tool (Python)
├── buildpacks/      # Language detection + Dockerfile templates
├── proxy/           # Nginx reverse proxy config
├── tests/           # pytest test suite
├── scripts/         # Bash automation
├── db/              # Database schema
├── Jenkinsfile      # Jenkins CI/CD pipeline
└── docker-compose.yml
```

## License

MIT
