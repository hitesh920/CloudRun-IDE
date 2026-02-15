# Contributing to CloudRun IDE

Thanks for your interest in contributing!

## Development Setup

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # Add GROQ_API_KEY or GEMINI_API_KEY
uvicorn app.main:app --reload
```

Requires Docker running locally.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Dev server at `http://localhost:5173`, proxies API to `localhost:8000`.

## Commit Guidelines

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add new language support
fix: fix WebSocket reconnect on timeout
docs: update deployment guide
style: format executor.py
refactor: extract AI provider logic
test: add executor unit tests
chore: update Docker base images
```

## Pull Requests

1. Fork the repo and create a feature branch (`git checkout -b feat/my-feature`)
2. Make your changes
3. Test locally with `docker compose up -d --build`
4. Submit a PR with a clear description of what changed and why

## Project Structure

- **Backend** (`backend/`) — FastAPI, Docker SDK, AI assistant
- **Frontend** (`frontend/`) — React, Vite, Monaco Editor, Tailwind
- **Deployment** (`deployment/`) — Docker Compose, Nginx, deployment docs

## Adding a New Language

1. Add Docker image to `backend/app/utils/constants.py` → `DOCKER_IMAGES`
2. Add execution command to `EXECUTION_COMMANDS`
3. Add file extension to `FILE_EXTENSIONS`
4. Add code template to `CODE_TEMPLATES`
5. Add to `backend/app/models.py` → `LanguageEnum`
6. Add to `frontend/src/components/Editor.jsx` → `LANGUAGE_CONFIGS`
7. Add to welcome screen in `frontend/src/App.jsx`
8. If network needed, add to `NETWORK_ENABLED_LANGUAGES` in `docker_manager.py`

---

**Happy Contributing!**
