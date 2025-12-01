import os
from dotenv import load_dotenv
from pathlib import Path
from datetime import timedelta

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path, override=False)

def _bool_env(name, default=False):
    val = os.getenv(name)
    
    if val is None:
        return default
    
    return str(val).lower() in ("1", "true", "yes", "on")

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///OCTEC.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = _bool_env("SQLALCHEMY_ECHO", False)

    SECRET_KEY = os.getenv("SECRET_KEY") or "chave-secreta-desenvolvimento"

    DEBUG = _bool_env("FLASK_DEBUG", True)

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = not DEBUG
    SESSION_COOKIE_SAMESITE = os.getenv("SESSION_COOKIE_SAMESITE", "Lax")

    SESSION_PERMANENT = True
    SESSION_LIFETIME_MINUTES = int(os.getenv("SESSION_LIFETIME_MINUTES", "120"))
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=SESSION_LIFETIME_MINUTES)

    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_DURATION = timedelta(days=int(os.getenv("REMEMBER_COOKIE_DAYS", "7")))
    REMEMBER_COOKIE_SECURE = not DEBUG