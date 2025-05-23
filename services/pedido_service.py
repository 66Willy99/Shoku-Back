from firebase_admin import db
from fastapi import HTTPException, status
import datetime

class PedidoService:
    def crear_pedido(self, user_id:str, restaurante_id:str, mesa_id:str, silla_id:str , platos: dict, fecha_actual: str = None):
        try:
            # Validación básica de campos
            if not user_id or user_id.strip() == "":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El ID del usuario no puede estar vacío"
                )
            
            if not restaurante_id or restaurante_id.strip() == "":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El ID del restaurante no puede estar vacío"
                )
            
            if not mesa_id or mesa_id.strip() == "":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El ID de la mesa no puede estar vacío"
                )
            
            if not silla_id or silla_id.strip() == "":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El ID de la silla no puede estar vacío"
                )
            
            if not platos or not isinstance(platos, dict):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Los platos deben ser un diccionario"
                )

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
            # Verificar si la silla existe
            silla_ref = restaurante_ref.child("sillas").child(silla_id)
            if not silla_ref.get():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Silla no encontrada"
                )
            pedido_data = {}
            fecha_actual = fecha_actual or datetime.datetime.now()
            fecha_actual = fecha_actual.timestamp()
            fecha_actual = fecha_actual * 1000
            # Crear la estructura del nuevo pedido
            pedido_data["mesa_id"] = mesa_id
            pedido_data["silla_id"] = silla_id
            pedido_data["estados"] = {"confirmado": fecha_actual, "estado_actual": "confirmado"}
            pedido_data["platos"]= platos
            # Guardar el nuevo pedido
            pedidos_ref = restaurante_ref.child("pedidos")
            nuevo_pedido_ref = pedidos_ref.push()
            nuevo_pedido_ref.set(pedido_data)
            return {
                "message": "Pedido creado exitosamente",
                "pedido_id": nuevo_pedido_ref.key
            }
        
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error interno: {str(e)}"
            )
        
    def obtener_pedidos(self, user_id:str, restaurante_id:str):
        try:
            # Validación básica de campos
            if not user_id or user_id.strip() == "":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El ID del usuario no puede estar vacío"
                )
            
            if not restaurante_id or restaurante_id.strip() == "":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El ID del restaurante no puede estar vacío"
                )
            
            # Obtener referencia al restaurante
            restaurante_ref = db.reference(f"usuarios/{user_id}/restaurantes/{restaurante_id}")
            if not restaurante_ref.get():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Restaurante no encontrado"
                )
            
            # Obtener los pedidos del restaurante
            pedidos_ref = restaurante_ref.child("pedidos")
            pedidos = pedidos_ref.get() or {}  # Si no hay pedidos, crea un dict vacío
            
            return {
                "message": "Pedidos obtenidos exitosamente",
                "pedidos": pedidos
            }
        
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error interno: {str(e)}"
            )
    
    def obtener_pedidos_mesa(self, user_id:str, restaurante_id:str, mesa_id:str):
        try:
            # Validación básica de campos
            if not user_id or user_id.strip() == "":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El ID del usuario no puede estar vacío"
                )
            
            if not restaurante_id or restaurante_id.strip() == "":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El ID del restaurante no puede estar vacío"
                )
            
            if not mesa_id or mesa_id.strip() == "":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El ID de la mesa no puede estar vacío"
                )
            
            # Obtener referencia al restaurante
            restaurante_ref = db.reference(f"usuarios/{user_id}/restaurantes/{restaurante_id}")
            if not restaurante_ref.get():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Restaurante no encontrado"
                )
            
            # Obtener los pedidos del restaurante
            pedidos_ref = restaurante_ref.child("pedidos")
            pedidos = pedidos_ref.get() or {}  # Si no hay pedidos, crea un dict vacío
            
            # Filtrar los pedidos por mesa
            pedidos_mesa = {pedido_id: pedido for pedido_id, pedido in pedidos.items() if pedido.get("mesa_id") == mesa_id}
            
            return {
                "message": "Pedidos obtenidos exitosamente",
                "pedidos": pedidos_mesa
            }
        
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error interno: {str(e)}"
            )
        
    def obtener_pedido(self, user_id:str, restaurante_id:str, pedido_id:str):
        try:
            # Validación básica de campos
            if not user_id or user_id.strip() == "":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El ID del usuario no puede estar vacío"
                )
            
            if not restaurante_id or restaurante_id.strip() == "":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El ID del restaurante no puede estar vacío"
                )
            
            if not pedido_id or pedido_id.strip() == "":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El ID del pedido no puede estar vacío"
                )
            
            # Obtener referencia al restaurante
            restaurante_ref = db.reference(f"usuarios/{user_id}/restaurantes/{restaurante_id}")
            if not restaurante_ref.get():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Restaurante no encontrado"
                )
            
            # Obtener el pedido específico
            pedido = db.reference(f"usuarios/{user_id}/restaurantes/{restaurante_id}/pedido/{pedido_id}").get()
            if not pedido:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Pedido no encontrado")
            return {
                "message": "Pedido obtenido exitosamente",
                "pedido": pedido
            }
        
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error interno: {str(e)}"
            )
        
    def actualizar_estado(self, user_id:str, restaurante_id:str, pedido_id:str, estado_actual:int):
        try:
            # Validación básica de campos
            if not user_id or user_id.strip() == "":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El ID del usuario no puede estar vacío"
                )
            
            if not restaurante_id or restaurante_id.strip() == "":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El ID del restaurante no puede estar vacío"
                )
            
            if not pedido_id or pedido_id.strip() == "":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El ID del pedido no puede estar vacío"
                )
            
            if not estado_actual:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El estado actual no puede estar vacío"
                )
            
            # Obtener referencia al restaurante
            restaurante_ref = db.reference(f"usuarios/{user_id}/restaurantes/{restaurante_id}")
            if not restaurante_ref.get():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Restaurante no encontrado"
                )
            
            # Obtener el pedido específico
            pedido_ref = db.reference(f"usuarios/{user_id}/restaurantes/{restaurante_id}/pedidos/{pedido_id}")
            pedido = pedido_ref.get()
            if not pedido:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Pedido no encontrado")
            
            # Actualizar el estado del pedido

            if estado_actual == 1:
                estado_actual = "preparacion"
            elif estado_actual == 2:
                estado_actual = "terminado"
            elif estado_actual == 3:
                estado_actual = "entregado"
            elif estado_actual == 4:
                estado_actual = "pagado"
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Estado no válido"
                )
            
            # Actualizar el estado en la base de datos
            estados = pedido.get("estados", {})
            estados["estado_actual"] = estado_actual
            estados[estado_actual] = datetime.datetime.now().timestamp() * 1000
            
            # Guardar los cambios
            pedido_ref.update({"estados": estados})
            
            return {
                "message": "Estado actualizado exitosamente",
                "pedido": pedido_ref.get()
            }
        
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=str(e))
