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