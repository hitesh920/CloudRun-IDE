"""
CloudRun IDE - Main Application
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 CloudRun IDE Backend Starting...")

    # Initialize database
    try:
        from app.core.database import create_tables
        create_tables()
    except Exception as e:
        print(f"⚠️ Database init error: {e}")

    # Initialize Docker
    try:
        from app.core.docker_manager import get_docker_manager
        docker_mgr = get_docker_manager()
        cleaned = docker_mgr.cleanup_orphaned_containers()
        if cleaned > 0:
            print(f"🧹 Cleaned up {cleaned} orphaned containers")
        if settings.PRE_PULL_IMAGES:
            from app.utils.constants import DOCKER_IMAGES
            print("📥 Pre-pulling Docker images...")
            for lang, image in DOCKER_IMAGES.items():
                try:
                    docker_mgr.pull_image(lang)
                except Exception as e:
                    print(f"  ⚠️ Failed to pull {image}: {e}")
    except Exception as e:
        print(f"⚠️ Docker init warning: {e}")

    print("✅ CloudRun IDE Backend Ready!")
    print(f"   📡 API: http://{settings.HOST}:{settings.PORT}")
    yield
    print("👋 CloudRun IDE Backend Shutting Down...")


app = FastAPI(title="CloudRun IDE", version="0.2.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.api.websocket import router as ws_router
from app.api.routes import router as api_router
from app.api.auth import router as auth_router

app.include_router(ws_router)
app.include_router(api_router)
app.include_router(auth_router)


@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "0.2.0"}
