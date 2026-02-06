# CloudRun IDE - Frontend

React + Vite frontend application for CloudRun IDE.

## 🚀 Quick Setup

### Prerequisites
- Node.js 18+ and npm

### Installation

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env
# Edit .env if needed (default values work for local dev)

# Run development server
npm run dev
```

The app will be available at: `http://localhost:5173`

## 📦 Key Dependencies

**Core:**
- `react` - UI framework
- `vite` - Build tool
- `@monaco-editor/react` - Code editor
- `tailwindcss` - Styling
- `lucide-react` - Icons

## 🔧 Available Scripts

```bash
npm run dev      # Start development server
npm run build    # Build for production
npm run preview  # Preview production build
npm run lint     # Run ESLint
```

## 🎨 Styling

This project uses Tailwind CSS with custom configuration for:
- Dark mode support
- Custom color palette
- Monospace font for code

## 🔧 Configuration

Environment variables (`.env`):
- `VITE_API_URL` - Backend API URL (default: http://localhost:8000)
- `VITE_WS_URL` - WebSocket URL (default: ws://localhost:8000)

## 📝 Build Output

Production build outputs to `dist/` directory.

---

**Status:** Dependencies configured ✅
