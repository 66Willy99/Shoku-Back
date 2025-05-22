from firebase_admin import db
from fastapi import HTTPException, status
import datetime

class PedidoService:
    def crear_pedido(self, user_id:str, restaurante_id:str, mesa_id:str, silla_id:str , platos: dict, fecha_actual: str = None):
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