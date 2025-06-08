from firebase_admin import db
from fastapi import HTTPException, status

class SillaService:
    def crear_silla(self, user_id:str, restaurante_id:str, mesa_id:str, numero: int):
        try:
            # Verificar si el restaurante existe
            restaurante_ref = db.reference(f"usuarios/{user_id}/restaurantes/{restaurante_id}")
            if not restaurante_ref.get():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Restaurante no encontrado"
                )
            # Verificar si la mesa existe
            mesa_ref = restaurante_ref.child("mesas").child(mesa_id)
            if not mesa_ref.get():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Mesa no encontrada"
                )
            # Verificar si la silla ya existe
            silla_ref = restaurante_ref.child("sillas")
            silla = silla_ref.get() or {}

            # Verificar si ya existe una silla con el mismo número
            for silla_data in silla.values():
                if silla_data.get("numero") == numero and silla_data.get("mesa_id") == mesa_id:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="El nro de silla ya existe en esta mesa"
                    )

            # Crear la estructura de la nueva silla
            silla_data = {
                "mesa_id": mesa_id,
                "numero": numero,
            }
            # Guardar la nueva silla
            nueva_silla_ref = silla_ref.push()
            nueva_silla_ref.set(silla_data)
            return {
                "message": "Silla creada exitosamente",
                "silla_id": nueva_silla_ref.key,
                **silla_data
            }
        
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error interno: {str(e)}"
            )
        
    def obtener_sillas(self, user_id:str, restaurante_id:str):
        try:
            # Verificar si el restaurante existe
            sillas_ref = db.reference(f"usuarios/{user_id}/restaurantes/{restaurante_id}/sillas")
            if not sillas_ref.get():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Restaurante no encontrado"
                )
            return {
                "message": "Sillas obtenidas exitosamente",
                "sillas": sillas_ref.get()
            }
        
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error interno: {str(e)}"
            )
        
    def obtener_silla(self, user_id:str, restaurante_id:str, silla_id:str):
        try:
            # Verificar si el restaurante existe
            silla_ref = db.reference(f"usuarios/{user_id}/restaurantes/{restaurante_id}/sillas/{silla_id}").get()
            if not silla_ref:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Silla no encontrada"
                )
            return {
                "message": "Silla obtenida exitosamente",
                "silla": silla_ref
            }
        
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error interno: {str(e)}"
            )
    
    def actualizar_silla(self, user_id:str, restaurante_id:str, silla_id:str, numero:int=None, mesa_id:str=None):
        try:
            # Verificar si el restaurante existe
            ref = db.reference(f"usuarios/{user_id}/restaurantes/{restaurante_id}/sillas/{silla_id}")
            if not ref.get():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, 
                    detail="Silla no encontrada"
                )
            silla_data = ref.get()
            # Actualizar los campos de la silla
            if numero is not None:
                if numero <= 0:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="El número de la silla debe ser mayor a 0"
                    )
                ref.update({"numero": numero})
            if mesa_id is not None:
                if mesa_id == "":
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="El ID de la mesa no puede estar vacío"
                    )
                ref.update({"mesa_id": mesa_id})
            return {
                "message": "Silla actualizada exitosamente",
                "silla_id": silla_id,
                "nuevo_numero": numero,
                "antiguo_numero": silla_data.get("numero"),
                "nuevo_mesa_id": mesa_id,
                "antiguo_mesa_id": silla_data.get("mesa_id")
            }
        
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error interno: {str(e)}"
            )
        
    def eliminar_silla(self, user_id:str, restaurante_id:str, silla_id:str):
        try:
            # Verificar si el restaurante existe
            ref = db.reference(f"usuarios/{user_id}/restaurantes/{restaurante_id}/sillas/{silla_id}")
            if not ref.get():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, 
                    detail="Silla no encontrada"
                )
            silla_data = ref.get()
            ref.delete()
            return {
                "message": "Silla eliminada exitosamente",
                "silla_id": silla_id,
                "mesa_id": silla_data.get("mesa_id"),
                "silla_numero": silla_data.get("numero")
            }
        
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error interno: {str(e)}"
            )