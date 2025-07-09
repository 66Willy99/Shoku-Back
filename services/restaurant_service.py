from firebase_admin import db
from fastapi import HTTPException, status

class RestaurantService:
    def crear_restaurante(self, user_id: str, nombre: str, direccion: str, telefono: str):
        try:
            # Validación básica de campos
            if not nombre or nombre.strip() == "":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El nombre del restaurante no puede estar vacío"
                )
            
            # Obtener referencia a los restaurantes del usuario
            restaurantes_ref = db.reference(f"usuarios/{user_id}/restaurantes")
            restaurantes = restaurantes_ref.get() or {}  # Si no hay restaurantes, crea un dict vacío
            
            # Verificar si el nombre ya existe (case insensitive)
            nombre_lower = nombre.lower()
            for restaurante_data in restaurantes.items():
                if restaurante_data.get("nombre", "").lower() == nombre_lower:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Ya existe un restaurante con ese nombre"
                    )
            
            # Crear estructura del nuevo restaurante
            restaurante_data = {
                "nombre": nombre,
                "direccion": direccion,
                "telefono": telefono,
                "categorias": {},
                "menus": {},
                "mesas": {},
                "pagos": {},
                "pedidos": {},
                "platos": {},
                "sillas": {},
                "trabajadores": {}
            }
            
            # Guardar el nuevo restaurante
            nuevo_restaurante_ref = restaurantes_ref.push()
            nuevo_restaurante_ref.set(restaurante_data)
            
            return {
                "message": "Restaurante creado exitosamente",
                "restaurante_id": nuevo_restaurante_ref.key,
                **restaurante_data
            }
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al crear restaurante: {str(e)}"
            )

    def obtener_restaurantes(self, user_id: str):
        try:
            restaurantes = db.reference(f"usuarios/{user_id}/restaurantes").get()
            if not restaurantes:
                raise HTTPException(status_code=404, detail="No hay Restaurantes creados")
            return restaurantes
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    def obtener_restaurante(self, user_id: str, restaurante_id: str):
        try:
            ref = db.reference(f"usuarios/{user_id}/restaurantes/{restaurante_id}")
            restaurante = ref.get()
            if not restaurante:
                raise HTTPException(status_code=404, detail="Restaurante no encontrado")
            return {"restaurante_id": restaurante_id, **restaurante}
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    def actualizar_restaurante(
        self, 
        user_id: str, 
        restaurante_id: str, 
        nombre: str = None,
        direccion: str = None,
        telefono: str = None
    ):
        try:
            ref = db.reference(f"usuarios/{user_id}/restaurantes/{restaurante_id}")
            
            # Validar que el restaurante existe
            if not ref.get():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Restaurante no encontrado"
                )
            # Actualizar solo los campos proporcionados
            updates = {}
            if nombre is not None:
                updates["nombre"] = nombre
            if direccion is not None:
                updates["direccion"] = direccion
            if telefono is not None:
                updates["telefono"] = telefono
            if not updates:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No hay datos para actualizar"
                )
            # Aplicar actualización
            ref.update(updates)

            return {
                "message": "Restaurante actualizado exitosamente",
                "restaurante_id": restaurante_id,
                **updates
            }
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al actualizar restaurante: {str(e)}"
            )

    def eliminar_restaurante(self, user_id: str, restaurante_id: str):
        try:
            ref = db.reference(f"usuarios/{user_id}/restaurantes/{restaurante_id}")
            if not ref.get():
                raise HTTPException(status_code=404, detail="Restaurante no encontrado")
            nombre = ref.child("nombre").get()
            ref.delete()
            return {"message": "Restaurante eliminado", "restaurante_id": restaurante_id, "nombre": nombre}
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
    
