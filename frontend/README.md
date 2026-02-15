# CloudRun IDE — Frontend

React + Vite frontend with VS Code-style dark theme, Monaco Editor, and real-time WebSocket execution.

## Quick Setup

```bash
cd frontend
npm install
cp .env.example .env  # Optional, defaults work for local dev
npm run dev
```

Opens at `http://localhost:5173`. API calls proxy to `http://localhost:8000`.

## Features

- **Monaco Editor** — VS Code editing experience with syntax highlighting, auto-completion, bracket matching, and language-specific settings.
- **VS Code Dark Theme** — `#1e1e1e` editor, `#252526` panels, `#007acc` status bar. No gradients or fancy colors.
- **Resizable Bottom Panel** — Drag the divider between editor and bottom panel to resize.
- **Tab-based Bottom Panel** — Terminal, AI Assistant, and Input tabs.
- **AI Auto-fix** — "Fix Error" extracts corrected code from AI response and applies it directly to the editor.
- **Activity Bar** — Collapsible file explorer sidebar.
- **6 Languages** — Python, Node.js, Java, C++, HTML, Ubuntu Shell.

## Scripts

```bash
npm run dev      # Development server (port 5173)
npm run build    # Production build → dist/
npm run preview  # Preview production build
npm run lint     # ESLint
```

## Dependencies

| Package | Purpose |
|---------|---------|
| `react` 18 | UI framework |
| `vite` 5 | Build tool + dev server |
| `@monaco-editor/react` | Code editor |
| `tailwindcss` 3 | Utility-first CSS |
| `lucide-react` | Icons |

## Component Structure

```
src/
├── App.jsx                 # Main layout — welcome screen + editor view
├── main.jsx                # React entry point
├── index.css               # Tailwind base + custom scrollbar
├── components/
│   ├── Editor.jsx          # Monaco editor + LANGUAGE_CONFIGS
│   ├── Console.jsx         # Terminal output (color-coded)
│   ├── AIAssistant.jsx     # AI actions + auto-fix + code extraction
│   ├── FileExplorer.jsx    # File upload + drag-and-drop
│   ├── InputPanel.jsx      # stdin input
│   ├── DependencyPrompt.jsx # Missing package notification
│   ├── StatusBar.jsx       # Bottom status bar
│   └── ThemeToggle.jsx     # Theme switch (unused in current VS Code theme)
├── hooks/
│   ├── useWebSocket.js     # WebSocket execution hook
│   ├── useTheme.js         # Theme state
│   └── useKeyboardShortcuts.js # Ctrl+Enter, Ctrl+K, etc.
└── services/
    ├── websocket.js        # WebSocket client (singleton)
    └── api.js              # REST API client
```

## Configuration

Environment variables (`.env`):

```env
VITE_API_URL=http://localhost:8000   # Not used — relative URLs go through proxy
VITE_WS_URL=ws://localhost:8000      # Not used — auto-detected from page URL
```

In production, Nginx proxies `/api/*` and `/ws/*` to the backend. No env vars needed.

## Build

```bash
npm run build
# Output: dist/
# Served by Nginx in Docker
```

The `nginx.conf` handles:
- SPA routing (`try_files`)
- API proxy (`/api` → `backend:8000`)
- WebSocket proxy (`/ws` → `backend:8000`)
- Gzip compression
