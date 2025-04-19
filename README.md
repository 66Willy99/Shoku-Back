# Shoku-App Backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:

venv\Scripts\activate

# Linux/MacOS:

source venv/bin/activate

## instalar las dependencias

pip install fastapi[all]

## Correr el Servidor 

uvicorn main:app (--reload si es para Dev)


