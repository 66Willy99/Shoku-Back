from fastapi import APIRouter, HTTPException, Depends, Query, Body, status
from services.pedido_service import PedidoService
from typing import List

router = APIRouter(prefix="/pedido", tags=["pedidos"])

@router.post("/")
async def crear_pedido(
    user_id:str= Body(...), 
    restaurante_id:str = Body(...), 
    mesa_id:str = Body(...),
    silla_id:str = Body(...),
    platos: dict = Body(...),
    service: PedidoService = Depends(PedidoService)
):
    return service.crear_pedido(user_id, restaurante_id, mesa_id, silla_id, platos)
