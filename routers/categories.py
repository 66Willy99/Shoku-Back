from fastapi import APIRouter, HTTPException, Depends, Query, Body, status
from services.category_service import CategoryService
from typing import List


router = APIRouter(prefix="/user/restaurant/category", tags=["categories"])

@router.post("/")
async def crear_categoria(
    user_id:str= Body(...), 
    restaurante_id:str = Body(...), 
    descripcion:str = Body(...), 
    nombre:str = Body(...),
    service: CategoryService = Depends(CategoryService)
):
    return service.crear_categoria(user_id, restaurante_id, descripcion, nombre)

@router.get("/all")
async def obtener_categorias(
    user_id:str,
    restaurante_id:str,
    service: CategoryService = Depends(CategoryService)
):
    return service.obtener_categorias(user_id, restaurante_id)

@router.get("/")
async def obtener_categoria(
    user_id:str,
    restaurante_id:str,
    categoria_id:str,
    service: CategoryService = Depends(CategoryService)
):
    return service.obtener_categoria(user_id, restaurante_id, categoria_id)

@router.put("/")
async def actualizar_categoria(newData : dict = Body(...), service: CategoryService = Depends(CategoryService)):
    try:
        user_id = newData.get("user_id")
        restaurante_id = newData.get("restaurante_id")
        categoria_id = newData.get("categoria_id")
        nombre = newData.get("nombre")
        descripcion = newData.get("descripcion")
        if not user_id or not restaurante_id or not categoria_id:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="user_id, restaurante_id y categoria_id son requeridos"
            )
        if nombre == "":
            nombre = None
        if descripcion == "":
            descripcion = None
        return service.actualizar_categoria(user_id, restaurante_id, categoria_id, nombre, descripcion)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error interno: {str(e)}")

@router.delete("/")
async def eliminar_categoria(
    user_id:str,
    restaurante_id:str,
    categoria_id:str,
    service: CategoryService = Depends(CategoryService)
):
    return service.eliminar_categoria(user_id, restaurante_id, categoria_id)