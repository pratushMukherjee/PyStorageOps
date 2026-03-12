# CloudForge - IBM SW Developer Intern Portfolio Project

## Project Overview
A self-hosted Platform-as-a-Service (PaaS) that deploys containerized applications
via REST API and CLI, with an AI-powered deployment assistant for intelligent
configuration, troubleshooting, and optimization. Think a mini Heroku with AI.

**Target Role:** IBM SW Developer Intern (Platform Engineering / Cloud)

---

## Architecture

```
CloudForge/
├── .github/workflows/ci.yml         # GitHub Actions CI/CD pipeline
├── Jenkinsfile                       # Jenkins pipeline definition
├── server/                           # Go API server (client-server arch)
│   ├── main.go
│   ├── go.mod / go.sum
│   ├── handlers/
│   │   ├── apps.go                   # App CRUD endpoints
│   │   ├── deployments.go            # Deployment lifecycle
│   │   ├── logs.go                   # Log streaming
│   │   └── health.go                 # Health check
│   ├── models/
│   │   ├── app.go                    # App model
│   │   └── deployment.go             # Deployment model
│   ├── middleware/
│   │   └── auth.go                   # API key authentication
│   ├── database/
│   │   └── db.go                     # SQLite database layer
│   └── router/
│       └── router.go                 # Route registration
├── ai-service/                       # Python AI deployment assistant
│   ├── main.py                       # FastAPI service
│   ├── requirements.txt
│   ├── agent.py                      # AI agent with tool-calling
│   ├── tools.py                      # Deployment analysis tools
│   └── prompts.py                    # Prompt templates
├── dashboard/                        # Web UI (vanilla JS + HTML/CSS)
│   ├── index.html
│   ├── style.css
│   └── app.js
├── cli/                              # Python CLI tool
│   ├── cloudforge.py                 # CLI entry point
│   └── requirements.txt
├── proxy/                            # Reverse proxy / routing
│   └── nginx.conf                    # Nginx routing config
├── buildpacks/                       # Language detection & Dockerfiles
│   ├── detect.py                     # Language auto-detection
│   ├── python/Dockerfile
│   ├── node/Dockerfile
│   ├── go/Dockerfile
│   └── java/Dockerfile
├── db/
│   └── schema.sql                    # Database schema
├── scripts/
│   ├── setup.sh                      # Environment setup
│   └── demo.sh                       # Demo deployment script
├── tests/
│   ├── test_api.py                   # API integration tests
│   ├── test_buildpacks.py            # Buildpack detection tests
│   ├── test_ai_agent.py              # AI service tests
│   └── conftest.py
├── docker-compose.yml                # Full platform stack
├── Dockerfile.server                 # Go server container
├── Dockerfile.ai                     # AI service container
└── README.md
```

---

## Phases & Commit Plan

### Phase 1: Go API Server Foundation
**Skills:** Go, client-server architecture, REST APIs, databases, SQL

- Go HTTP server with chi router
- App CRUD endpoints (create, list, get, delete)
- Deployment endpoints (deploy, status, rollback)
- SQLite database with migrations
- API key authentication middleware
- Health check endpoint
- **Commit:** "feat: Go API server with app management and deployment endpoints"

### Phase 2: Buildpack System & Container Deployment
**Skills:** Docker, virtualization, Python, multi-language support

- Language auto-detection (Python, Node, Go, Java)
- Per-language Dockerfile templates (buildpacks)
- Container build and run orchestration
- Port allocation and management
- **Commit:** "feat: buildpack system with auto-detection and container deployment"

### Phase 3: Database Layer & Deployment Lifecycle
**Skills:** SQL, databases, application state management

- Full SQLite schema (apps, deployments, env vars, logs)
- Deployment state machine (pending -> building -> running -> stopped)
- Environment variable management
- Deployment history and rollback support
- **Commit:** "feat: database schema, deployment lifecycle, and rollback support"

### Phase 4: AI Deployment Assistant
**Skills:** Generative AI, prompt engineering, Python, FastAPI, tool-calling

- FastAPI AI service with OpenAI integration
- Deployment analysis agent with tool-calling
- Dockerfile generation from project description
- Error diagnosis and fix suggestions
- Optimization recommendations
- **Commit:** "feat: AI-powered deployment assistant with tool-calling agent"

### Phase 5: Web Dashboard UI
**Skills:** HTML/CSS/JS, wireframes to UI, responsive design

- App management dashboard (list, create, delete)
- Deployment status with real-time updates
- Log viewer
- AI assistant chat panel
- Responsive design
- **Commit:** "feat: web dashboard with app management, logs, and AI chat"

### Phase 6: CLI Tool
**Skills:** Python, developer tooling, UX

- `cloudforge deploy` — deploy from current directory
- `cloudforge apps` — list/create/delete apps
- `cloudforge logs` — stream application logs
- `cloudforge ai` — ask AI for deployment help
- **Commit:** "feat: CLI tool for app deployment and management"

### Phase 7: Reverse Proxy & Networking
**Skills:** Networking protocols, server architecture, Nginx

- Nginx reverse proxy configuration
- Dynamic routing to deployed containers
- SSL/TLS termination config
- **Commit:** "feat: Nginx reverse proxy with dynamic container routing"

### Phase 8: CI/CD Pipelines
**Skills:** Jenkins, GitHub Actions, DevOps, continuous delivery

- Jenkinsfile with build/test/deploy stages
- GitHub Actions CI (lint, test, build Docker images)
- Automated deployment pipeline
- **Commit:** "feat: Jenkins and GitHub Actions CI/CD pipelines"

### Phase 9: Docker Compose & Tests
**Skills:** Docker, testing, integration, virtualization

- docker-compose.yml for full platform stack
- API integration tests
- Buildpack detection tests
- AI service tests
- Setup and demo scripts
- **Commit:** "feat: docker-compose stack, integration tests, and automation scripts"

### Phase 10: Documentation
**Skills:** Communication, technical writing

- Comprehensive README with architecture diagram
- API documentation with examples
- **Commit:** "docs: README with architecture, API docs, and usage examples"

---

## Key Technologies Demonstrated

| Category | Technologies |
|----------|-------------|
| Languages | Go, Python, JavaScript, SQL, Bash |
| Server Architecture | Go HTTP server, client-server, REST APIs |
| Cloud/PaaS | Container deployment, buildpacks, port management |
| AI Integration | OpenAI API, tool-calling agent, prompt engineering |
| Frontend | HTML, CSS, JavaScript (dashboard UI) |
| Databases | SQLite, schema design, migrations |
| Virtualization | Docker, docker-compose, multi-stage builds |
| DevOps/CI/CD | Jenkins, GitHub Actions, Nginx |
| Networking | Reverse proxy, routing, SSL config |
| Testing | pytest, integration tests, API tests |

---

## How This Maps to IBM Job Requirements

**Required Skills:**
- Client-server architecture (Go API server) ✓
- APIs — clean, well-documented (OpenAPI/Swagger) ✓
- DevOps tools — Git, Jenkins ✓
- Databases (SQLite, schema design) ✓
- Servers and applications ✓
- Agile development (phased commits, CI/CD) ✓

**Preferred Skills:**
- Cloud development with CD pipeline (Jenkins + GitHub Actions) ✓
- Generative AI in dev environment + prompt engineering ✓
- Multiple languages: Go, Python, SQL ✓
- Virtualization concepts (Docker containers, buildpacks) ✓
- IaaS/PaaS/SaaS (self-hosted PaaS platform) ✓
- Wireframes to functional UI (web dashboard) ✓
- AI integration into platform solutions ✓
