from fastapi import APIRouter, HTTPException, Depends, status, Body
from fastapi.security import OAuth2PasswordRequestForm
from services.user_service import UserService


router = APIRouter(prefix="/user", tags=["users"])

@router.get("s/")
async def obtener_usuarios(service: UserService = Depends(UserService)):
    return service.obtener_usuarios()

@router.get("/")
async def obtener_usuario(userId: str, service: UserService = Depends(UserService)):
    return service.obtener_usuario(userId)

@router.post("/auth", status_code=status.HTTP_200_OK)
async def login(credentials: dict = Body(...), service: UserService = Depends(UserService)):
    try:
        email = credentials.get("email")
        password = credentials.get("password")
        
        if not email or not password:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Email y contraseña son requeridos"
            )
            
        return service.login(email, password)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno: {str(e)}"
        )

@router.post("/register")
async def register(email: str, password: str, service: UserService = Depends(UserService)):
    return service.register(email, password)

@router.put("/edit-name")
async def edit_user_name(userId: str, new_name: str, service: UserService = Depends(UserService)):
    return service.edit_user_name(userId, new_name)