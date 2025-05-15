from fastapi import APIRouter, HTTPException, Depends, Query, Body, status
from services.restaurant_service import RestaurantService
from typing import List


router = APIRouter(prefix="/user/restaurant", tags=["restaurants"])

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

@router.post("/category")
async def crear_categoria(
    user_id:str, 
    restaurante_id:str, 
    descripcion:str, 
    nombre:str,
    service: RestaurantService = Depends(RestaurantService)
):
    return service.crear_categoria(user_id, restaurante_id, descripcion, nombre)

@router.get("/categories")
async def obtener_categorias(
    user_id:str, 
    restaurante_id:str, 
    service: RestaurantService = Depends(RestaurantService)
):
    return service.obtener_categorias(user_id, restaurante_id)

@router.put("/category")
async def actualizar_categoria(
    user_id:str, 
    restaurante_id:str, 
    categoria_id:str, 
    nombre:str = None, 
    descripcion:str = None,
    service: RestaurantService = Depends(RestaurantService)
):
    return service.editar_categoria(user_id, restaurante_id, categoria_id, nombre, descripcion)

@router.delete("/category")
async def eliminar_categoria(
    user_id:str, 
    restaurante_id:str, 
    categoria_id:str,
    service: RestaurantService = Depends(RestaurantService)
):
    return service.eliminar_categoria(user_id, restaurante_id, categoria_id)

@router.post("/menu")
async def crear_menu(
    user_id: str,
    restaurante_id: str,
    nombre: str,
    platos_ids: List[str] = None,  # Lista de IDs de platos Debe pasarse como ["id1", "id2", ...]
    descripcion: str = None,
    service: RestaurantService = Depends(RestaurantService)
):
    return service.crear_menu(user_id=user_id, restaurante_id=restaurante_id, nombre=nombre, descripcion=descripcion, platos_ids=platos_ids)

@router.get("/menus")
async def obtener_menus(
    user_id:str, 
    restaurante_id:str,
    service: RestaurantService = Depends(RestaurantService)
):
    return service.obtener_menus(user_id, restaurante_id)

@router.get("/menu")
async def obtener_menu(
    user_id:str, 
    restaurante_id:str, 
    menu_id:str,
    service: RestaurantService = Depends(RestaurantService)
):
    return service.obtener_menu(user_id, restaurante_id, menu_id)

@router.put("/menu")
async def editar_menu_endpoint(
    user_id: str,
    restaurante_id: str,
    menu_id: str,
    nombre: str = None,
    descripcion: str = None,
    platos: List[str] = None,
    service: RestaurantService = Depends(RestaurantService)
):
    return service.editar_menu(
        user_id=user_id,
        restaurante_id=restaurante_id,
        menu_id=menu_id,
        nombre=nombre,
        descripcion=descripcion,
        platos=platos
    )