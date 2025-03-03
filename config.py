
import os

class Config:
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', '123456')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    if os.getenv('APP_ENV') == 'docker':
        # Configuración para el entorno Docker
        SQLALCHEMY_DATABASE_URI = 'sqlite:///app.db'
    else:
        # Configuración para el entorno local
        SQLALCHEMY_DATABASE_URI = 'sqlite:///C:/Users/gayar/Personal_Project/RepoP0/app.db'



