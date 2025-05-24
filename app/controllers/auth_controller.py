from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    jwt_required, 
    get_jwt_identity,
    create_access_token,
    create_refresh_token,
    get_jwt
)
from app.services.auth_service import AuthService
from app.utils.decorators import api_key_required, validate_json
from app.models import User
from app.extensions import db
import os
from datetime import datetime

bp = Blueprint('auth', __name__, url_prefix='/api/auth')

def check_admin_credentials(username_or_email, password):
    """Verifica si las credenciales coinciden con el admin del .env"""
    admin_username = os.getenv('ADMIN_USERNAME')
    admin_email = os.getenv('ADMIN_EMAIL')
    admin_password = os.getenv('ADMIN_PASSWORD')
    
    # Verificar coincidencia de usuario/email y contraseña
    return ((username_or_email == admin_username or username_or_email == admin_email) 
            and password == admin_password)

def create_admin_payload():
    """Crea el payload JWT para el administrador"""
    return {
        "identity": "admin",
        "is_admin": True,
        "username": os.getenv('ADMIN_USERNAME'),
        "email": os.getenv('ADMIN_EMAIL'),
        "tipo": "admin"
    }

@bp.route('/login', methods=['POST'])
@validate_json({
    'username_or_email': {'type': 'string', 'required': True},
    'password': {'type': 'string', 'required': True}
})
def login():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'message': 'No se proporcionaron datos'}), 400
            
        username_or_email = data.get('username_or_email')
        password = data.get('password')
        
        if not username_or_email or not password:
            return jsonify({'message': 'Se requieren nombre de usuario/email y contraseña'}), 400
        
        # Primero verificar si es el administrador
        if check_admin_credentials(username_or_email, password):
            admin_payload = create_admin_payload()
            
            access_token = create_access_token(identity=admin_payload)
            refresh_token = create_refresh_token(identity=admin_payload)
            
            return jsonify({
                'access_token': access_token,
                'refresh_token': refresh_token,
                'user': {
                    'id': 'admin',
                    'username': os.getenv('ADMIN_USERNAME'),
                    'email': os.getenv('ADMIN_EMAIL'),
                    'tipo': 'admin',
                    'is_admin': True,
                    'foto_perfil': None,
                    'ultimo_login': datetime.utcnow().isoformat()
                }
            }), 200
        
        # Si no es admin, proceder con la lógica normal
        is_email = '@' in username_or_email
        
        if is_email:
            user = User.query.filter_by(email=username_or_email).first()
            error_msg = 'Email no encontrado'
        else:
            user = User.query.filter_by(username=username_or_email).first()
            error_msg = 'Nombre de usuario no encontrado'
        
        if not user:
            return jsonify({
                'message': error_msg,
                'error_type': 'user_not_found'
            }), 404
        
        if not user.check_password(password):
            return jsonify({
                'message': 'Contraseña incorrecta',
                'error_type': 'wrong_password'
            }), 401
        
        if not user.activo:
            return jsonify({
                'message': 'Cuenta desactivada',
                'error_type': 'account_inactive'
            }), 403
        
        user_identity = {
            "identity": str(user.id),
            "is_admin": False,
            "tipo": user.tipo,
            "username": user.username,
            "email": user.email
        }
        
        access_token = create_access_token(identity=user_identity)
        refresh_token = create_refresh_token(identity=user_identity)
        
        user.ultimo_login = db.func.now()
        db.session.commit()
        
        user_dict = user.to_dict()
        user_dict['is_admin'] = False
        
        return jsonify({
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': user_dict
        }), 200

    except Exception as e:
        return jsonify({
            'message': 'Error en el servidor',
            'error': str(e)
        }), 500

@bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    try:
        current_user = get_jwt()
        
        # Si es admin, refrescar con los mismos claims
        if current_user.get('is_admin'):
            new_token = create_access_token(identity=create_admin_payload())
            return jsonify({'access_token': new_token}), 200
        
        # Para usuarios normales
        current_user_id = current_user.get('identity')
        user = User.query.get(int(current_user_id))
        
        if not user:
            return jsonify({'message': 'Usuario no encontrado'}), 404
            
        user_identity = {
            "identity": str(user.id),
            "is_admin": False,
            "tipo": user.tipo,
            "username": user.username,
            "email": user.email
        }
        
        new_token = create_access_token(identity=user_identity)
        return jsonify({'access_token': new_token}), 200
        
    except Exception as e:
        return jsonify({'message': 'Error al refrescar token', 'error': str(e)}), 500

@bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    try:
        # Obtener información del token actual
        jwt_data = get_jwt()
        
        # Aquí puedes agregar lógica para invalidar el token si es necesario
        # Por ejemplo, si tienes una lista de tokens revocados:
        # jti = jwt_data['jti']
        # revoked_store.add(jti)
        
        return jsonify({
            "message": "Sesión cerrada exitosamente",
            "logged_out": True
        }), 200
    except Exception as e:
        return jsonify({
            "message": "Error al cerrar sesión",
            "error": str(e)
        }), 500

@bp.route('/logout', methods=['OPTIONS'])
def logout_options():
    """Endpoint para manejar solicitudes OPTIONS de CORS"""
    return jsonify({}), 200

@bp.route('/verify', methods=['GET'])
@jwt_required()
def verify_token():
    """Endpoint para verificar tokens"""
    try:
        claims = get_jwt()
        
        # Si es admin
        if claims.get('is_admin'):
            return jsonify({
                "valid": True,
                "user": {
                    'id': 'admin',
                    'username': os.getenv('ADMIN_USERNAME'),
                    'email': os.getenv('ADMIN_EMAIL'),
                    'tipo': 'admin',
                    'is_admin': True,
                    'foto_perfil': None
                }
            }), 200
        
        # Si es usuario normal
        current_user_id = claims.get('identity')
        user = User.query.get(int(current_user_id))
        
        if not user:
            return jsonify({"valid": False}), 401
        
        user_dict = user.to_dict()
        user_dict['is_admin'] = False
        
        return jsonify({
            "valid": True,
            "user": user_dict
        }), 200
    except Exception as e:
        return jsonify({"valid": False, "error": str(e)}), 500

@bp.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    try:
        claims = get_jwt()
        
        if claims.get('is_admin'):
            return jsonify({
                'message': f'Administrador autenticado: {claims["username"]}',
                'user': {
                    'id': 'admin',
                    'username': claims['username'],
                    'email': claims['email'],
                    'tipo': 'admin',
                    'is_admin': True
                }
            }), 200
        
        current_user_id = claims.get('identity')
        user = User.query.get(int(current_user_id))
        
        return jsonify({
            'message': f'Usuario autenticado: {user.username}',
            'user': user.to_dict()
        }), 200
    except Exception as e:
        return jsonify({'message': 'Error al verificar usuario', 'error': str(e)}), 500

@bp.route('/admin', methods=['GET'])
@jwt_required()
def admin_only():
    """Endpoint exclusivo para administradores"""
    claims = get_jwt()
    
    if not claims.get('is_admin'):
        return jsonify({
            'message': 'Acceso denegado: se requiere rol de administrador'
        }), 403
    
    return jsonify({
        'message': 'Bienvenido al panel de administración',
        'admin_data': {
            'username': claims['username'],
            'email': claims['email'],
            'last_login': datetime.utcnow().isoformat()
        }
    })

@bp.route('/internal', methods=['GET'])
@api_key_required
def internal():
    return jsonify({'message': 'Acceso API interno autorizado'}), 200