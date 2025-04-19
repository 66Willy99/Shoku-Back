from firebase_admin import auth, db
from fastapi import HTTPException

class UserService:
    def obtener_usuarios(self):
        users = db.reference("usuarios").get()
        return users

    def obtener_usuario(self, userId: str):
        try:
            ref = db.reference(f"usuarios/{userId}")
            user_data = ref.get()
            if not user_data:
                raise HTTPException(status_code=404, detail="Usuario no encontrado")
            return {userId: user_data}
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    def register(self, email: str, password: str):
        try:
            user = auth.create_user(
                email=email,
                password=password,
            )
            userData = {
                "email": email,
                "nivel": 0,
                "nombre": "",
            }
            ref = db.reference(f"usuarios/{user.uid}")
            ref.set(userData)
            return {"uid": user.uid, "email": user.email}
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    def edit_user_name(self, userId: str, new_name: str):
        try:
            ref = db.reference(f"usuarios/{userId}")
            user_data = ref.get()
            
            if not user_data:
                raise HTTPException(status_code=404, detail="Usuario no encontrado")
            
            ref.update({"nombre": new_name})
            return {"message": "Nombre actualizado exitosamente", "new_name": new_name}
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))