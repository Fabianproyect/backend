import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'secret-key-default')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-default')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'mysql://user:password@localhost/db_name')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_ACCESS_TOKEN_EXPIRES = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 3600))  # 1 hora
    API_KEY = os.getenv('API_KEY', 'default-api-key-for-internal-requests')
    
    # Configuración de uploads
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'img')  # Cambiado de 'app/img'
    ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB

    # Configuración para producción
    if os.getenv('FLASK_ENV') == 'production':
        PROPAGATE_EXCEPTIONS = True