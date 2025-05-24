from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
from .extensions import db, migrate, jwt
from .config import Config

def create_app():
    app = Flask(__name__)
    
    # Cargar configuración primero
    app.config.from_object(Config)
    load_dotenv()
    
    # Sobreescribir configuraciones específicas si es necesario
    app.config.update({
        'SQLALCHEMY_DATABASE_URI': os.getenv('DATABASE_URL', 'mysql://laravel_user:Mizaptech123*@localhost/test'),
        'JWT_COOKIE_CSRF_PROTECT': False,
        'JWT_HEADER_TYPE': '',
    })
    
    # Configuración CORS más flexible para desarrollo
    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://127.0.0.1:5500", "http://localhost:*","https://2ndcn790-5500.use2.devtunnels.ms","https://*.devtunnels.ms","https://2ndcn790-5000.use2.devtunnels.ms"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True,
            "max_age": 600
        }
    })
    
    # Inicialización de extensiones
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    
    # Configuración de rutas para uploads (asegurando ruta absoluta)
    app.config['UPLOAD_FOLDER'] = os.path.abspath(os.path.join(os.path.dirname(__file__), 'app', 'img'))
    
    # Crear directorio de uploads si no existe
    upload_folder = app.config['UPLOAD_FOLDER']
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
        app.logger.info(f"Created upload directory at: {upload_folder}")
    else:
        app.logger.info(f"Upload directory already exists at: {upload_folder}")
    
    # Debug: Mostrar configuración de rutas
    app.logger.info(f"BASE_DIR: {app.config['UPLOAD_FOLDER']}")
    app.logger.info(f"Contenido del directorio uploads: {os.listdir(upload_folder)}")
    
    # Registrar blueprints
    with app.app_context():
        from .models.user import User
        from .models.profesional import Profesional
        from .models.cliente import Cliente
        from .models.portafolio import Portafolio
        
        from .controllers import (
            auth_controller, 
            profesional_controller, 
            cliente_controller, 
            user_controller,
            portafolio_controller,
            imagen_controller,
            trabajo_controller  # Nuevo controlador
        )
        
        app.register_blueprint(auth_controller.bp)
        app.register_blueprint(profesional_controller.bp)
        app.register_blueprint(cliente_controller.bp)
        app.register_blueprint(user_controller.bp)
        app.register_blueprint(portafolio_controller.bp)
        app.register_blueprint(imagen_controller.bp)
        app.register_blueprint(trabajo_controller.bp)  # Registrar el nuevo blueprint
        
        
        try:
            db.create_all()
            app.logger.info("Tablas de la base de datos creadas correctamente")
        except Exception as e:
            app.logger.error(f"No se pudieron crear tablas: {str(e)}")
    
    register_error_handlers(app)
    return app

def register_error_handlers(app):
    @app.errorhandler(404)
    def not_found_error(error):
        app.logger.warning(f"Recurso no encontrado: {request.url}")
        return jsonify({
            'message': 'Recurso no encontrado',
            'status': 404,
            'path': request.path
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f'Error interno: {str(error)}')
        return jsonify({
            'message': 'Error interno del servidor',
            'status': 500,
            'error': str(error)
        }), 500

    @app.errorhandler(413)
    def request_entity_too_large(error):
        app.logger.warning("Archivo demasiado grande subido")
        return jsonify({
            'message': 'El archivo es demasiado grande (máximo 5MB permitidos)',
            'status': 413
        }), 413