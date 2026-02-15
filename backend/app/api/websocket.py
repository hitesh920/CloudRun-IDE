"""
CloudRun IDE - WebSocket Endpoints
WebSocket routes for real-time code execution output streaming.
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import json
import asyncio

from app.core.executor import code_executor
from app.utils.helpers import get_timestamp

router = APIRouter(tags=["websocket"])


@router.websocket("/ws/execute")
async def websocket_execute_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time code execution.
    
    Client sends:
    {
        "language": "python",
        "code": "print('Hello')",
        "stdin": ""
    }
    
    Server streams:
    {
        "type": "stdout" | "stderr" | "status" | "error" | "complete",
        "content": "message",
        "timestamp": "ISO timestamp"
    }
    """
    await websocket.accept()
    print("🔌 WebSocket connected")
    
    try:
        # Receive execution request with a timeout
        try:
            data = await asyncio.wait_for(
                websocket.receive_json(),
                timeout=30.0
            )
        except asyncio.TimeoutError:
            print("⚠️ WebSocket timeout waiting for request")
            await _safe_send(websocket, {
                "type": "error",
                "content": "Timeout waiting for execution request",
                "timestamp": get_timestamp(),
            })
            await _safe_close(websocket)
            return
        
        language = data.get("language")
        code = data.get("code")
        stdin = data.get("stdin", "")
        files = data.get("files", [])
        
        print(f"📝 Execution request: language={language}, code_length={len(code or '')}, has_stdin={bool(stdin)}, files={len(files)}")
        
        if not language or not code:
            await _safe_send(websocket, {
                "type": "error",
                "content": "Missing required fields: language and code",
                "timestamp": get_timestamp(),
            })
            await _safe_close(websocket)
            return
        
        # Execute code and stream output
        async for message in code_executor.execute_code_stream(
            language=language,
            code=code,
            stdin=stdin,
            files=files,
        ):
            print(f"📤 Sending: {message.get('type')} - {message.get('content', '')[:80]}")
            
            sent = await _safe_send(websocket, message)
            if not sent:
                print("⚠️ Client disconnected during execution")
                break
        
        # Close connection after execution
        await _safe_close(websocket)
        print("🔌 WebSocket closed (execution complete)")
        
    except WebSocketDisconnect:
        print("🔌 WebSocket disconnected by client")
    
    except Exception as e:
        print(f"❌ WebSocket error: {e}")
        await _safe_send(websocket, {
            "type": "error",
            "content": f"Server error: {str(e)}",
            "timestamp": get_timestamp(),
        })
        await _safe_close(websocket)


async def _safe_send(websocket: WebSocket, message: dict) -> bool:
    """Send a message, returning False if the connection is closed."""
    try:
        await websocket.send_json(message)
        return True
    except Exception:
        return False


async def _safe_close(websocket: WebSocket):
    """Safely close a WebSocket connection."""
    try:
        await websocket.close()
    except Exception:
        pass
