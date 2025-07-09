from firebase_admin import db
from fastapi import HTTPException, status

class MenuService:
    def crear_menu(self, user_id:str, restaurante_id:str, descripcion:str, nombre:str, platos: list = None):
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
                    detail="El nombre del menu no puede estar vacío"
                )
            # Verificar si el menú ya existe
            menus_ref = restaurante_ref.child("menus")
            menus = menus_ref.get() or {}

            # Verificar si ya existe un menú con el mismo nombre
            nombre_lower = nombre.lower()
            for menu_data in menus.values():
                if menu_data.get("nombre").lower() == nombre_lower:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="El menú ya existe"
                    )

            # Crear la estructura del nuevo menú
            menu_data = {
                "descripcion": descripcion,
                "nombre": nombre,
                "platos": platos if platos is not None else []
            }
            # Guardar el nuevo menú
            nuevo_menu_ref = restaurante_ref.child("menus").push()
            nuevo_menu_ref.set(menu_data)
            return {
                "message": "Menú creado exitosamente",
                "menu_id": nuevo_menu_ref.key,
                **menu_data
            }
        
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error interno: {str(e)}"
            )
    
    def obtener_menus(self, user_id:str, restaurante_id:str):
        try:
            # Verificar si el restaurante existe
            restaurante_ref = db.reference(f"usuarios/{user_id}/restaurantes/{restaurante_id}")
            if not restaurante_ref.get():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Restaurante no encontrado"
                )
            # Obtener los menús
            menus_ref = restaurante_ref.child("menus")
            menus = menus_ref.get() or {}
            return {
                "message": "Menús obtenidos exitosamente",
                "menus": menus
            }
        
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error interno: {str(e)}"
            )
    
    def obtener_menu(self, user_id:str, restaurante_id:str, menu_id:str):
        try:
            menu = db.reference(f"usuarios/{user_id}/restaurantes/{restaurante_id}/menus/{menu_id}").get()
            if not menu:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Menú no encontrado")
            return menu
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=str(e))
    
    def actualizar_menu(self, user_id:str, restaurante_id:str, menu_id:str, nombre:str = None, descripcion:str = None, platos: list = None):
        try:
            ref = db.reference(f"usuarios/{user_id}/restaurantes/{restaurante_id}/menus/{menu_id}")
            if not ref.get():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, 
                    detail="Menu no encontrado"
                )
            menu_data = ref.get()
            if not menu_data:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Menu no encontrado")
            if nombre is not None:
                nombre = nombre.strip()
                if nombre == "":
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El nombre del menú no puede estar vacío")
                ref.update({"nombre": nombre})
            if descripcion is not None:
                descripcion = descripcion.strip()
                if descripcion == "":
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La descripción del menú no puede estar vacía")
                ref.update({"descripcion": descripcion})
            if platos is not None:
                ref.update({"platos": platos})

            return {
                "message": "Menú actualizado exitosamente",
                "menu_id": menu_id,
                "nuevo_nombre": nombre,
                "nuevo_descripcion": descripcion,
                "antiguo_nombre": menu_data.get("nombre"),
                "antiguo_descripcion": menu_data.get("descripcion"),
                "nuevos_platos": platos,
                "antiguos_platos": menu_data.get("platos")
            }
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al actualizar menu: {str(e)}"
            )
    
    def eliminar_menu(self, user_id:str, restaurante_id:str, menu_id:str):
        try:
            menu_ref = db.reference(f"usuarios/{user_id}/restaurantes/{restaurante_id}/menus/{menu_id}")
            if not menu_ref.get():
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Menu no encontrado")
            nombre_menu = menu_ref.get().get("nombre")
            menu_ref.delete()
            return {"message": "Menú eliminado exitosamente","menu_id": menu_id,"nombre_menu": nombre_menu}
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )