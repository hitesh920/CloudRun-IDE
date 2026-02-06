"""
CloudRun IDE - WebSocket Manager
Manages WebSocket connections for real-time output streaming.
"""

from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, Set
import asyncio
import json


class WebSocketManager:
    """Manages WebSocket connections and message broadcasting."""
    
    def __init__(self):
        """Initialize the WebSocket manager."""
        # Active connections: {execution_id: set of websockets}
        self.active_connections: Dict[str, Set[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, execution_id: str):
        """
        Accept and register a new WebSocket connection.
        
        Args:
            websocket: WebSocket connection
            execution_id: Execution identifier
        """
        await websocket.accept()
        
        if execution_id not in self.active_connections:
            self.active_connections[execution_id] = set()
        
        self.active_connections[execution_id].add(websocket)
        print(f"✅ WebSocket connected for execution: {execution_id}")
    
    def disconnect(self, websocket: WebSocket, execution_id: str):
        """
        Remove a WebSocket connection.
        
        Args:
            websocket: WebSocket connection
            execution_id: Execution identifier
        """
        if execution_id in self.active_connections:
            self.active_connections[execution_id].discard(websocket)
            
            # Clean up empty sets
            if not self.active_connections[execution_id]:
                del self.active_connections[execution_id]
        
        print(f"👋 WebSocket disconnected for execution: {execution_id}")
    
    async def send_message(self, websocket: WebSocket, message: dict):
        """
        Send a message to a specific WebSocket.
        
        Args:
            websocket: WebSocket connection
            message: Message dictionary to send
        """
        try:
            await websocket.send_json(message)
        except Exception as e:
            print(f"❌ Failed to send message: {e}")
    
    async def broadcast_to_execution(self, execution_id: str, message: dict):
        """
        Broadcast a message to all connections for an execution.
        
        Args:
            execution_id: Execution identifier
            message: Message dictionary to broadcast
        """
        if execution_id not in self.active_connections:
            return
        
        # Create list of websockets to avoid modification during iteration
        connections = list(self.active_connections[execution_id])
        
        for websocket in connections:
            try:
                await websocket.send_json(message)
            except Exception as e:
                print(f"❌ Failed to broadcast to websocket: {e}")
                # Remove failed connection
                self.disconnect(websocket, execution_id)
    
    async def send_stdout(self, execution_id: str, content: str, timestamp: str):
        """Send stdout message."""
        await self.broadcast_to_execution(execution_id, {
            "type": "stdout",
            "content": content,
            "timestamp": timestamp,
        })
    
    async def send_stderr(self, execution_id: str, content: str, timestamp: str):
        """Send stderr message."""
        await self.broadcast_to_execution(execution_id, {
            "type": "stderr",
            "content": content,
            "timestamp": timestamp,
        })
    
    async def send_status(self, execution_id: str, status: str, timestamp: str):
        """Send status update."""
        await self.broadcast_to_execution(execution_id, {
            "type": "status",
            "content": status,
            "timestamp": timestamp,
        })
    
    async def send_error(self, execution_id: str, error: str, timestamp: str):
        """Send error message."""
        await self.broadcast_to_execution(execution_id, {
            "type": "error",
            "content": error,
            "timestamp": timestamp,
        })
    
    async def send_complete(self, execution_id: str, exit_code: int, timestamp: str):
        """Send execution complete message."""
        await self.broadcast_to_execution(execution_id, {
            "type": "complete",
            "content": f"Execution completed with exit code {exit_code}",
            "exit_code": exit_code,
            "timestamp": timestamp,
        })
    
    def get_connection_count(self, execution_id: str) -> int:
        """Get number of active connections for an execution."""
        if execution_id not in self.active_connections:
            return 0
        return len(self.active_connections[execution_id])
    
    def has_connections(self, execution_id: str) -> bool:
        """Check if there are any active connections for an execution."""
        return self.get_connection_count(execution_id) > 0


# Global WebSocket manager instance
websocket_manager = WebSocketManager()
