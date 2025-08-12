import os

class Config:
    SQLALCHEMY_DATABASE_URI = "sqlite:///OCTEC.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv("SECRET_KEY")