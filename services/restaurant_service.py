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

    def crear_menu(self, user_id: str, restaurante_id: str, nombre: str, descripcion: str, platos_ids: list = None):
        try:
            # Validar que los platos existan (si se proporcionan)
            if platos_ids:
                for plato_id in platos_ids:
                    if not db.reference(f"platos/{plato_id}").get():
                        raise HTTPException(status_code=400, detail=f"El plato {plato_id} no existe en la base de datos")
            
            # Crear menú solo con referencias
            menu_ref = db.reference(f"usuarios/{user_id}/restaurantes/{restaurante_id}/menus").push()
            menu_data = {
                "nombre": nombre,
                "descripcion": descripcion,
                "platos": {pid: True for pid in platos_ids} if platos_ids else {}
            }
            menu_ref.set(menu_data)
            return {"menu_id": menu_ref.key, **menu_data}
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    def obtener_menus(self, user_id: str, restaurante_id: str):
        try:
            menus = db.reference(
                f"usuarios/{user_id}/restaurantes/{restaurante_id}/menus"
            ).get()
            if not menus:
                raise HTTPException(status_code=404, detail="Menus no encontrados")
            return {"menus": menus}
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    def obtener_menu(self, user_id: str, restaurante_id: str, menu_id: str):
        try:
            # Obtener datos del menú
            menu_ref = db.reference(f"usuarios/{user_id}/restaurantes/{restaurante_id}/menus/{menu_id}")
            menu_data = menu_ref.get()
            
            if not menu_data:
                raise HTTPException(status_code=404, detail="Menú no encontrado")
            
            # Obtener stock de cada plato
            platos_con_stock = {}
            for plato_id in menu_data.get("platos", {}):
                plato_data = db.reference(f"platos/{plato_id}").get()
                if plato_data:
                    platos_con_stock[plato_id] = {
                        "nombre": plato_data.get("nombre"),
                        "stock": plato_data.get("stock", 0),
                        "precio": plato_data.get("precio")
                    }
            
            return {
                "menu_id": menu_id,
                "nombre": menu_data.get("nombre"),
                "descripcion": menu_data.get("descripcion"),
                "platos": platos_con_stock  # Datos consolidados
            }
            
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    def editar_menu(self, user_id: str, restaurante_id: str, menu_id: str, nombre: str = None, descripcion: str = None, platos: list = None,):
        try:
            # Referencia al menú específico
            menu_ref = db.reference(
                f"usuarios/{user_id}/restaurantes/{restaurante_id}/menus/{menu_id}"
            )

            # Obtener datos actuales
            current_data = menu_ref.get() or {}

            # Actualizar solo los campos proporcionados
            update_data = {}
            if nombre is not None:
                update_data["nombre"] = nombre
            if descripcion is not None:
                update_data["descripcion"] = descripcion
            if platos is not None:
                update_data["platos"] = {
                    pid: True for pid in platos
                }  # Convertir lista a dict

            # Aplicar actualización
            menu_ref.update(update_data)

            # Devolver datos actualizados
            updated_data = {**current_data, **update_data}
            return {"menu_id": menu_id, **updated_data}

        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    def eliminar_menu(self, user_id: str, restaurante_id: str, menu_id: str):
        try:
            ref = db.reference(
                f"usuarios/{user_id}/restaurantes/{restaurante_id}/menus/{menu_id}"
            )
            if not ref.get():
                raise HTTPException(status_code=404, detail="Menu no encontrado")

            ref.delete()
            return {"message": "Menu eliminado", "menu_id": menu_id}
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
