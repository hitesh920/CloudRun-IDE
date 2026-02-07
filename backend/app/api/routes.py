"""
CloudRun IDE - API Routes
REST API endpoints for code execution and management.
"""

from fastapi import APIRouter, HTTPException, status
from typing import List, Optional
from pydantic import BaseModel

from app.models import (
    ExecuteCodeRequest,
    ExecutionResponse,
    LanguageEnum,
)
from app.core.executor import code_executor
from app.services.ai_assistant import ai_assistant
from app.utils.constants import CODE_TEMPLATES

router = APIRouter(prefix="/api", tags=["execution"])


class AIAssistRequest(BaseModel):
    """Request model for AI assistance."""
    action: str
    code: Optional[str] = None
    error: Optional[str] = None
    language: str


@router.post("/execute", response_model=ExecutionResponse)
async def execute_code(request: ExecuteCodeRequest):
    """Execute code in a Docker container."""
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
    """Stop a running code execution."""
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
    """Get list of supported programming languages."""
    return {
        "languages": [lang.value for lang in LanguageEnum],
        "count": len(LanguageEnum),
    }


@router.get("/templates/{language}")
async def get_code_template(language: LanguageEnum):
    """Get starter code template for a language."""
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
    """Get starter code templates for all languages."""
    return {
        "templates": CODE_TEMPLATES,
    }


@router.post("/ai/assist")
async def ai_assist(request: AIAssistRequest):
    """Get AI assistance for code."""
    if not ai_assistant.is_enabled():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI assistant is not configured. Please set GEMINI_API_KEY.",
        )
    
    try:
        if request.action == "fix_error":
            if not request.code or not request.error:
                raise HTTPException(status_code=400, detail="code and error required")
            result = await ai_assistant.fix_error(request.code, request.error, request.language)
        
        elif request.action == "explain_error":
            if not request.error:
                raise HTTPException(status_code=400, detail="error required")
            result = await ai_assistant.explain_error(request.error, request.language)
        
        elif request.action == "explain_code":
            if not request.code:
                raise HTTPException(status_code=400, detail="code required")
            result = await ai_assistant.explain_code(request.code, request.language)
        
        elif request.action == "optimize_code":
            if not request.code:
                raise HTTPException(status_code=400, detail="code required")
            result = await ai_assistant.optimize_code(request.code, request.language)
        
        else:
            raise HTTPException(status_code=400, detail=f"Unknown action: {request.action}")
        
        if not result.get("success"):
            raise HTTPException(status_code=500, detail=result.get("error", "AI request failed"))
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI assistance failed: {str(e)}")


@router.get("/ai/status")
async def ai_status():
    """Check if AI assistant is available."""
    return {
        "enabled": ai_assistant.is_enabled(),
        "provider": "Google Gemini" if ai_assistant.is_enabled() else None,
    }
