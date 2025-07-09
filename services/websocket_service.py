import json
import asyncio
from typing import Dict
from fastapi import WebSocket, WebSocketDisconnect, HTTPException
from firebase_admin import db
from datetime import datetime
from services.restaurant_service import RestaurantService

class KitchenWebSocketService:
    def __init__(self):
        self.active_connections = {}  # {restaurant_id: [websockets]}
        self.restaurant_service = RestaurantService()

    async def connect(self, user_id: str, restaurant_id: str, websocket: WebSocket):
        # Validar que el restaurante existe
        try:
            self.restaurant_service.obtener_restaurante(user_id, restaurant_id)
        except HTTPException as e:
            await websocket.close(code=1008)  # Policy Violation
            raise e

        await websocket.accept()
        
        # Manejar múltiples conexiones por restaurante
        if restaurant_id not in self.active_connections:
            self.active_connections[restaurant_id] = []
        
        self.active_connections[restaurant_id].append(websocket)
        print(f"✅ Nueva conexión WebSocket para restaurante {restaurant_id}. Total conexiones: {len(self.active_connections[restaurant_id])}")

    def disconnect(self, restaurant_id: str, websocket: WebSocket):
        if restaurant_id in self.active_connections:
            try:
                self.active_connections[restaurant_id].remove(websocket)
                print(f"❌ Conexión WebSocket desconectada del restaurante {restaurant_id}. Conexiones restantes: {len(self.active_connections[restaurant_id])}")
                
                # Si no hay más conexiones, eliminar la entrada
                if not self.active_connections[restaurant_id]:
                    del self.active_connections[restaurant_id]
            except ValueError:
                pass  # La conexión ya no estaba en la lista

    async def send_message(self, restaurant_id: str, message: str):
        if restaurant_id in self.active_connections:
            # Crear una copia de la lista para evitar modificaciones durante la iteración
            connections = self.active_connections[restaurant_id].copy()
            disconnected_websockets = []
            
            for websocket in connections:
                try:
                    await websocket.send_text(message)
                except Exception as e:
                    print(f"Error enviando mensaje via WebSocket: {e}")
                    disconnected_websockets.append(websocket)
            
            # Limpiar conexiones muertas
            for ws in disconnected_websockets:
                self.disconnect(restaurant_id, ws)

    async def broadcast_pedido_terminado(self, restaurant_id: str, pedido_data: dict):
        """
        Envía una notificación específica cuando un pedido está terminado.
        """
        mensaje = json.dumps({
            "evento": "pedido_terminado",
            "data": pedido_data,
            "timestamp": datetime.now().isoformat()
        })
        
        await self.send_message(restaurant_id, mensaje)
        print(f"📢 Notificación de pedido terminado enviada a restaurante {restaurant_id}: Mesa {pedido_data.get('mesa_numero', 'N/A')}")

    def get_active_connections_count(self, restaurant_id: str) -> int:
        """
        Retorna el número de conexiones activas para un restaurante.
        """
        return len(self.active_connections.get(restaurant_id, []))

# Instancia global para importar en el router
kitchen_websocket_service = KitchenWebSocketService()

