from fastapi import Depends
from firebase_config import get_db

def get_firebase_db():
    return get_db()