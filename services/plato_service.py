from firebase_admin import db
from fastapi import HTTPException, status

class PlatoService:
    def crear_plato(self, user_id:str, restaurante_id:str, 
                    categoria_id:str, descripcion:str, imagenUrl:list,
                    nombre:str, precio:float, stock:int):
        try:
            # Verificar si el restaurante existe
            restaurante_ref = db.reference(f"usuarios/{user_id}/restaurantes/{restaurante_id}")
            if not restaurante_ref.get():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Restaurante no encontrado"
                )
            if precio <= 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="el precio no puede ser cero o negativo"
                )
            # Verificar si el plato ya existe
            platos_ref = restaurante_ref.child("platos")
            platos = platos_ref.get() or {}

            # Verificar si ya existe un plato con el mismo nombre
            for plato_data in platos.values():
                if plato_data.get("nombre") == nombre:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="El plato ya existe"
                    )

            # Crear la estructura del nuevo plato
            plato_data = {
                "categoria_id": categoria_id,
                "descripcion": descripcion,
                "imagenUrl": imagenUrl,
                "nombre": nombre,
                "precio": precio,
                "stock": stock,
            }
            # Guardar el nuevo plato
            nuevo_plato_ref = restaurante_ref.child("platos").push()
            nuevo_plato_ref.set(plato_data)
            return {
                "message": "Plato creado exitosamente",
                "plato_id": nuevo_plato_ref.key,
                **plato_data
            }
        
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error interno: {str(e)}"
            )
        
    def obtener_platos(self, user_id:str, restaurante_id:str):
        try:
            restaurante_ref = db.reference(f"usuarios/{user_id}/restaurantes/{restaurante_id}")
            if not restaurante_ref.get():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Restaurante no encontrado"
                )
            platos_ref = restaurante_ref.child("platos")
            platos = platos_ref.get() or {}

            return {
                "message": "Platos obtenidos exitosamente",
                "platos": platos
            }
        
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error interno: {str(e)}"
            )

    def obtener_plato(self, user_id:str, restaurante_id:str, plato_id:str):
        try:
            plato = db.reference(f"usuarios/{user_id}/restaurantes/{restaurante_id}/platos/{plato_id}").get()
            if not plato:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Plato no encontrado")
            return plato
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=str(e))
        
    def actualizar_plato(self, user_id:str, restaurante_id:str, plato_id:str,
                        categoria_id:str= None, descripcion:str= None, imagenUrl:list= None,
                        nombre:str= None, precio:float= None, stock:int= None):
        try:
            ref = db.reference(f"usuarios/{user_id}/restaurantes/{restaurante_id}/platos/{plato_id}")
            plato_data = ref.get()
            if not plato_data.get():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, 
                    detail="Plato no encontrado"
                )
            
            if categoria_id is not None:
                ref.update({"categoria_id": categoria_id})
            if descripcion is not None:
                descripcion = descripcion.strip()
                descripcion = descripcion.lower()
                if descripcion == "":
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="La descripción no puede estar vacía"
                    )
                ref.update({"descripcion": descripcion})
                descripcion = plato_data.get("descripcion")
            if imagenUrl is not None:
                if len(imagenUrl) > 3:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="No se pueden asignar más de 3 imágenes a un plato"
                    )
                ref.update({"imagenUrl": imagenUrl})
            if nombre is not None:
                nombre = nombre.strip()
                nombre = nombre.lower()
                if nombre == "":
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="El nombre del plato no puede estar vacío"
                    )
                ref.update({"nombre": nombre})
            if precio is not None:
                if precio <= 0:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="El precio no puede ser cero o negativo"
                    )
                ref.update({"precio": precio})
            if stock is not None:
                if stock < 0:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="El stock no puede ser negativo"
                    )
                ref.update({"stock": stock})
            # Verificar si el precio es válido
            if precio <= 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El precio no puede ser cero o negativo"
                )
            ref.update({"precio": precio})
            
            return {
                "message": "Plato actualizado exitosamente",
                "plato_id": plato_id,
                "nuevo_categoria_id": categoria_id,
                "antiguo_categoria_id": plato_data.get("categoria_id"),
                "nuevo_descripcion": descripcion,
                "antiguo_descripcion": plato_data.get("descripcion"),
                "nuevo_imagenUrl": imagenUrl,
                "antiguo_imagenUrl": plato_data.get("imagenUrl"),
                "nuevo_nombre": nombre,
                "antiguo_nombre": plato_data.get("nombre"),
                "nuevo_precio": precio,
                "antiguo_precio": plato_data.get("precio"),
                "nuevo_stock": stock,
                "antiguo_stock": plato_data.get("stock")

            }
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error interno: {str(e)}"
            )
        
    def eliminar_plato(self, user_id:str, restaurante_id:str, plato_id:str):
        try:
            ref = db.reference(f"usuarios/{user_id}/restaurantes/{restaurante_id}/platos/{plato_id}")
            if not ref.get():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, 
                    detail="Plato no encontrado"
                )
            plato_data = ref.get()
            ref.delete()
            return {
                "message": "Plato eliminado exitosamente",
                "plato_id": plato_id,
                "plato_nombre": plato_data.get("nombre"),
            }
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error interno: {str(e)}"
            )