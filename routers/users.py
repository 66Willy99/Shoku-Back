from fastapi import APIRouter, HTTPException, Depends
from services.user_service import UserService

router = APIRouter()

@router.get("/users")
async def obtener_usuarios(service: UserService = Depends(UserService)):
    return service.obtener_usuarios()

@router.get("/user")
async def obtener_usuario(userId: str, service: UserService = Depends(UserService)):
    return service.obtener_usuario(userId)

@router.post("/user/register")
async def register(email: str, password: str, service: UserService = Depends(UserService)):
    return service.register(email, password)

@router.put("/user/edit-name")
async def edit_user_name(userId: str, new_name: str, service: UserService = Depends(UserService)):
    return service.edit_user_name(userId, new_name)