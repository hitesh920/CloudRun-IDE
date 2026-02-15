# CloudRun IDE

A cloud-based code execution IDE with real-time output streaming, AI-powered code assistance, and Docker isolation. Built with FastAPI, React, and Monaco Editor.

![Version](https://img.shields.io/badge/version-0.2.0-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## Features

**Code Execution** — Write and run code in Python, Node.js, Java, C++, HTML, and Ubuntu Shell directly in the browser. Each execution runs in an isolated Docker container with resource limits and automatic cleanup.

**Real-time Streaming** — Output streams live over WebSocket as your program runs. See stdout, stderr, status updates, and execution results in real time.

**AI Assistant** — Powered by Groq (llama-3.3-70b) with Gemini fallback. Fix errors with one click and the corrected code is auto-applied to the editor. Also supports explaining errors, explaining code, and optimization suggestions.

**VS Code-style UI** — Dark theme interface with Monaco Editor, tab-based bottom panel (Terminal / AI Assistant / Input), activity bar, collapsible file explorer, resizable panels, and a blue status bar.

**Ubuntu Shell** — Run system commands (`apt-get`, `curl`, `ls`, `uname`, etc.) in a network-enabled Ubuntu 22.04 container.

**File Upload** — Drag-and-drop or browse to upload additional files for multi-file projects. Files are copied into the execution container.

**Dependency Detection** — Automatically detects missing Python (pip) and Node.js (npm) packages from error output and suggests installation.

## Supported Languages

| Language | Docker Image | File | Network |
|----------|-------------|------|---------|
| Python 3.11 | `python:3.11-slim` | `main.py` | Disabled |
| Node.js 20 | `node:20-alpine` | `index.js` | Disabled |
| Java 21 | `eclipse-temurin:21-jdk` | `Main.java` | Disabled |
| C++ (GCC 12) | `gcc:12` | `main.cpp` | Disabled |
| HTML/CSS/JS | None (preview only) | `index.html` | N/A |
| Ubuntu Shell | `ubuntu:22.04` | `script.sh` | **Enabled** |

## Quick Start

### Prerequisites

- Docker & Docker Compose
- A free [Groq API key](https://console.groq.com/keys) (recommended) or [Gemini API key](https://makersuite.google.com/app/apikey)

### Setup

```bash
git clone https://github.com/hitesh920/CloudRun.git
cd CloudRun

# Configure environment
cp backend/.env.example backend/.env
# Edit backend/.env — add GROQ_API_KEY (and/or GEMINI_API_KEY)

# Start
docker compose up -d

# View logs
docker compose logs -f
```

Open **http://localhost** (or your server IP) in a browser.

### First-time Setup

The first launch pulls Docker images for all languages (~2-3 minutes). Subsequent starts are instant.

## Architecture

```
┌─────────────────────────────────────────┐
│  Browser (React + Monaco Editor)        │
│  Port 80 (Nginx)                        │
├─────────────────────────────────────────┤
│  Nginx Reverse Proxy                    │
│  /api/* → backend:8000                  │
│  /ws/*  → backend:8000 (WebSocket)      │
├─────────────────────────────────────────┤
│  FastAPI Backend (Port 8000)            │
│  REST API + WebSocket + AI Assistant    │
├─────────────────────────────────────────┤
│  Docker Engine                          │
│  Isolated containers per execution      │
└─────────────────────────────────────────┘
```

**Backend** — FastAPI with WebSocket streaming, Docker SDK for container management, multi-provider AI assistant (Groq + Gemini).

**Frontend** — React 18, Vite, Monaco Editor, Tailwind CSS. VS Code dark theme with resizable panels.

**Execution** — Each code run creates a temporary Docker container with CPU/memory limits, streams logs in real time, then cleans up automatically.

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl + Enter` | Run code |
| `Ctrl + Shift + S` | Stop execution |
| `Ctrl + K` | Clear console |
| `Ctrl + S` | Save code to localStorage |

## AI Assistant

The AI assistant uses Groq (free, fast) as the primary provider with Google Gemini as fallback.

| Action | What it does |
|--------|-------------|
| **Fix Error** | Analyzes the error, generates corrected code, and **auto-applies it to the editor** |
| **Explain Error** | Explains what went wrong in simple terms |
| **Explain Code** | Step-by-step breakdown of your code |
| **Optimize** | Suggests improvements and auto-applies optimized code |

### Configuration

Add one or both API keys to `backend/.env`:

```env
GROQ_API_KEY=gsk_...        # Free at https://console.groq.com/keys
GEMINI_API_KEY=AIza...       # Free at https://makersuite.google.com/app/apikey
```

Groq is tried first. If unavailable, Gemini is used as fallback.

## Project Structure

```
CloudRun/
├── backend/
│   ├── app/
│   │   ├── api/            # REST routes + WebSocket endpoints
│   │   ├── core/           # Docker manager + code executor
│   │   ├── services/       # AI assistant + dependency detector
│   │   ├── utils/          # Constants, helpers
│   │   ├── config.py       # Settings from .env
│   │   ├── models.py       # Pydantic models
│   │   └── main.py         # FastAPI app entry point
│   ├── Dockerfile
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/     # Editor, Console, AIAssistant, etc.
│   │   ├── hooks/          # useWebSocket, useTheme, useKeyboardShortcuts
│   │   ├── services/       # WebSocket + REST API clients
│   │   └── App.jsx         # Main layout (VS Code theme)
│   ├── nginx.conf          # Reverse proxy config
│   ├── Dockerfile
│   └── package.json
├── deployment/
│   └── README.md           # Deployment guide
├── docker-compose.yml
└── README.md
```

## Environment Variables

See `backend/.env.example` for all options:

| Variable | Default | Description |
|----------|---------|-------------|
| `GROQ_API_KEY` | — | Groq API key (primary AI provider) |
| `GEMINI_API_KEY` | — | Google Gemini API key (fallback) |
| `MAX_EXECUTION_TIME` | `60` | Max seconds per execution |
| `MAX_MEMORY` | `1g` | Memory limit per container |
| `RATE_LIMIT_PER_MINUTE` | `10` | API rate limit |
| `PRE_PULL_IMAGES` | `True` | Pull Docker images on startup |

## Deployment

For VPS deployment (Oracle Cloud, AWS, etc.), see [deployment/README.md](deployment/README.md).

Quick summary:

```bash
# On your VPS
git clone https://github.com/hitesh920/CloudRun.git
cd CloudRun
cp backend/.env.example backend/.env
nano backend/.env  # Add API keys
docker compose up -d
```

Open `http://<your-server-ip>` in a browser.

## Development

### Backend (local)

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # Add API keys
uvicorn app.main:app --reload --port 8000
```

### Frontend (local)

```bash
cd frontend
npm install
npm run dev
# Opens at http://localhost:5173, proxies API to localhost:8000
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT License — see [LICENSE](LICENSE).

---

**Built by [hitesh920](https://github.com/hitesh920)**
