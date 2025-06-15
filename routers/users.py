from fastapi import APIRouter, HTTPException, Depends, status, Body
from fastapi.security import OAuth2PasswordRequestForm
from services.user_service import UserService
from firebase_admin import auth


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
async def register(email: str= Body(...), password: str = Body(...), service: UserService = Depends(UserService)):
    return service.register(email, password)

@router.put("/edit")
async def editUser(newData : dict = Body(...), service: UserService = Depends(UserService)):
    try:
        userId = newData.get("userId")
        newName = newData.get("newName")
        newEmail = newData.get("newEmail")

        if newEmail == "":
            newEmail = None
        if newName == "":
            newName = None
            
        return service.editUser(userId, newName, newEmail)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno: {str(e)}"
        )

@router.post("/reset-test-user")
async def reset_test_user():
    test_email = "prueba@prueba.com"
    new_password = "prueba123"
    
    try:
        user = auth.get_user_by_email(test_email)
        auth.update_user(user.uid, password=new_password)
        return {"message": "Contraseña actualizada"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))