"""
CloudRun IDE - WebSocket Endpoints
WebSocket routes for real-time code execution output streaming.
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import json

from app.core.websocket_manager import websocket_manager
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
    execution_id = None
    
    try:
        # Receive execution request
        data = await websocket.receive_json()
        
        language = data.get("language")
        code = data.get("code")
        stdin = data.get("stdin", "")
        files = data.get("files", [])
        
        print(f"📝 Execution request: language={language}, code_length={len(code)}, has_stdin={bool(stdin)}, files={len(files)}")
        
        if not language or not code:
            await websocket.send_json({
                "type": "error",
                "content": "Missing required fields: language and code",
                "timestamp": get_timestamp(),
            })
            await websocket.close()
            return
        
        # Execute code with streaming
        print(f"🚀 Starting execution for {language}")
        async for message in code_executor.execute_code_stream(
            language=language,
            code=code,
            stdin=stdin,
            files=files,
        ):
            print(f"📤 Sending: {message.get('type')} - {message.get('content', '')[:50]}")
            await websocket.send_json(message)
        
        print(f"✅ Execution completed for {language}")
        # Close connection after execution
        await websocket.close()
        
    except WebSocketDisconnect:
        print("⚠️ WebSocket disconnected by client")
        if execution_id:
            # Stop execution if client disconnects
            code_executor.stop_execution(execution_id)
    
    except Exception as e:
        print(f"❌ WebSocket error: {e}")
        import traceback
        traceback.print_exc()
        try:
            await websocket.send_json({
                "type": "error",
                "content": f"Execution error: {str(e)}",
                "timestamp": get_timestamp(),
            })
        except:
            pass


@router.websocket("/ws/output/{execution_id}")
async def websocket_output_endpoint(websocket: WebSocket, execution_id: str):
    """
    WebSocket endpoint for receiving output from an ongoing execution.
    
    This allows multiple clients to connect to the same execution
    and receive real-time output updates.
    """
    await websocket_manager.connect(websocket, execution_id)
    
    try:
        # Keep connection alive and receive any control messages
        while True:
            data = await websocket.receive_text()
            
            # Handle control messages
            message = json.loads(data)
            
            if message.get("action") == "stop":
                # Stop the execution
                code_executor.stop_execution(execution_id)
                await websocket_manager.send_status(
                    execution_id,
                    "Execution stopped by user",
                    get_timestamp(),
                )
                break
    
    except WebSocketDisconnect:
        print(f"WebSocket disconnected for execution: {execution_id}")
    
    except Exception as e:
        print(f"WebSocket error: {e}")
    
    finally:
        websocket_manager.disconnect(websocket, execution_id)
