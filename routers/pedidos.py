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

@router.get("s/")
async def obtener_pedidos(
    user_id: str = Body(...),
    restaurante_id: str = Body(...),
    service: PedidoService = Depends(PedidoService)
):
    return service.obtener_pedidos(user_id, restaurante_id)

@router.get("/")
async def obtener_pedido(
    pedido_id: str = Body(...),
    user_id: str = Body(...),
    restaurante_id: str = Body(...),
    service: PedidoService = Depends(PedidoService)
):
    return service.obtener_pedido(pedido_id, user_id, restaurante_id)

@router.get("s/mesa/")
async def obtener_pedidos_mesa(
    user_id: str = Body(...),
    restaurante_id: str = Body(...),
    mesa_id: str = Body(...),
    service: PedidoService = Depends(PedidoService)
):
    return service.obtener_pedidos_mesa(user_id, restaurante_id, mesa_id)

@router.put("/")
async def actualizar_estado(
    pedido_id: str = Body(...),
    user_id: str = Body(...),
    restaurante_id: str = Body(...),
    estado_actual: int = Body(...),
    service: PedidoService = Depends(PedidoService)
):
    return service.actualizar_estado(user_id, restaurante_id,pedido_id ,  estado_actual)
