import firebase_admin
from firebase_admin import credentials, firestore, auth, db
from fastapi import FastAPI

# Ruta al archivo JSON de credenciales (descargado desde Firebase)
cred = credentials.Certificate("cred.json")

# Inicializar Firebase
firebase_admin.initialize_app(cred, {
    'databaseURL' : 'https://shoku-76287-default-rtdb.firebaseio.com/'
})

# Obtener instancias de Firestore y Auth (opcional)
rtdb = db.reference()

app = FastAPI()

@app.get("/users")
async def obtener_usuarios():
    users = rtdb.child("users").get()
    return users

@app.get("/usuario_por_id")
async def buscar_por_email(email: str):
    usuarios = rtdb.child("usuarios").get()
    resultado = [user for user in usuarios.values() if user.get("email") == email]
    return resultado