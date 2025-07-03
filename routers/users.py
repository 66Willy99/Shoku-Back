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

@router.put("/suscripcion")
async def actualizar_nivel_suscripcion(
    datos_suscripcion: dict = Body(...), 
    service: UserService = Depends(UserService)
):
    """
    Actualiza el nivel de suscripción del usuario.
    
    Body parameters:
    - userId: ID del usuario
    - nivel: Nuevo nivel de suscripción (0: gratuito, 1: básico, 2: premium, 3: enterprise)
    """
    try:
        userId = datos_suscripcion.get("userId")
        nivel = datos_suscripcion.get("nivel")
        
        if not userId:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="El userId es requerido"
            )
            
        if nivel is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="El nivel de suscripción es requerido"
            )
            
        # Validar que nivel sea un entero
        try:
            nivel = int(nivel)
        except (ValueError, TypeError):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="El nivel debe ser un número entero"
            )
            
        return service.actualizar_nivel_suscripcion(userId, nivel)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno: {str(e)}"
        )

@router.get("/niveles-suscripcion")
async def obtener_niveles_suscripcion():
    """
    Obtiene información sobre los niveles de suscripción disponibles.
    """
    niveles = {
        0: {
            "nombre": "Gratuito",
            "descripcion": "Funcionalidades básicas",
            "max_restaurantes": 1,
            "max_mesas": 5,
            "reportes_avanzados": False
        },
        1: {
            "nombre": "Básico",
            "descripcion": "Plan básico con más funciones",
            "max_restaurantes": 2,
            "max_mesas": 15,
            "reportes_avanzados": True
        },
        2: {
            "nombre": "Premium",
            "descripcion": "Plan premium con funciones avanzadas",
            "max_restaurantes": 5,
            "max_mesas": 50,
            "reportes_avanzados": True
        },
        3: {
            "nombre": "Enterprise",
            "descripcion": "Plan empresarial sin límites",
            "max_restaurantes": -1,  # -1 significa ilimitado
            "max_mesas": -1,
            "reportes_avanzados": True
        }
    }
    
    return {
        "message": "Niveles de suscripción obtenidos exitosamente",
        "niveles": niveles
    }

@router.get("/perfil")
async def obtener_perfil_usuario(
    userId: str, 
    service: UserService = Depends(UserService)
):
    """
    Obtiene el perfil completo del usuario con información de suscripción.
    """
    return service.obtener_perfil_usuario(userId)