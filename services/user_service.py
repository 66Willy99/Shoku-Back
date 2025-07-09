from firebase_admin import auth, db
from fastapi import HTTPException, status
from config import FIREBASE_CONFIG
import requests
import time
import time

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
            
            return response_data
            
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

    def editUser(self, userId: str, newName: str = None, newEmail: str = None):
        try:
            ref = db.reference(f"usuarios/{userId}")
            user_data = ref.get()
            
            if not user_data:
                raise HTTPException(status_code=404, detail="Usuario no encontrado")
            if newEmail is not None:
                auth.update_user(userId, email=newEmail)
                ref.update({"email": newEmail})
            if newName is not None:
                auth.update_user(userId, display_name=newName) 
                ref.update({"nombre": newName})
            return {"message": "Nombre actualizado exitosamente", 
                    "Nuevo Nombre": newName, 
                    "Nuevo Email": newEmail,
                    "Antiguo Nombre": user_data.get("nombre"),
                    "Antiguo Email": user_data.get("email")}
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    def actualizar_nivel_suscripcion(self, userId: str, nuevo_nivel: int):
        """
        Actualiza el nivel de suscripción del usuario.
        
        Args:
            userId: ID del usuario
            nuevo_nivel: Nuevo nivel de suscripción (0: gratuito, 1: basico, 2: premium)
        """
        try:
            # Validar que el nivel sea válido
            if nuevo_nivel < 0 or nuevo_nivel > 5:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El nivel de suscripción debe estar entre 0 y 5"
                )
            
            ref = db.reference(f"usuarios/{userId}")
            user_data = ref.get()
            
            if not user_data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Usuario no encontrado"
                )
            
            nivel_anterior = user_data.get("nivel", 0)
            
            # Actualizar el nivel en Firebase
            ref.update({
                "nivel": nuevo_nivel,
                "fecha_actualizacion_nivel": int(time.time() * 1000)
            })
            
            return {
                "message": "Nivel de suscripción actualizado exitosamente",
                "userId": userId,
                "nivel_anterior": nivel_anterior,
                "nivel_actual": nuevo_nivel,
                "fecha_actualizacion": int(time.time() * 1000)
            }
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al actualizar nivel de suscripción: {str(e)}"
            )

    def obtener_perfil_usuario(self, userId: str):
        """
        Obtiene el perfil completo del usuario con información de suscripción.
        """
        try:
            ref = db.reference(f"usuarios/{userId}")
            user_data = ref.get()
            
            if not user_data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Usuario no encontrado"
                )
            
            # Obtener información del nivel de suscripción
            nivel_actual = user_data.get("nivel", 0)
            
            niveles_info = {
                0: {"nombre": "Gratuito", "max_restaurantes": 1, "max_mesas": 2, "max_sillas": 10},
                1: {"nombre": "Básico", "max_restaurantes": 2, "max_mesas": 15, "max_sillas": 30},
                2: {"nombre": "Premium", "max_restaurantes": 5, "max_mesas": 50, "max_sillas": 100}
            }
            
            info_nivel = niveles_info.get(nivel_actual, niveles_info[0])
            
            # Contar restaurantes actuales
            restaurantes_actuales = len(user_data.get("restaurantes", {}))
            
            return {
                "userId": userId,
                "email": user_data.get("email", ""),
                "nombre": user_data.get("nombre", ""),
                "nivel": nivel_actual,
                "info_suscripcion": {
                    "nombre_plan": info_nivel["nombre"],
                    "restaurantes_actuales": restaurantes_actuales,
                    "max_restaurantes": info_nivel["max_restaurantes"],
                    "max_mesas": info_nivel["max_mesas"],
                    "puede_crear_restaurante": (
                        info_nivel["max_restaurantes"] == -1 or 
                        restaurantes_actuales < info_nivel["max_restaurantes"]
                    )
                },
                "fecha_actualizacion_nivel": user_data.get("fecha_actualizacion_nivel")
            }
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al obtener perfil de usuario: {str(e)}"
            )