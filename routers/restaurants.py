from fastapi import APIRouter, HTTPException, Depends
from services.restaurant_service import RestaurantService

router = APIRouter(prefix="/user/restaurants", tags=["restaurants"])

@router.post("/")
async def crear_restaurante(
    user_id: str,
    nombre: str,
    direccion: str,
    telefono: str,
    service: RestaurantService = Depends(RestaurantService)
):
    return service.crear_restaurante(user_id, nombre, direccion, telefono)

@router.get("/")
async def obtener_restaurantes(
    # user_id: str = Query(..., description="ID del usuario"),
    service: RestaurantService = Depends(RestaurantService)
):
    return service.obtener_restaurantes()
    

router = APIRouter(prefix="/user/restaurant", tags=["restaurants"])
@router.get("/")
async def obtener_restaurante(
    user_id: str,
    restaurante_id: str,
    service: RestaurantService = Depends(RestaurantService)
):
    return service.obtener_restaurante(user_id, restaurante_id)

@router.put("/")
async def actualizar_restaurante(
    user_id: str,
    restaurante_id: str,
    nombre: str = None,
    direccion: str = None,
    telefono: str = None,
    service: RestaurantService = Depends(RestaurantService)
):
    return service.actualizar_restaurante(
        user_id, restaurante_id, nombre, direccion, telefono
    )

@router.delete("/")
async def eliminar_restaurante(
    user_id: str,
    restaurante_id: str,
    service: RestaurantService = Depends(RestaurantService)
):
    return service.eliminar_restaurante(user_id, restaurante_id)

router = APIRouter(prefix="/user/restaurant/category", tags=["restaurants"])

@router.post("/")
async def crear_categoria(
    user_id:str, 
    restaurante_id:str, 
    descripcion:str, 
    nombre:str,
    service: RestaurantService = Depends(RestaurantService)
):
    return service.crear_categoria(user_id, restaurante_id, descripcion, nombre)