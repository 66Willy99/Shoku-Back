import json
import asyncio
from typing import Dict
from fastapi import WebSocket, WebSocketDisconnect, HTTPException
from firebase_admin import db
from datetime import datetime
from services.restaurant_service import RestaurantService

class KitchenWebSocketService:
    def __init__(self):
        self.active_connections = {}
        self.restaurant_service = RestaurantService()

    async def connect(self, user_id: str, restaurant_id: str, websocket: WebSocket):
        # Validar que el restaurante existe
        try:
            self.restaurant_service.obtener_restaurante(user_id, restaurant_id)
        except HTTPException as e:
            await websocket.close(code=1008)  # Policy Violation
            raise e

        await websocket.accept()
        self.active_connections[restaurant_id] = websocket

    def disconnect(self, restaurant_id: str):
        self.active_connections.pop(restaurant_id, None)

    async def send_message(self, restaurant_id: str, message: str):
        websocket = self.active_connections.get(restaurant_id)
        if websocket:
            await websocket.send_text(message)

# Instancia global para importar en el router
kitchen_websocket_service = KitchenWebSocketService()

