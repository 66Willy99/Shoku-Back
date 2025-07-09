from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from services.websocket_service import kitchen_websocket_service
import json
from datetime import datetime

router = APIRouter(prefix="/ws", tags=["websockets"])

@router.websocket("/kitchen/{user_id}/{restaurant_id}")
async def websocket_kitchen(websocket: WebSocket, user_id: str, restaurant_id: str):
    await kitchen_websocket_service.connect(user_id, restaurant_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Procesar mensajes recibidos del cliente
            try:
                mensaje = json.loads(data)
                if mensaje.get("tipo") == "ping":
                    # Responder a ping con pong
                    response = json.dumps({"tipo": "pong", "timestamp": datetime.now().isoformat()})
                    await kitchen_websocket_service.send_message(restaurant_id, response)
                else:
                    # Echo para otros mensajes
                    await kitchen_websocket_service.send_message(restaurant_id, f"Echo: {data}")
            except json.JSONDecodeError:
                # Si no es JSON válido, hacer echo simple
                await kitchen_websocket_service.send_message(restaurant_id, f"Echo: {data}")
    except WebSocketDisconnect:
        kitchen_websocket_service.disconnect(restaurant_id, websocket)

@router.get("/msg/{user_id}/{restaurant_id}/{mesa_id}")
async def websocket_msg(user_id: str, restaurant_id: str, mesa_id: str):
    pass