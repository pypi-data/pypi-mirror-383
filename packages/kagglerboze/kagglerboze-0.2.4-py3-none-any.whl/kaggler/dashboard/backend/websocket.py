"""WebSocket handler for real-time updates."""
import asyncio
import json
from typing import Dict, Set
from datetime import datetime
from fastapi import WebSocket, WebSocketDisconnect
import logging

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections for real-time updates."""

    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        self.all_connections: Set[WebSocket] = set()
        self.lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket, competition_id: str = None):
        """Connect a new WebSocket client."""
        await websocket.accept()
        async with self.lock:
            self.all_connections.add(websocket)
            if competition_id:
                if competition_id not in self.active_connections:
                    self.active_connections[competition_id] = set()
                self.active_connections[competition_id].add(websocket)
        logger.info(f"Client connected. Total connections: {len(self.all_connections)}")

    async def disconnect(self, websocket: WebSocket, competition_id: str = None):
        """Disconnect a WebSocket client."""
        async with self.lock:
            self.all_connections.discard(websocket)
            if competition_id and competition_id in self.active_connections:
                self.active_connections[competition_id].discard(websocket)
                if not self.active_connections[competition_id]:
                    del self.active_connections[competition_id]
        logger.info(f"Client disconnected. Total connections: {len(self.all_connections)}")

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Send a message to a specific client."""
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            await self.disconnect(websocket)

    async def broadcast_to_competition(self, message: dict, competition_id: str):
        """Broadcast a message to all clients subscribed to a competition."""
        async with self.lock:
            connections = self.active_connections.get(competition_id, set()).copy()

        disconnected = []
        for connection in connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to client: {e}")
                disconnected.append(connection)

        # Clean up disconnected clients
        for connection in disconnected:
            await self.disconnect(connection, competition_id)

    async def broadcast_to_all(self, message: dict):
        """Broadcast a message to all connected clients."""
        async with self.lock:
            connections = self.all_connections.copy()

        disconnected = []
        for connection in connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to client: {e}")
                disconnected.append(connection)

        # Clean up disconnected clients
        for connection in disconnected:
            await self.disconnect(connection)

    def get_connection_count(self, competition_id: str = None) -> int:
        """Get the number of active connections."""
        if competition_id:
            return len(self.active_connections.get(competition_id, set()))
        return len(self.all_connections)


class EvolutionNotifier:
    """Handles notifications for evolution progress."""

    def __init__(self, manager: ConnectionManager):
        self.manager = manager

    async def notify_generation_complete(
        self,
        competition_id: str,
        generation: int,
        metrics: dict
    ):
        """Notify clients when a generation completes."""
        message = {
            "type": "generation_complete",
            "competition_id": competition_id,
            "generation": generation,
            "metrics": metrics,
            "timestamp": datetime.now().isoformat()
        }
        await self.manager.broadcast_to_competition(message, competition_id)

    async def notify_pareto_update(
        self,
        competition_id: str,
        pareto_frontier: list
    ):
        """Notify clients of Pareto frontier updates."""
        message = {
            "type": "pareto_update",
            "competition_id": competition_id,
            "pareto_frontier": pareto_frontier,
            "timestamp": datetime.now().isoformat()
        }
        await self.manager.broadcast_to_competition(message, competition_id)

    async def notify_competition_complete(
        self,
        competition_id: str,
        final_metrics: dict
    ):
        """Notify clients when a competition completes."""
        message = {
            "type": "competition_complete",
            "competition_id": competition_id,
            "final_metrics": final_metrics,
            "timestamp": datetime.now().isoformat()
        }
        await self.manager.broadcast_to_competition(message, competition_id)

    async def notify_error(
        self,
        competition_id: str,
        error_message: str
    ):
        """Notify clients of errors."""
        message = {
            "type": "error",
            "competition_id": competition_id,
            "error": error_message,
            "timestamp": datetime.now().isoformat()
        }
        await self.manager.broadcast_to_competition(message, competition_id)

    async def notify_status_change(
        self,
        competition_id: str,
        status: str,
        details: dict = None
    ):
        """Notify clients of competition status changes."""
        message = {
            "type": "status_change",
            "competition_id": competition_id,
            "status": status,
            "details": details or {},
            "timestamp": datetime.now().isoformat()
        }
        await self.manager.broadcast_to_competition(message, competition_id)


# Global connection manager instance
manager = ConnectionManager()
notifier = EvolutionNotifier(manager)


async def websocket_endpoint(websocket: WebSocket, competition_id: str = None):
    """WebSocket endpoint handler."""
    await manager.connect(websocket, competition_id)
    try:
        # Send initial connection confirmation
        await manager.send_personal_message(
            {
                "type": "connected",
                "competition_id": competition_id,
                "timestamp": datetime.now().isoformat()
            },
            websocket
        )

        # Keep connection alive and handle incoming messages
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                await handle_client_message(websocket, message, competition_id)
            except json.JSONDecodeError:
                await manager.send_personal_message(
                    {
                        "type": "error",
                        "error": "Invalid JSON format",
                        "timestamp": datetime.now().isoformat()
                    },
                    websocket
                )
    except WebSocketDisconnect:
        await manager.disconnect(websocket, competition_id)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await manager.disconnect(websocket, competition_id)


async def handle_client_message(
    websocket: WebSocket,
    message: dict,
    competition_id: str
):
    """Handle messages from clients."""
    msg_type = message.get("type")

    if msg_type == "ping":
        await manager.send_personal_message(
            {
                "type": "pong",
                "timestamp": datetime.now().isoformat()
            },
            websocket
        )
    elif msg_type == "subscribe":
        new_competition_id = message.get("competition_id")
        if new_competition_id:
            await manager.connect(websocket, new_competition_id)
            await manager.send_personal_message(
                {
                    "type": "subscribed",
                    "competition_id": new_competition_id,
                    "timestamp": datetime.now().isoformat()
                },
                websocket
            )
    elif msg_type == "unsubscribe":
        old_competition_id = message.get("competition_id")
        if old_competition_id:
            await manager.disconnect(websocket, old_competition_id)
            await manager.send_personal_message(
                {
                    "type": "unsubscribed",
                    "competition_id": old_competition_id,
                    "timestamp": datetime.now().isoformat()
                },
                websocket
            )
