# CloudRun IDE — Folder Structure

## Full Project Tree

```
CloudRun/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                 # FastAPI app, lifespan, startup
│   │   ├── config.py               # Settings from .env
│   │   ├── models.py               # Pydantic models, LanguageEnum
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── routes.py           # REST endpoints (/api/*)
│   │   │   └── websocket.py        # WebSocket endpoint (/ws/execute)
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── docker_manager.py   # Container create/start/stop/cleanup
│   │   │   ├── executor.py         # Code execution + log streaming
│   │   │   └── websocket_manager.py# Connection tracking
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── ai_assistant.py     # Groq + Gemini AI providers
│   │   │   └── dependency_detector.py # Missing package detection
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── constants.py        # Docker images, commands, templates
│   │       └── helpers.py          # ID generation, validation, etc.
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── .env.example
│   ├── .dockerignore
│   ├── .gitignore
│   └── README.md
├── frontend/
│   ├── public/
│   │   └── vite.svg
│   ├── src/
│   │   ├── main.jsx                # React entry point
│   │   ├── App.jsx                 # Main layout (VS Code theme)
│   │   ├── index.css               # Tailwind + custom styles
│   │   ├── components/
│   │   │   ├── Editor.jsx          # Monaco editor + language configs
│   │   │   ├── Console.jsx         # Terminal output
│   │   │   ├── AIAssistant.jsx     # AI actions + auto-fix
│   │   │   ├── FileExplorer.jsx    # File upload / drag-drop
│   │   │   ├── InputPanel.jsx      # stdin input
│   │   │   ├── DependencyPrompt.jsx# Missing package notification
│   │   │   ├── StatusBar.jsx       # Bottom status bar
│   │   │   └── ThemeToggle.jsx     # Theme switch
│   │   ├── hooks/
│   │   │   ├── useWebSocket.js     # WebSocket execution hook
│   │   │   ├── useTheme.js         # Theme state management
│   │   │   └── useKeyboardShortcuts.js # Ctrl+Enter, etc.
│   │   └── services/
│   │       ├── websocket.js        # WebSocket client singleton
│   │       └── api.js              # REST API client
│   ├── index.html
│   ├── nginx.conf                  # Production reverse proxy
│   ├── Dockerfile
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   ├── .env.example
│   ├── .dockerignore
│   ├── .gitignore
│   └── README.md
├── deployment/
│   └── README.md                   # Deployment guide
├── docker-compose.yml
├── CONTRIBUTING.md
├── FOLDER-STRUCTURE.md
├── LICENSE
├── .gitignore
└── README.md
```

## Create from Scratch

```bash
mkdir -p CloudRun/{backend/app/{api,core,services,utils},frontend/{public,src/{components,hooks,services}},deployment}
```
