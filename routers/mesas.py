from fastapi import APIRouter, HTTPException, Depends, Query, Body, status
from services.mesa_service import MesaService
from typing import List


router = APIRouter(prefix="/mesa", tags=["mesas"])

@router.post("/")
async def crear_mesa(
    user_id:str= Body(...), 
    restaurante_id:str = Body(...), 
    capacidad:int = Body(...), 
    estado:str = Body(...),
    numero:int = Body(...),
    service: MesaService = Depends(MesaService)
):
    return service.crear_mesa(user_id, restaurante_id, capacidad, estado, numero)

@router.get("/all")
async def obtener_mesas(
    user_id:str= Body(...), 
    restaurante_id:str = Body(...),
    service: MesaService = Depends(MesaService)
):
    return service.obtener_mesas(user_id, restaurante_id)

@router.get("/")
async def obtener_mesa(
    user_id:str= Body(...), 
    restaurante_id:str = Body(...),
    mesa_id:str = Body(...),
    service: MesaService = Depends(MesaService)
):
    return service.obtener_mesa(user_id, restaurante_id, mesa_id)

@router.put("/")
async def actualizar_mesa(
    user_id:str= Body(...), 
    restaurante_id:str = Body(...),
    mesa_id:str = Body(...),
    capacidad:int = Body(...), 
    estado:str = Body(...),
    numero:int = Body(...),
    service: MesaService = Depends(MesaService)
):
    return service.actualizar_mesa(user_id, restaurante_id, mesa_id, capacidad, estado, numero)

@router.delete("/")
async def eliminar_mesa(
    user_id:str= Body(...), 
    restaurante_id:str = Body(...),
    mesa_id:str = Body(...),
    service: MesaService = Depends(MesaService)
):
    return service.eliminar_mesa(user_id, restaurante_id, mesa_id)