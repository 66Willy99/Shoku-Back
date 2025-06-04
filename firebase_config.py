import firebase_admin
from firebase_admin import credentials, db
from config import FIREBASE_CONFIG

def initialize_firebase():
    # Cargar credenciales
    cred = credentials.Certificate("cred.json")
    
    # Configuración de inicialización con la URL del archivo config
    firebase_config = {
        'databaseURL': FIREBASE_CONFIG["databaseURL"],
        # Agrega otras configuraciones si son necesarias
    }
    
    # Inicializar la app de Firebase
    firebase_admin.initialize_app(cred, firebase_config)

def get_db():
    return db