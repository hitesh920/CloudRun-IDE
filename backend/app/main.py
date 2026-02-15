"""
CloudRun IDE - FastAPI Application
Main entry point for the backend server.
"""

import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings


def print_banner():
    """Print startup banner."""
    print("")
    print("=" * 60)
    print("  ☁️  CloudRun IDE Backend")
    print("=" * 60)
    print("")


def check_docker():
    """Check Docker connectivity and pre-pull images."""
    from app.core.docker_manager import get_docker_manager
    from app.utils.constants import DOCKER_IMAGES
    
    try:
        dm = get_docker_manager()
        print("✅ Docker connection: OK")
        
        if settings.PRE_PULL_IMAGES:
            print("")
            print("📦 Pre-pulling Docker images...")
            for lang, image in DOCKER_IMAGES.items():
                try:
                    dm.client.images.get(image)
                    print(f"  ✅ {lang:10s} → {image} (cached)")
                except Exception:
                    print(f"  📥 {lang:10s} → {image} (pulling...)")
                    try:
                        dm.client.images.pull(image)
                        print(f"  ✅ {lang:10s} → {image} (pulled)")
                    except Exception as e:
                        print(f"  ❌ {lang:10s} → {image} (failed: {e})")
            print("📦 Image pre-pull complete")
        
        return True
    except Exception as e:
        print(f"❌ Docker connection: FAILED ({e})")
        print("   ⚠️  Code execution will not work without Docker!")
        return False


def check_ai():
    """Check AI assistant availability."""
    from app.services.ai_assistant import ai_assistant
    
    if ai_assistant.is_enabled():
        print("✅ AI Assistant (Gemini): OK")
    else:
        print("⚠️  AI Assistant (Gemini): DISABLED (no API key)")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan - startup and shutdown."""
    # === STARTUP ===
    print_banner()
    
    print("🔧 Configuration:")
    print(f"   Host:        {settings.HOST}:{settings.PORT}")
    print(f"   Debug:       {settings.DEBUG}")
    print(f"   CORS:        {settings.CORS_ORIGINS}")
    print(f"   Max Timeout: {settings.MAX_EXECUTION_TIME}s")
    print(f"   Max Memory:  {settings.MAX_MEMORY}")
    print("")
    
    print("🔍 Running startup checks...")
    print("")
    
    # Check Docker
    docker_ok = check_docker()
    print("")
    
    # Check AI
    check_ai()
    print("")
    
    # Print endpoints
    print("🌐 Endpoints:")
    print(f"   📝 API Docs:   http://{settings.HOST}:{settings.PORT}/docs")
    print(f"   🔌 WebSocket:  ws://{settings.HOST}:{settings.PORT}/ws/execute")
    print(f"   ❤️  Health:     http://{settings.HOST}:{settings.PORT}/health")
    print(f"   📊 Status:     http://{settings.HOST}:{settings.PORT}/api/status")
    print("")
    
    if docker_ok:
        print("=" * 60)
        print("  🚀 CloudRun IDE is READY and RUNNING!")
        print("=" * 60)
    else:
        print("=" * 60)
        print("  ⚠️  CloudRun IDE started with WARNINGS")
        print("=" * 60)
    
    print("")
    
    yield
    
    # === SHUTDOWN ===
    print("")
    print("👋 CloudRun IDE Backend shutting down...")
    
    # Cleanup orphaned containers
    try:
        from app.core.docker_manager import get_docker_manager
        dm = get_docker_manager()
        containers = dm.client.containers.list(
            filters={"name": "cloudrun_"},
            all=True
        )
        if containers:
            print(f"🧹 Cleaning up {len(containers)} orphaned container(s)...")
            for c in containers:
                try:
                    c.remove(force=True)
                    print(f"   ✅ Removed: {c.name}")
                except Exception:
                    pass
    except Exception:
        pass
    
    print("👋 Goodbye!")


# Create FastAPI app instance
app = FastAPI(
    title="CloudRun IDE API",
    description="A secure multi-language cloud-based code execution platform",
    version="0.2.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
from app.api.routes import router as api_router
from app.api.websocket import router as ws_router

app.include_router(api_router)
app.include_router(ws_router)


@app.get("/")
async def root():
    """Root endpoint - API info."""
    return {
        "name": "CloudRun IDE API",
        "version": "0.2.0",
        "status": "running",
        "docs": "/docs",
        "websocket": "/ws/execute",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    docker_ok = False
    try:
        from app.core.docker_manager import get_docker_manager
        dm = get_docker_manager()
        dm.client.ping()
        docker_ok = True
    except Exception:
        pass
    
    from app.services.ai_assistant import ai_assistant
    
    return {
        "status": "healthy" if docker_ok else "degraded",
        "version": "0.2.0",
        "docker": "connected" if docker_ok else "disconnected",
        "ai": "enabled" if ai_assistant.is_enabled() else "disabled",
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
