from firebase_admin import db
from fastapi import HTTPException, status

class CategoryService:    
    def crear_categoria(self, user_id:str, restaurante_id:str, descripcion:str, nombre:str):
        try:
            # Verificar si el restaurante existe
            restaurante_ref = db.reference(f"usuarios/{user_id}/restaurantes/{restaurante_id}")
            if not restaurante_ref.get():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Restaurante no encontrado"
                )
            if not nombre or nombre.strip() == "":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El nombre de la categoria no puede estar vacío"
                )
            # Verificar si la categoría ya existe
            categorias_ref = restaurante_ref.child("categorias")
            categorias = categorias_ref.get() or {}

            # Verificar si ya existe una categoría con el mismo nombre
            nombre_lower = nombre.lower()
            for categoria_data in categorias.values():
                if categoria_data.get("nombre").lower() == nombre_lower:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="La categoría ya existe"
                    )

            # Crear la estructura de la nueva categoría
            categoria_data = {
                "descripcion": descripcion,
                "nombre": nombre
            }
            # Guardar la nueva categoría
            nueva_categoria_ref = restaurante_ref.child("categorias").push()
            nueva_categoria_ref.set(categoria_data)
            return {
                "message": "Categoría creada exitosamente",
                "category_id": nueva_categoria_ref.key,
                **categoria_data
            }
        
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error interno: {str(e)}"
            )
        
    def obtener_categorias(self, user_id:str, restaurante_id:str):
        try:
            # Verificar si el restaurante existe
            restaurante_ref = db.reference(f"usuarios/{user_id}/restaurantes/{restaurante_id}")
            if not restaurante_ref.get():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Restaurante no encontrado"
                )
            
            # Obtener las categorías del restaurante
            categorias_ref = restaurante_ref.child("categorias")
            categorias = categorias_ref.get() or {}
            
            return {
                "message": "Categorías obtenidas exitosamente",
                "categorias": categorias
            }
        
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error interno: {str(e)}"
            )
    
    def obtener_categoria(self, user_id:str, restaurante_id:str, categoria_id:str):
        try:
            categorias = db.reference(f"usuarios/{user_id}/restaurantes/{restaurante_id}/categorias/{categoria_id}").get()
            if not categorias:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Categoria no encontrada")
            return categorias
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=str(e))
    
    def actualizar_categoria(self, user_id:str, restaurante_id:str, categoria_id:str, nombre:str = None, descripcion:str = None):
        try:
            ref = db.reference(f"usuarios/{user_id}/restaurantes/{restaurante_id}/categorias/{categoria_id}")
            if not ref.get():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Categoria no encontrada"
                )
            category_data = ref.get()
            if not category_data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Categoría no encontrada"
                )
            if nombre is not None:
                nombre = nombre.strip()
                if nombre == "":
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="El nombre de la categoria no puede estar vacío"
                    )
                ref.update({"nombre": nombre})
            if descripcion is not None:
                descripcion = descripcion.strip()
                if descripcion == "":
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="La descripción de la categoria no puede estar vacía"
                    )
                ref.update({"descripcion": descripcion})
            
            return {
                "message": "Categoría actualizada exitosamente",
                "categoria_id": categoria_id,
                "nuevo_nombre": nombre,
                "nuevo_descripcion": descripcion,
                "antiguo_nombre": category_data.get("nombre"),
                "antiguo_descripcion": category_data.get("descripcion")
            }
        
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al actualizar categoria: {str(e)}"
            )
    def eliminar_categoria(self, user_id:str, restaurante_id:str, categoria_id:str):
        try:
            categoria_ref = db.reference(f"usuarios/{user_id}/restaurantes/{restaurante_id}/categorias/{categoria_id}")
            if not categoria_ref.get():
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Categoría no encontrada")
            nombre_categoria = categoria_ref.child("nombre").get()
            categoria_ref.delete()
            return {"message": "Categoría eliminada exitosamente","categoria_id": categoria_id,"nombre": nombre_categoria}
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
            