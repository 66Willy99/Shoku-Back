from fastapi import APIRouter, HTTPException, Depends, Query, Body, status
from services.restaurant_service import RestaurantService
from typing import List


router = APIRouter(prefix="/restaurant", tags=["restaurants"])

@router.get("s/")
async def obtener_restaurantes(
    user_id: str,
    service: RestaurantService = Depends(RestaurantService)
):
    return service.obtener_restaurantes(user_id)

@router.get("/")
async def obtener_restaurante(
    user_id: str,
    restaurante_id: str,
    service: RestaurantService = Depends(RestaurantService)
):
    return service.obtener_restaurante(user_id, restaurante_id)

@router.post("/")
async def crear_restaurante(
    user_id: str = Body(...),
    nombre: str = Body(...),
    direccion: str = Body(...),
    telefono: str = Body(...),
    service: RestaurantService = Depends(RestaurantService)
):
    return service.crear_restaurante(user_id, nombre, direccion, telefono)

@router.put("/")
async def actualizar_restaurante(
    user_id: str = Body(...),
    restaurante_id: str = Body(...),
    nombre: str = Body(...),
    direccion: str = Body(...),
    telefono: str = Body(...),
    service: RestaurantService = Depends(RestaurantService)
):
    try:
        
        return service.actualizar_restaurante(
            user_id=user_id,
            restaurante_id=restaurante_id,
            nombre=nombre,
            direccion=direccion,
            telefono=telefono
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en la solicitud: {str(e)}"
        )

@router.delete("/")
async def eliminar_restaurante(
    user_id: str,
    restaurante_id: str,
    service: RestaurantService = Depends(RestaurantService)
):
    return service.eliminar_restaurante(user_id, restaurante_id)
