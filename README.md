# CloudRun IDE 🚀

A powerful, cloud-based IDE for executing code in multiple programming languages with real-time output streaming, AI assistance, and Docker isolation.

![CloudRun IDE](https://img.shields.io/badge/version-1.0.0-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## ✨ Features

### 🎯 Core Functionality
- **Multi-language Support**: Python, Node.js, Java, C++, HTML/CSS/JS
- **Real-time Output Streaming**: WebSocket-based live execution feedback
- **Docker Isolation**: Secure code execution in isolated containers
- **File Upload**: Support for multi-file projects
- **Input Handling**: Interactive programs with stdin support

### 🤖 AI-Powered
- **Fix Errors**: AI suggests fixes for bugs
- **Explain Code**: Get step-by-step explanations
- **Optimize Code**: Receive optimization suggestions
- **Error Explanations**: Understand what went wrong
- Powered by **Google Gemini**

### 🎨 User Experience
- **Monaco Editor**: VS Code-like editing experience
- **Light/Dark Theme**: Toggle with persistent preference
- **Keyboard Shortcuts**: Ctrl+Enter to run, Ctrl+K to clear
- **Status Bar**: Real-time execution metrics
- **Dependency Detection**: Auto-detect missing packages

---

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Node.js 20+ (for local development)
- Python 3.11+ (for local development)

### Installation

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd cloudrun-ide
   ```

2. **Setup environment:**
   ```bash
   cp backend/.env.example backend/.env
   # Edit backend/.env and add your GEMINI_API_KEY
   ```

3. **Start with Docker Compose:**
   ```bash
   docker-compose up -d
   ```

4. **Access the application:**
   - Frontend: http://localhost
   - API Docs: http://localhost:8000/docs

---

## 💻 Local Development

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

---

## 🎮 Usage

1. **Select a Language**: Choose from Python, Node.js, Java, C++, or HTML/CSS/JS
2. **Write Code**: Use the Monaco editor with syntax highlighting
3. **Upload Files** (optional): Add dependencies or multi-file projects
4. **Add Input** (optional): Provide stdin for interactive programs
5. **Run Code**: Click "Run Code" or press `Ctrl+Enter`
6. **Get AI Help**: Use AI assistant to fix errors or optimize code

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl + Enter` | Run code |
| `Ctrl + K` | Clear console |
| `Ctrl + S` | Save code |
| `Ctrl + Shift + S` | Stop execution |

---

## 🌐 Supported Languages

| Language | Version | Package Manager |
|----------|---------|-----------------|
| Python | 3.11 | pip |
| Node.js | 20 | npm |
| Java | 21 | - |
| C++ | GCC 12 | - |
| HTML/CSS/JS | - | - |

---

## 🤖 AI Features

### Prerequisites
Get a free Gemini API key from [Google AI Studio](https://makersuite.google.com/app/apikey)

### Available Actions
1. **Fix Error**: AI analyzes error and provides corrected code
2. **Explain Error**: Understand what the error means
3. **Explain Code**: Get step-by-step breakdown
4. **Optimize Code**: Receive performance suggestions

---

## 🚢 Deployment

See [deployment/README.md](deployment/README.md) for detailed instructions.

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit changes: `git commit -m 'Add feature'`
4. Push to branch: `git push origin feature-name`
5. Submit a pull request

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Built with ❤️ for developers everywhere**
