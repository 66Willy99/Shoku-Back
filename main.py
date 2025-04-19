import firebase_admin
from firebase_admin import credentials, firestore, auth, db
from fastapi import FastAPI, HTTPException

# Ruta al archivo JSON de credenciales (descargado desde Firebase)
cred = credentials.Certificate("cred.json")

# Inicializar Firebase
firebase_admin.initialize_app(cred, {
    "databaseURL": "https://shoku-76287-default-rtdb.firebaseio.com",
    "storageBucket": "shoku-76287.firebasestorage.app"
})

# Obtener instancias de Firestore y Auth (opcional)
rtdb = db.reference()

app = FastAPI()

@app.get("/users")
async def obtener_usuarios():
    users = rtdb.child("usuarios").get()
    return users

@app.get("/user/{userId}")
async def obtener_usuario(userId: str):
    try:
        ref = db.reference(f"usuarios/{userId}")
        user_data = ref.get()
        if not user_data:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        return { userId: user_data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

#Agregar Restaurante
@app.post("/user/{userId}/add-restaurant")
async def add_restaurant(userId: str, nombre: str, direccion:str, telefono: str):
    try:
        # Referencia al subnodo 'restaurantes' del usuario
        metadata_ref = db.reference(f"usuarios/{userId}/metadata/last_restaurant_id")
        last_id = metadata_ref.get() or -1
        
        new_id = last_id + 1

        restaurant_data = {
            "nombre": nombre,
            "direccion": direccion,
            "telefono": telefono,
        }
        db.reference(f"usuarios/{userId}/restaurantes/{new_id}").set(restaurant_data)
        metadata_ref.set(new_id)
        
        return {"nombre": nombre, "message": "Restaurante creado exitosamente"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Registro de usuario
@app.post("/user/register")
async def register(email: str, password: str):
    try:
        user = auth.create_user(
            email=email,
            password=password,
        )
        userData = {
            "email":email,
            "nivel":0,
            "nombre": "",
        }
        ref = db.reference(f"usuarios/{user.uid}")
        ref.set(userData)

        return {"uid": user.uid, "email": user.email}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))