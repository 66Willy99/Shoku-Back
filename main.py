from fastapi import FastAPI
from firebase_config import initialize_firebase
from routers import users, restaurants

# Inicializar Firebase
initialize_firebase()

app = FastAPI()

# Incluir routers
app.include_router(users.router)
app.include_router(restaurants.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the API"}