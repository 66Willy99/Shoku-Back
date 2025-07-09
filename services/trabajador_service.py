from firebase_admin import db
from fastapi import HTTPException, status
import bcrypt

class TrabajadorService:
    
    def hash_password(plain_password: str) -> str:
        hashed = bcrypt.hashpw(plain_password.encode('utf-8'), bcrypt.gensalt())
        return hashed.decode('utf-8')
    
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    
    def crear_trabajador(self, user_id: str, restaurante_id: str, email: str, nombre: str, rol: str, user: str, password_hash: str):
        try:
            # Validación básica de campos
            if not nombre or nombre.strip() == "":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El nombre del trabajador no puede estar vacío"
                )
            
            if not email or email.strip() == "":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El email del trabajador no puede estar vacío"
                )
            
            if not rol or rol.strip() == "":    
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El rol del trabajador no puede estar vacío"
                )
            
            if not user or user.strip() == "":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El usuario del trabajador no puede estar vacío"
                )
            
            if len(password_hash) < 6:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="La contraseña del trabajador debe tener al menos 6 caracteres"
                )
            if not password_hash or password_hash.strip() == "":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="La contraseña del trabajador no puede estar vacía"
                )
            
            password_hash = TrabajadorService.hash_password(password_hash)
                        
            # Obtener referencia al restaurante
            restaurante_ref = db.reference(f"usuarios/{user_id}/restaurantes/{restaurante_id}")
            if not restaurante_ref.get():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Restaurante no encontrado"
                )
            
            # Obtener referencia a los trabajadores del restaurante
            trabajadores_ref = restaurante_ref.child("trabajadores")
            trabajadores = trabajadores_ref.get() or {}  # Si no hay trabajadores, crea un dict vacío
                
            # Verificar si el email ya existe (case insensitive)
            email_lower = email.lower()
            for trabajador_data in trabajadores.values():
                if trabajador_data.get("email", "").lower() == email_lower:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Ya existe un trabajador con ese email"
                    )
                
            # Verificar si el usuario ya existe (case insensitive)
            user_lower = user.lower()
            for trabajador_data in trabajadores.values():
                if trabajador_data.get("user", "").lower() == user_lower:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Ya existe un trabajador con ese usuario"
                    )
                
            
            
            
            # Crear estructura del nuevo trabajador
            trabajador_data = {
                "email": email,
                "nombre": nombre,
                "rol": rol,
                "user": user,
                "password_hash": password_hash
            }
            
            # Guardar el nuevo trabajador
            nuevo_trabajador_ref = trabajadores_ref.push()
            nuevo_trabajador_ref.set(trabajador_data)
            
            return {
                "message": "Trabajador creado exitosamente",
                "trabajador_id": nuevo_trabajador_ref.key,
                **trabajador_data
            }
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al crear trabajador: {str(e)}"
            )
        
    def obtener_trabajadores(self, user_id: str, restaurante_id: str):
        try:
            # Obtener referencia al restaurante
            restaurante_ref = db.reference(f"usuarios/{user_id}/restaurantes/{restaurante_id}")
            if not restaurante_ref.get():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Restaurante no encontrado"
                )
            
            # Obtener los trabajadores
            trabajadores_ref = restaurante_ref.child("trabajadores")
            trabajadores = trabajadores_ref.get() or {}
            
            if not trabajadores:
                raise HTTPException(status_code=404, detail="No hay Trabajadores creados")
            
            return trabajadores
        
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
        
    def obtener_trabajador(self, user_id: str, restaurante_id: str, trabajador_id: str):
        try:
            # Obtener referencia al restaurante
            trabajador = db.reference(f"usuarios/{user_id}/restaurantes/{restaurante_id}/trabajadores/{trabajador_id}").get()
            if not trabajador:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Trabajador no encontrado")
            return trabajador
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=str(e))
            
    def actualizar_trabajador(self, user_id: str, restaurante_id: str, trabajador_id: str, email: str = None, nombre: str = None, rol: str = None, user: str = None):
        try:
            # Obtener referencia al restaurante
            restaurante_ref = db.reference(f"usuarios/{user_id}/restaurantes/{restaurante_id}")
            if not restaurante_ref.get():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Restaurante no encontrado"
                )
            
            # Obtener referencia al trabajador
            trabajador_ref = restaurante_ref.child("trabajadores").child(trabajador_id)
            if not trabajador_ref.get():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Trabajador no encontrado"
                )
            
            # Actualizar solo los campos proporcionados
            updates = {}
            if email is not None:
                if email.strip() == "":
                    email = trabajador_ref.child("email").get()
                updates["email"] = email
            if nombre is None or nombre.strip() == "":
                    raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El nombre del trabajador no puede estar vacío"
                )
            updates["nombre"] = nombre
            if rol is not None:
                if rol not in ["cocinero", "garzon", "admin"]:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Rol inválido. Debe ser 'cocinero', 'garzon' o 'admin'."
                    )
                updates["rol"] = rol
            if user is None or user.strip() == "":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El usuario del trabajador no puede estar vacío"
                )
            updates["user"] = user
            
            if not updates:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No se proporcionaron datos para actualizar"
                )
            
            # Actualizar el trabajador
            trabajador_ref.update(updates)
            
            return {
                "message": "Trabajador actualizado exitosamente",
                "trabajador_id": trabajador_id,
                **updates
            }
        
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        
    def eliminar_trabajador(self, user_id: str, restaurante_id: str, trabajador_id: str):
        try:
            # Obtener referencia al restaurante
            restaurante_ref = db.reference(f"usuarios/{user_id}/restaurantes/{restaurante_id}")
            if not restaurante_ref.get():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Restaurante no encontrado"
                )
            
            # Obtener referencia al trabajador
            trabajador_ref = restaurante_ref.child("trabajadores").child(trabajador_id)
            if not trabajador_ref.get():
                raise HTTPException(status_code=404, detail="Trabajador no encontrado")
            
            # Eliminar el trabajador
            trabajador_ref.delete()
            
            return {
                "message": "Trabajador eliminado exitosamente",
                "trabajador_id": trabajador_id
            }
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    def login_trabajador(self, restaurante_id: str, user: str, password: str):
        usuarios_ref = db.reference("usuarios")
        usuarios = usuarios_ref.get() or {}
        for user_id, usuario in usuarios.items():
            restaurantes = usuario.get("restaurantes", {})
            if restaurante_id in restaurantes:
                trabajadores = restaurantes[restaurante_id].get("trabajadores", {})
                for trabajador_id, trabajador in trabajadores.items():
                    if trabajador.get("user") == user:
                        hashed_password = trabajador.get("password_hash")
                        if hashed_password and TrabajadorService.verify_password(password, hashed_password):
                            return {
                                "message": "Login exitoso",
                                "trabajador_id": trabajador_id,
                                "nombre": trabajador.get("nombre"),
                                "rol": trabajador.get("rol"),
                                "email": trabajador.get("email"),
                                "user_id": user_id,
                                "restaurante_id": restaurante_id
                            }
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
