"""
CloudRun IDE - Data Models
Pydantic models for request/response validation.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum


class LanguageEnum(str, Enum):
    """Supported programming languages."""
    PYTHON = "python"
    JAVA = "java"
    CPP = "cpp"
    NODEJS = "nodejs"
    HTML = "html"
    UBUNTU = "ubuntu"


class ExecutionStatus(str, Enum):
    """Execution status types."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    ERROR = "error"
    TIMEOUT = "timeout"
    STOPPED = "stopped"


class ExecuteCodeRequest(BaseModel):
    """Request model for code execution."""
    language: LanguageEnum
    code: str = Field(..., min_length=1)
    stdin: Optional[str] = None
    files: Optional[List[dict]] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "language": "python",
                "code": "print('Hello, World!')",
                "stdin": "",
                "files": []
            }
        }


class ExecutionResponse(BaseModel):
    """Response model for code execution."""
    execution_id: str
    status: ExecutionStatus
    message: str


class OutputMessage(BaseModel):
    """WebSocket output message."""
    type: str  # "stdout", "stderr", "status", "error"
    content: str
    timestamp: str


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str


class APIInfoResponse(BaseModel):
    """API info response."""
    name: str
    version: str
    status: str
    docs: str
