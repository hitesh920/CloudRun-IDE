# CloudRun IDE - Frontend

React + Vite frontend application for CloudRun IDE.

## 🏗️ Structure

```
frontend/
├── public/
│   └── index.html
│
├── src/
│   ├── App.jsx              # Main application component
│   ├── main.jsx             # React entry point
│   ├── index.css            # Global styles
│   │
│   ├── components/          # React components
│   │   ├── WelcomeScreen.jsx
│   │   ├── Editor.jsx
│   │   ├── Console.jsx
│   │   ├── Toolbar.jsx
│   │   ├── FileExplorer.jsx
│   │   ├── InputPanel.jsx
│   │   ├── AIAssistant.jsx
│   │   ├── DependencyPrompt.jsx
│   │   ├── StatusBar.jsx
│   │   ├── ThemeToggle.jsx
│   │   └── AdvancedModeToggle.jsx
│   │
│   ├── services/            # API clients
│   │   ├── api.js
│   │   └── websocket.js
│   │
│   ├── hooks/               # Custom React hooks
│   │   ├── useWebSocket.js
│   │   ├── useEditor.js
│   │   └── useTheme.js
│   │
│   ├── utils/               # Utilities
│   │   ├── constants.js
│   │   ├── templates.js
│   │   └── helpers.js
│   │
│   └── styles/
│       └── tailwind.config.js
│
├── package.json
└── vite.config.js
```

## 🚀 Setup

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env and set VITE_API_URL
```

### 3. Run Development Server

```bash
npm run dev
```

The app will be available at `http://localhost:5173`

## 🔧 Configuration

Environment variables in `.env`:
- `VITE_API_URL` - Backend API URL (default: http://localhost:8000)
- `VITE_WS_URL` - WebSocket URL (default: ws://localhost:8000)

## 🏗️ Build for Production

```bash
npm run build
```

Build output will be in `dist/` directory.

## 📦 Key Dependencies

- **React 18** - UI framework
- **Vite 5** - Build tool
- **@monaco-editor/react** - Code editor
- **Tailwind CSS** - Styling
- **Lucide React** - Icons

## 🧪 Development

```bash
npm run dev      # Start dev server
npm run build    # Build for production
npm run preview  # Preview production build
npm run lint     # Run linter
```

---

**Status:** In Development 🚧
