from firebase_admin import auth, db
from fastapi import HTTPException, status
from config import FIREBASE_CONFIG
import requests

class UserService:
    def obtener_usuarios(self):
        users = db.reference("usuarios").get()
        return users

    def obtener_usuario(self, userId: str):
        try:
            ref = db.reference(f"usuarios/{userId}")
            user_data = ref.get()
            if not user_data:
                raise HTTPException(status_code=404, detail="Usuario no encontrado")
            return {userId: user_data}
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    def login(self, email: str, password: str):
        try:
            # Paso 1: Obtener usuario por email (verifica si existe)
            user = auth.get_user_by_email(email)
            
            # Paso 2: Verificar contraseña (requiere autenticación con REST API)
            # Creamos una función auxiliar para esto
            return self._verify_password(email, password, user.uid)
            
        except auth.UserNotFoundError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no registrado"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error de autenticación: {str(e)}"
            )
    
    def _verify_password(self, email: str, password: str, uid: str):
        try:
            response = requests.post(
                f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_CONFIG['webApiKey']}",
                json={
                    "email": email,
                    "password": password,
                    "returnSecureToken": True
                },
                timeout=10  # Agrega timeout
            )
            
            response.raise_for_status()  # Lanza excepción para códigos 4xx/5xx
            response_data = response.json()
            
            return {
                "uid": uid,
                "email": email,
                "token": response_data["idToken"],
                "refreshToken": response_data.get("refreshToken", "")
            }
            
        except requests.exceptions.RequestException as e:
            error_msg = "Error al comunicarse con Firebase"
            if e.response is not None:
                error_data = e.response.json()
                error_msg = error_data.get("error", {}).get("message", "Credenciales inválidas")
            
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=error_msg
            )

    def register(self, email: str, password: str):
        try:
            user = auth.create_user(
                email=email,
                password=password,
            )
            userData = {
                "email": email,
                "nivel": 0,
                "nombre": "",
            }
            ref = db.reference(f"usuarios/{user.uid}")
            ref.set(userData)
            return {"uid": user.uid, "email": user.email}
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    def edit_user_name(self, userId: str, new_name: str):
        try:
            ref = db.reference(f"usuarios/{userId}")
            user_data = ref.get()
            
            if not user_data:
                raise HTTPException(status_code=404, detail="Usuario no encontrado")
            
            ref.update({"nombre": new_name})
            return {"message": "Nombre actualizado exitosamente", "new_name": new_name}
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))