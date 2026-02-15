"""
CloudRun IDE - Data Models
Pydantic models for request/response validation.
"""

from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class LanguageEnum(str, Enum):
    """Supported programming languages."""
    python = "python"
    nodejs = "nodejs"
    java = "java"
    cpp = "cpp"
    html = "html"
    ubuntu = "ubuntu"


class FileData(BaseModel):
    """Uploaded file data."""
    name: str
    content: str


class ExecuteCodeRequest(BaseModel):
    """Request model for code execution."""
    language: str
    code: str
    stdin: Optional[str] = None
    files: Optional[List[FileData]] = None


class ExecutionResponse(BaseModel):
    """Response model for code execution."""
    execution_id: str
    status: str
    message: str


class ExecutionResult(BaseModel):
    """Full execution result."""
    execution_id: str
    status: str
    stdout: str = ""
    stderr: str = ""
    exit_code: int = 0
    execution_time: float = 0.0
