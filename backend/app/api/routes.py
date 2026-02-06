"""
CloudRun IDE - API Routes
REST API endpoints for code execution and management.
"""

from fastapi import APIRouter, HTTPException, status
from typing import List

from app.models import (
    ExecuteCodeRequest,
    ExecutionResponse,
    LanguageEnum,
)
from app.core.executor import code_executor
from app.utils.constants import CODE_TEMPLATES

router = APIRouter(prefix="/api", tags=["execution"])


@router.post("/execute", response_model=ExecutionResponse)
async def execute_code(request: ExecuteCodeRequest):
    """
    Execute code in a Docker container.
    
    This endpoint executes code synchronously and returns the complete result.
    For real-time output streaming, use WebSocket endpoint instead.
    """
    try:
        result = await code_executor.execute_code(
            language=request.language,
            code=request.code,
            stdin=request.stdin,
        )
        
        return ExecutionResponse(
            execution_id=result["execution_id"],
            status=result["status"],
            message=f"Execution {result['status']}",
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Execution failed: {str(e)}",
        )


@router.post("/execute/stop/{execution_id}")
async def stop_execution(execution_id: str):
    """
    Stop a running code execution.
    """
    success = code_executor.stop_execution(execution_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Execution {execution_id} not found or already completed",
        )
    
    return {
        "execution_id": execution_id,
        "status": "stopped",
        "message": "Execution stopped successfully",
    }


@router.get("/languages")
async def get_supported_languages():
    """
    Get list of supported programming languages.
    """
    return {
        "languages": [lang.value for lang in LanguageEnum],
        "count": len(LanguageEnum),
    }


@router.get("/templates/{language}")
async def get_code_template(language: LanguageEnum):
    """
    Get starter code template for a language.
    """
    template = code_executor.get_code_template(language.value)
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Template not found for language: {language}",
        )
    
    return {
        "language": language,
        "template": template,
    }


@router.get("/templates")
async def get_all_templates():
    """
    Get starter code templates for all languages.
    """
    return {
        "templates": CODE_TEMPLATES,
    }
