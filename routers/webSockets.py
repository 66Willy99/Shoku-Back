from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from services.websocket_service import kitchen_websocket_service

router = APIRouter(prefix="/ws", tags=["websockets"])

@router.websocket("/kitchen/{user_id}/{restaurant_id}")
async def websocket_kitchen(websocket: WebSocket, user_id: str, restaurant_id: str):
    await kitchen_websocket_service.connect(user_id, restaurant_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Aquí puedes procesar el mensaje recibido
            await kitchen_websocket_service.send_message(restaurant_id, f"Echo: {data}")
    except WebSocketDisconnect:
        kitchen_websocket_service.disconnect(restaurant_id)