# CloudRun IDE

**A Secure Multi-Language Cloud-Based Code Execution Sandbox with AI Assistance**

## 🎯 Overview

CloudRun IDE is a web-based integrated development environment that allows users to write, upload, and execute source code in multiple programming languages directly from a browser. The system provides secure, containerized cloud execution with real-time output streaming and AI-powered debugging support.

## ✨ Features

- 🚀 Multi-language support (Python, Java, C++, Node.js, HTML/CSS/JS)
- 🔒 Secure Docker container isolation
- ⚡ Real-time output streaming via WebSockets
- 🤖 AI-powered code assistance (Google Gemini)
- 📦 Automatic dependency detection and installation
- 📁 Multi-file upload support
- ⌨️ Interactive input handling
- 🎨 Light/Dark theme
- 🔧 Advanced Ubuntu execution mode

## 🏗️ Architecture

### Frontend
- **React + Vite** - Fast, modern UI framework
- **Monaco Editor** - VS Code-like editing experience
- **Tailwind CSS** - Utility-first styling
- **WebSockets** - Real-time communication

### Backend
- **Python + FastAPI** - High-performance async API
- **Docker SDK** - Container orchestration
- **WebSockets** - Real-time output streaming
- **Google Gemini API** - AI assistance

## 📁 Project Structure

```
cloudrun-ide/
├── backend/           # FastAPI backend server
├── frontend/          # React frontend application
├── deployment/        # Deployment configurations
└── docs/              # Documentation
```

## 🚀 Quick Start

Coming soon...

## 🛠️ Technology Stack

**Frontend:**
- React 18
- Vite 5
- Monaco Editor
- Tailwind CSS

**Backend:**
- Python 3.11
- FastAPI
- Docker SDK
- Google Generative AI

**Infrastructure:**
- Docker containers
- ARM64 compatible (Oracle Cloud)

## 🔒 Security

- Isolated Docker containers per execution
- Resource limits (CPU, memory, timeout)
- Network isolation
- Rate limiting

## 📄 License

MIT License

## 👨‍💻 Author

CloudRun IDE - 2025

---

**Status:** In Development 🚧
