from fastapi import FastAPI
from firebase_config import initialize_firebase
from routers import users, restaurants, categories, menus, mesas, sillas, platos, pedidos, trabajador, webSockets, reportes
from fastapi.middleware.cors import CORSMiddleware
from routers import pagos

# Inicializar Firebase
initialize_firebase()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especifica tus dominios
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Incluir routers
app.include_router(users.router)
app.include_router(restaurants.router)
app.include_router(categories.router)
app.include_router(menus.router)
app.include_router(mesas.router)
app.include_router(sillas.router)
app.include_router(platos.router)
app.include_router(pedidos.router)
app.include_router(trabajador.router)
app.include_router(pagos.router)
app.include_router(webSockets.router)
app.include_router(reportes.router)

@app.get("/")
def main():
    return {"message": "Welcome to the API"}