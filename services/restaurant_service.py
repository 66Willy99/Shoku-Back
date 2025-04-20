from firebase_admin import db
from fastapi import HTTPException

class RestaurantService:
    def crear_restaurante(self, user_id: str, nombre: str, direccion: str, telefono: str):
        try:
            restaurante_ref = db.reference(f"usuarios/{user_id}/restaurantes").push()
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
            restaurante_ref.set(restaurante_data)

            #restaurante_ref.key es una referencia al mismo restaurante con su key, o lo que es lo mismo un ID unico para el restaurante
            return {"restaurante_id": restaurante_ref.key, **restaurante_data} 
            
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    def obtener_restaurantes(self, user_id: str):
        try:
            restaurantes = db.reference(f"usuarios/{user_id}/restaurantes").get()
            if not restaurantes:
                raise HTTPException(status_code=404, detail="Restaurante no encontrado")
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
        self, user_id: str, restaurante_id: str, nombre: str = None, 
        direccion: str = None, telefono: str = None
    ):
        try:
            ref = db.reference(f"usuarios/{user_id}/restaurantes/{restaurante_id}")
            updates = {}
            if nombre: updates["nombre"] = nombre
            if direccion: updates["direccion"] = direccion
            if telefono: updates["telefono"] = telefono
            
            if not updates:
                raise HTTPException(status_code=400, detail="No hay datos para actualizar")
            
            ref.update(updates)
            return {"message": "Restaurante actualizado", "restaurante_id": restaurante_id, **updates}
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    def eliminar_restaurante(self, user_id: str, restaurante_id: str):
        try:
            ref = db.reference(f"usuarios/{user_id}/restaurantes/{restaurante_id}")
            if not ref.get():
                raise HTTPException(status_code=404, detail="Restaurante no encontrado")
            
            ref.delete()
            return {"message": "Restaurante eliminado", "restaurante_id": restaurante_id}
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    def crear_categoria(self, user_id:str, restaurante_id:str, descripcion:str, nombre:str):
        try:
            categoria_ref= db.reference(f"usuarios/{user_id}/restaurantes/{restaurante_id}/categorias").push()
            categoria_data = {
                "descripcion" : descripcion,
                "nombre" : nombre
            }
            categoria_ref.set(categoria_data)
            return {"categoria_id": categoria_ref.key, **categoria_data}
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    def obtener_categorias(self, user_id:str, restaurante_id:str):
        try:
            categorias = db.reference(f"usuarios/{user_id}/restaurantes/{restaurante_id}/categorias").get()
            # categorias_nombre = [categoria['nombre'] for categoria in categorias.values()] # Esto es para obtener solo los nombres de las categorias, pero no se si es necesario
            if not categorias:
                raise HTTPException(status_code=404, detail="Categorias no encontradas")
            return {"categorias": categorias}
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    def editar_categoria(self, user_id:str, restaurante_id:str, categoria_id:str, descripcion:str=None, nombre:str=None):
        try:
            ref = db.reference(f"usuarios/{user_id}/restaurantes/{restaurante_id}/categorias/{categoria_id}")
            updates = {}
            if descripcion: updates["descripcion"] = descripcion #valida si descripcion no es None y si no lo es, lo agrega al diccionario de updates
            if nombre: updates["nombre"] = nombre                #(Tenia una forma de llamarse el if de esta manera pero no la recuerdo) xd
            
            if not updates:
                raise HTTPException(status_code=400, detail="No hay datos para actualizar")
            
            ref.update(updates)
            return {"message": "Categoria actualizada", "categoria_id": categoria_id, **updates}
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
        
    def eliminar_categoria(self, user_id:str, restaurante_id:str, categoria_id:str):
        try:
            ref = db.reference(f"usuarios/{user_id}/restaurantes/{restaurante_id}/categorias/{categoria_id}")
            if not ref.get():
                raise HTTPException(status_code=404, detail="Categoria no encontrada")
            
            ref.delete()
            return {"message": "Categoria eliminada", "categoria_id": categoria_id}
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))