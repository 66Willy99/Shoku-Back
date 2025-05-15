from fastapi import APIRouter, HTTPException, Depends, Query, Body, status
from services.menu_service import MenuService
from typing import List


router = APIRouter(prefix="/menu", tags=["menus"])

@router.post("/")
async def crear_menu(
    user_id:str= Body(...), 
    restaurante_id:str = Body(...), 
    descripcion:str = Body(...), 
    nombre:str = Body(...),
    platos:list = Body(...),
    service: MenuService = Depends(MenuService)
):
    return service.crear_menu(user_id, restaurante_id, descripcion, nombre, platos)

@router.get("/all")
async def obtener_menus(
    user_id:str,
    restaurante_id:str,
    service: MenuService = Depends(MenuService)
):
    return service.obtener_menus(user_id, restaurante_id)

@router.get("/")
async def obtener_menu(
    user_id:str,
    restaurante_id:str,
    menu_id:str,
    service: MenuService = Depends(MenuService)
):
    return service.obtener_menu(user_id, restaurante_id, menu_id)

@router.put("/")
async def actualizar_menu(newData : dict = Body(...), service: MenuService = Depends(MenuService)):
    try:
        user_id = newData.get("user_id")
        restaurante_id = newData.get("restaurante_id")
        menu_id = newData.get("menu_id")
        nombre = newData.get("nombre")
        descripcion = newData.get("descripcion")
        platos = newData.get("platos")
        if not user_id or not restaurante_id or not menu_id:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="user_id, restaurante_id y menu_id son requeridos"
            )
        if nombre == "":
            nombre = None
        if descripcion == "":
            descripcion = None
        if platos == []:
            platos = None
        return service.actualizar_menu(user_id, restaurante_id, menu_id, nombre, descripcion, platos)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error interno: {str(e)}")
    
@router.delete("/")
async def eliminar_menu(
    user_id:str,
    restaurante_id:str,
    menu_id:str,
    service: MenuService = Depends(MenuService)
):
    try:
        if not user_id or not restaurante_id or not menu_id:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="user_id, restaurante_id y menu_id son requeridos"
            )
        return service.eliminar_menu(user_id, restaurante_id, menu_id)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error interno: {str(e)}")

