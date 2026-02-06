# CloudRun IDE - Project Structure

## 📁 Complete Directory Structure

```
cloudrun-ide/
│
├── README.md                           # Main project documentation
├── .gitignore                          # Git ignore rules
│
├── backend/                            # Backend server
│   ├── README.md                       # Backend documentation
│   ├── requirements.txt                # Python dependencies
│   ├── .env.example                    # Environment template
│   │
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                     # FastAPI entry point
│   │   ├── config.py                   # App configuration
│   │   ├── models.py                   # Pydantic models
│   │   │
│   │   ├── core/                       # Core functionality
│   │   │   ├── __init__.py
│   │   │   ├── docker_manager.py       # Docker operations
│   │   │   ├── executor.py             # Code execution
│   │   │   ├── websocket_manager.py    # WebSocket handling
│   │   │   └── rate_limiter.py         # Rate limiting
│   │   │
│   │   ├── services/                   # Business logic
│   │   │   ├── __init__.py
│   │   │   ├── ai_assistant.py         # Gemini integration
│   │   │   ├── dependency_detector.py  # Package detection
│   │   │   └── file_handler.py         # File operations
│   │   │
│   │   ├── api/                        # API routes
│   │   │   ├── __init__.py
│   │   │   ├── routes.py               # REST endpoints
│   │   │   └── websocket.py            # WebSocket endpoints
│   │   │
│   │   └── utils/                      # Utilities
│   │       ├── __init__.py
│   │       ├── helpers.py              # Helper functions
│   │       └── constants.py            # Constants
│   │
│   ├── dockerfiles/                    # Execution environments
│   │   ├── Dockerfile.python.arm64     # Python container
│   │   ├── Dockerfile.node.arm64       # Node.js container
│   │   ├── Dockerfile.java.arm64       # Java container
│   │   ├── Dockerfile.cpp.arm64        # C++ container
│   │   └── Dockerfile.ubuntu.arm64     # Ubuntu container
│   │
│   └── scripts/                        # Automation scripts
│       ├── build-images.sh             # Build Docker images
│       └── setup-vps.sh                # VPS setup
│
├── frontend/                           # Frontend application
│   ├── README.md                       # Frontend documentation
│   ├── package.json                    # Node dependencies
│   ├── vite.config.js                  # Vite configuration
│   ├── .env.example                    # Environment template
│   │
│   ├── public/
│   │   ├── index.html                  # HTML entry point
│   │   └── favicon.ico                 # App icon
│   │
│   └── src/
│       ├── App.jsx                     # Main component
│       ├── main.jsx                    # React entry
│       ├── index.css                   # Global styles
│       │
│       ├── components/                 # UI components
│       │   ├── WelcomeScreen.jsx       # Language selection
│       │   ├── Editor.jsx              # Code editor
│       │   ├── Console.jsx             # Output display
│       │   ├── Toolbar.jsx             # Action buttons
│       │   ├── FileExplorer.jsx        # File browser
│       │   ├── InputPanel.jsx          # User input
│       │   ├── AIAssistant.jsx         # AI panel
│       │   ├── DependencyPrompt.jsx    # Install prompt
│       │   ├── StatusBar.jsx           # Status display
│       │   ├── ThemeToggle.jsx         # Theme switcher
│       │   └── AdvancedModeToggle.jsx  # Mode toggle
│       │
│       ├── services/                   # API clients
│       │   ├── api.js                  # REST client
│       │   └── websocket.js            # WebSocket client
│       │
│       ├── hooks/                      # Custom hooks
│       │   ├── useWebSocket.js         # WebSocket hook
│       │   ├── useEditor.js            # Editor state
│       │   └── useTheme.js             # Theme state
│       │
│       ├── utils/                      # Utilities
│       │   ├── constants.js            # Constants
│       │   ├── templates.js            # Code templates
│       │   └── helpers.js              # Helper functions
│       │
│       └── styles/
│           └── tailwind.config.js      # Tailwind config
│
├── deployment/                         # Deployment configs
│   ├── nginx.conf                      # Nginx configuration
│   ├── cloudrun-ide.service            # Systemd service
│   ├── setup.sh                        # Deployment script
│   └── ssl-setup.sh                    # SSL configuration
│
└── docs/                               # Documentation
    ├── API.md                          # API documentation
    ├── DEPLOYMENT.md                   # Deployment guide
    ├── VPS-SETUP.md                    # VPS setup guide
    └── ARM64-NOTES.md                  # ARM64 considerations
```

## 📊 File Count

- **Backend:** ~25 files
- **Frontend:** ~25 files
- **Deployment:** ~5 files
- **Documentation:** ~5 files
- **Total:** ~60 files

## 🎯 Key Directories

### `/backend/app/core`
Core functionality: Docker management, code execution, WebSocket handling

### `/backend/app/services`
Business logic: AI assistance, dependency detection, file handling

### `/backend/app/api`
API layer: REST endpoints and WebSocket routes

### `/frontend/src/components`
UI components: All React components for the interface

### `/frontend/src/services`
API clients: Communication with backend

### `/frontend/src/hooks`
Custom React hooks: Reusable stateful logic

### `/deployment`
Production deployment: Nginx, systemd, setup scripts

---

**Note:** This structure will be populated incrementally through atomic commits.
