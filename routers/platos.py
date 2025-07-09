from fastapi import APIRouter, HTTPException, Depends, Query, Body, status
from services.plato_service import PlatoService
from typing import List

router = APIRouter(prefix="/plato", tags=["platos"])

@router.post("/")
async def crear_plato(
    user_id:str= Body(...), 
    restaurante_id:str = Body(...), 
    categoria_id:str = Body(...),
    descripcion:str = Body(...),
    imagenUrl:list = Body(...),
    nombre:str = Body(...),
    precio:float = Body(...),
    stock:int = Body(...),
    service: PlatoService = Depends(PlatoService)
):
    return service.crear_plato(user_id, restaurante_id, categoria_id, descripcion, imagenUrl, nombre, precio, stock)

@router.get("s/")
async def obtener_platos(
    user_id:str= Query(...), 
    restaurante_id:str = Query(...),
    service: PlatoService = Depends(PlatoService)
):
    return service.obtener_platos(user_id, restaurante_id)

@router.get("/")
async def obtener_plato(
    user_id:str= Query(...), 
    restaurante_id:str = Query(...),
    plato_id:str = Query(...),
    service: PlatoService = Depends(PlatoService)
):
    return service.obtener_plato(user_id, restaurante_id, plato_id)

@router.put("/")
async def actualizar_plato(
    user_id:str= Body(...), 
    restaurante_id:str = Body(...),
    plato_id:str = Body(...),
    categoria_id:str= Body(...), 
    descripcion:str= Body(...), 
    imagenUrl:list= Body(...),
    nombre:str= Body(...), 
    precio:float= Body(...), 
    stock:int= Body(...),
    service: PlatoService = Depends(PlatoService)
):
    return service.actualizar_plato(user_id, restaurante_id, plato_id, categoria_id, descripcion, imagenUrl, nombre, precio, stock)

@router.delete("/")
async def eliminar_plato(
    user_id:str= Body(...), 
    restaurante_id:str = Body(...),
    plato_id:str = Body(...),
    service: PlatoService = Depends(PlatoService)
):
    return service.eliminar_plato(user_id, restaurante_id, plato_id)

