# CloudRun IDE — Backend

FastAPI backend for CloudRun IDE. Handles code execution in Docker containers, real-time WebSocket streaming, user authentication, and multi-provider AI assistance.

## Quick Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env      # Add GROQ_API_KEY and/or GEMINI_API_KEY, set JWT_SECRET
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Requires Docker running locally for code execution.

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check |
| `GET` | `/api/status` | Full system status |
| `GET` | `/api/languages` | Supported languages |
| `GET` | `/api/templates` | Code templates for all languages |
| `GET` | `/api/templates/{lang}` | Template for specific language |
| `POST` | `/api/execute` | Execute code (sync) |
| `POST` | `/api/execute/stop/{id}` | Stop running execution |
| `POST` | `/api/ai/assist` | AI code assistance |
| `GET` | `/api/ai/status` | AI provider status |
| `POST` | `/api/auth/register` | Create new account |
| `POST` | `/api/auth/login` | Login (username/email + password) |
| `GET` | `/api/auth/me` | Get current user profile |
| `POST` | `/api/auth/verify` | Verify JWT token |
| `WS` | `/ws/execute` | WebSocket streaming execution |

Interactive docs at `http://localhost:8000/docs`.

## Supported Languages

| Language | Image | Execution |
|----------|-------|-----------|
| Python 3.11 | `python:3.11-slim` | `python -u main.py` |
| Node.js 20 | `node:20-alpine` | `node index.js` |
| Java 21 | `eclipse-temurin:21-jdk` | `javac + java` |
| C++ (GCC 12) | `gcc:12` | `g++ + run` |
| HTML | None | Preview returned as WebSocket message |
| Ubuntu Shell | `ubuntu:22.04` | `bash -c <code>` (network enabled) |

## Authentication

JWT-based auth with SQLite storage (zero config):

- **Register** — `POST /api/auth/register` with username, email, password
- **Login** — `POST /api/auth/login` with username/email + password
- **Verify** — `POST /api/auth/verify` with `Authorization: Bearer <token>` header
- **Password hashing** — PBKDF2-SHA256 with 100,000 iterations
- **Token expiry** — 7 days

Database: SQLite at `data/cloudrun.db` (auto-created on startup). Supports PostgreSQL via `DATABASE_URL` env var.

## AI Assistant

Multi-provider with automatic fallback:

1. **Groq** (primary) — Free, fast. Uses `llama-3.3-70b-versatile`.
2. **Gemini** (fallback) — Google's `gemini-2.0-flash`.

Actions: `fix_error`, `explain_error`, `explain_code`, `optimize_code`.

## Configuration

All settings via environment variables (`.env` file):

```env
# AI (at least one required for AI features)
GROQ_API_KEY=gsk_...
GEMINI_API_KEY=AIza...

# Auth & Database
JWT_SECRET=change-me-to-random-string
DATABASE_URL=              # Default: SQLite. Set for PostgreSQL.

# Server
HOST=0.0.0.0
PORT=8000
DEBUG=false

# Execution limits
MAX_EXECUTION_TIME=30
MAX_MEMORY=256m
MAX_CPU_QUOTA=50000
MAX_CPU_PERIOD=100000

# Misc
CORS_ORIGINS=*
MAX_REQUESTS_PER_MINUTE=30
PRE_PULL_IMAGES=false
```

## Key Dependencies

- `fastapi` + `uvicorn` — Web framework and ASGI server
- `docker` — Docker SDK for container management
- `sqlalchemy` — Database ORM (SQLite / PostgreSQL)
- `google-genai` — Gemini AI integration
- `requests` — Groq API calls
- `websockets` — Real-time streaming
- `pydantic` + `pydantic-settings` — Data validation and config
- `slowapi` — Rate limiting

## Architecture

```
app/
├── main.py              # FastAPI app, lifespan, CORS
├── config.py            # Settings from .env
├── models.py            # Pydantic models (LanguageEnum, etc.)
├── api/
│   ├── auth.py          # Auth endpoints (register/login/verify)
│   ├── routes.py        # REST API endpoints
│   └── websocket.py     # WebSocket execution endpoint
├── core/
│   ├── database.py      # SQLAlchemy models + SQLite/PostgreSQL
│   ├── docker_manager.py # Container lifecycle management
│   ├── executor.py       # Code execution + package install + streaming
│   └── websocket_manager.py # Connection tracking
├── services/
│   ├── ai_assistant.py   # Multi-provider AI (Groq + Gemini)
│   └── dependency_detector.py # Missing package detection
└── utils/
    ├── constants.py      # Docker images, commands, templates
    └── helpers.py        # Utility functions
```
