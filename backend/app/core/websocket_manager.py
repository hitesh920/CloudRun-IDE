"""
CloudRun IDE - WebSocket Manager
Manages WebSocket connections for real-time output streaming.
"""

from fastapi import WebSocket
from typing import Dict, Set


class WebSocketManager:
    """Manages WebSocket connections and message broadcasting."""
    
    def __init__(self):
        """Initialize the WebSocket manager."""
        self.active_connections: Dict[str, Set[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, execution_id: str):
        """Accept and register a new WebSocket connection."""
        await websocket.accept()
        
        if execution_id not in self.active_connections:
            self.active_connections[execution_id] = set()
        
        self.active_connections[execution_id].add(websocket)
    
    def disconnect(self, websocket: WebSocket, execution_id: str):
        """Remove a WebSocket connection."""
        if execution_id in self.active_connections:
            self.active_connections[execution_id].discard(websocket)
            
            if not self.active_connections[execution_id]:
                del self.active_connections[execution_id]
    
    async def broadcast_to_execution(self, execution_id: str, message: dict):
        """Broadcast a message to all connections for an execution."""
        if execution_id not in self.active_connections:
            return
        
        connections = list(self.active_connections[execution_id])
        
        for websocket in connections:
            try:
                await websocket.send_json(message)
            except Exception:
                self.disconnect(websocket, execution_id)
    
    def get_connection_count(self, execution_id: str) -> int:
        """Get number of active connections for an execution."""
        if execution_id not in self.active_connections:
            return 0
        return len(self.active_connections[execution_id])


# Global WebSocket manager instance
websocket_manager = WebSocketManager()
