from fastapi import APIRouter, HTTPException, Depends, Query, Body, status
from services.trabajador_service import TrabajadorService

router = APIRouter(prefix="/trabajador", tags=["trabajadores"])

@router.post("/")
async def crear_trabajador(
    user_id: str = Body(...), 
    restaurante_id: str = Body(...), 
    email: str = Body(...),
    nombre: str = Body(...),
    rol: str = Body(...),
    user: str = Body(...),
    service: TrabajadorService = Depends(TrabajadorService)
):
    return service.crear_trabajador(user_id, restaurante_id, email, nombre, rol, user)

@router.get("es/")
async def obtener_trabajadores(
    user_id: str = Body(...), 
    restaurante_id: str = Body(...),
    service: TrabajadorService = Depends(TrabajadorService)
):
    return service.obtener_trabajadores(user_id, restaurante_id)

@router.get("/")
async def obtener_trabajador(
    user_id: str = Body(...), 
    restaurante_id: str = Body(...),
    trabajador_id: str = Body(...),
    service: TrabajadorService = Depends(TrabajadorService)
):
    return service.obtener_trabajador(user_id, restaurante_id, trabajador_id)

@router.put("/")
async def actualizar_trabajador(
    user_id: str = Body(...), 
    restaurante_id: str = Body(...),
    trabajador_id: str = Body(...),
    email: str = Body(...),
    nombre: str = Body(...),
    rol: str = Body(...),
    user: str = Body(...),
    service: TrabajadorService = Depends(TrabajadorService)
):
    return service.actualizar_trabajador(user_id, restaurante_id, trabajador_id, email, nombre, rol, user)

@router.delete("/")
async def eliminar_trabajador(
    user_id: str = Body(...), 
    restaurante_id: str = Body(...),
    trabajador_id: str = Body(...),
    service: TrabajadorService = Depends(TrabajadorService)
):
    return service.eliminar_trabajador(user_id, restaurante_id, trabajador_id)
