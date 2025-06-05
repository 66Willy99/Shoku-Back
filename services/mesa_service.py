from fastapi import HTTPException, status
from firebase_admin import db
from grpc import Status
from services.silla_service import SillaService

class MesaService:
    def crear_mesa(self, user_id:str, restaurante_id:str, capacidad:int, estado:str, numero:int):
        try:
            # Verificar si el restaurante existe
            restaurante_ref = db.reference(f"usuarios/{user_id}/restaurantes/{restaurante_id}")
            if not restaurante_ref.get():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Restaurante no encontrado"
                )
            if capacidad <= 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="el numero de la mesa no puede ser cero o negativo"
                )
            # Verificar si la mesa ya existe
            mesas_ref = restaurante_ref.child("mesas")
            mesas = mesas_ref.get() or {}

            # Verificar si ya existe una mesa con el mismo nombre
            
            for mesa_data in mesas.values():
                if mesa_data.get("numero") == numero:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="La mesa ya existe"
                    )

            # Crear la estructura de la nueva mesa
            mesa_data = {
                "capacidad": capacidad,
                "estado": estado,
                "numero": numero,
                
            }
            # Guardar la nueva mesa
            nueva_mesa_ref = restaurante_ref.child("mesas").push()
            nueva_mesa_ref.set(mesa_data)
            return {
                "message": "Mesa creada exitosamente",
                "mesa_id": nueva_mesa_ref.key,
                **mesa_data
            }
        
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error interno: {str(e)}"
            )
        
    def obtener_mesas(self, user_id:str, restaurante_id:str):
        try:
            restaurante_ref = db.reference(f"usuarios/{user_id}/restaurantes/{restaurante_id}")
            if not restaurante_ref.get():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Restaurante no encontrado"
                )
            mesas_ref = restaurante_ref.child("mesas")
            mesas = mesas_ref.get() or {}

            return {
                "message": "Mesas obtenidas exitosamente",
                "mesas": mesas
            }
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error interno: {str(e)}"
            )
    
    def obtener_mesa(self, user_id:str, restaurante_id:str, mesa_id:str):
        try:
            mesa = db.reference(f"usuarios/{user_id}/restaurantes/{restaurante_id}/mesas/{mesa_id}").get()
            if not mesa:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Mesa no encontrada")
            return mesa
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=str(e))
    
    def actualizar_mesa(self, user_id:str, restaurante_id:str, mesa_id:str, capacidad:int=None, estado:str=None, numero:int=None):
        try:
            ref = db.reference(f"usuarios/{user_id}/restaurantes/{restaurante_id}/mesas/{mesa_id}")
            if not ref.get():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, 
                    detail="Mesa no encontrada"
                )
            mesa_data = ref.get()
            if not mesa_data:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mesa no encontrada")
            if capacidad is not None:
                if capacidad <= 0 or capacidad == mesa_data.get("capacidad"):
                    capacidad = mesa_data.get("capacidad")
                    ref.update({"capacidad": capacidad})
                else:
                    ref.update({"capacidad": capacidad})
            if estado is not None:
                estado = estado.strip()
                estado = estado.lower()
                if estado == "":
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El estado de la mesa no puede estar vacío")
                ref.update({"estado": estado})
            if numero is not None:
                if numero <= 0 or numero == mesa_data.get("numero"):
                    numero = mesa_data.get("numero")
                    ref.update({"numero": numero})
                else:
                    ref.update({"numero": numero})

            return {
                "message": "Menú actualizado exitosamente",
                "mesa_id": mesa_id,
                "nuevo_capacidad": capacidad,
                "antiguo_capacidad": mesa_data.get("capacidad"),
                "nuevo_numero": numero,
                "antiguos_numero": mesa_data.get("numero"),
                "nuevo_estado": estado,
                "antiguo_estado": mesa_data.get("estado")
                
            }
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al actualizar menu: {str(e)}"
            )
        
    def eliminar_mesa(self, user_id: str, restaurante_id: str, mesa_id: str):
        try:
            ref = db.reference(f"usuarios/{user_id}/restaurantes/{restaurante_id}/mesas/{mesa_id}")
            if not ref.get():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, 
                    detail="Mesa no encontrada"
                )
            mesa_data = ref.get()
            

            # Obtener todas las sillas del restaurante
            sillas_response = SillaService.obtener_sillas(self, user_id, restaurante_id)
            sillas = sillas_response.get("sillas", {})

            # Filtrar las sillas que pertenecen a la mesa que se va a eliminar
            sillas_a_eliminar = [silla_id for silla_id, silla in sillas.items() if silla.get("mesa_id") == mesa_id]

            # Eliminar cada silla asociada a la mesa
            for silla_id in sillas_a_eliminar:
                SillaService.eliminar_silla(self, user_id, restaurante_id, silla_id)

            ref.delete()

            return {
                "message": "Mesa eliminada exitosamente",
                "mesa_id": mesa_id,
                "mesa_numero": mesa_data.get("numero"),
            }
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al eliminar mesa: {str(e)}"
            )