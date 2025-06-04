from fastapi import APIRouter, HTTPException, Depends, Query, Body, status
from services.silla_service import SillaService
from typing import List

router = APIRouter(prefix="/silla", tags=["sillas"])

@router.post("/")
async def crear_silla(
    user_id:str= Body(...), 
    restaurante_id:str = Body(...), 
    mesa_id:str = Body(...),
    numero:int = Body(...),
    service: SillaService = Depends(SillaService)
):
    return service.crear_silla(user_id, restaurante_id, mesa_id, numero)

@router.get("/all")
async def obtener_sillas(
    user_id:str= Query(...), 
    restaurante_id:str = Query(...),
    service: SillaService = Depends(SillaService)
):
    return service.obtener_sillas(user_id, restaurante_id)

@router.get("/")
async def obtener_silla(
    user_id:str= Query(...), 
    restaurante_id:str = Query(...),
    silla_id:str = Query(...),
    service: SillaService = Depends(SillaService)
):
    return service.obtener_silla(user_id, restaurante_id, silla_id)

@router.put("/")
async def actualizar_silla(
    user_id:str= Body(...), 
    restaurante_id:str = Body(...),
    silla_id:str = Body(...),
    numero:int = Body(...),
    service: SillaService = Depends(SillaService)
):
    return service.actualizar_silla(user_id, restaurante_id, silla_id, numero)

@router.delete("/")
async def eliminar_silla(
    user_id:str= Body(...), 
    restaurante_id:str = Body(...),
    silla_id:str = Body(...),
    service: SillaService = Depends(SillaService)
):
    return service.eliminar_silla(user_id, restaurante_id, silla_id)
