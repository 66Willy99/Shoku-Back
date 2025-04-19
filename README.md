# Shoku-App Backend

# Crea el virtual environment
python -m venv venv

# Activa el virtual environment
# Windows:

venv\Scripts\activate

# Linux/MacOS:

source venv/bin/activate

## instalar las dependencias

pip install fastapi[all]
pip install firebase_admin

## Correr el Servidor 

uvicorn main:app (--reload si es para Dev)


