# CloudRun IDE - Backend

FastAPI backend server for CloudRun IDE.

## 🚀 Quick Setup

### Prerequisites
- Python 3.11+
- Docker installed and running
- Google Gemini API key

### Installation

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY

# Run server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 📦 Key Dependencies

- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `docker` - Container management
- `google-generativeai` - AI integration
- `websockets` - Real-time communication
- `slowapi` - Rate limiting

## 🔧 Configuration

See `.env.example` for all available environment variables.

Required:
- `GEMINI_API_KEY` - Get from https://makersuite.google.com/app/apikey

---

**Status:** Dependencies configured ✅
