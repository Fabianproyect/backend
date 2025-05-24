from functools import wraps
from flask import request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.models import User
import re

def validate_json(schema):
    """
    Decorador para validar el JSON de entrada contra un esquema definido.
    
    Args:
        schema (dict): Esquema de validación con reglas para cada campo
        
    Ejemplo de esquema:
    {
        'username': {'type': 'string', 'required': True},
        'email': {'type': 'string', 'regex': r'^[^@]+@[^@]+\.[^@]+'},
        'age': {'type': 'integer', 'min': 18}
    }
    """
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if not request.is_json:
                return jsonify({'message': 'Se esperaba contenido JSON'}), 400
            
            data = request.get_json()
            errors = {}
            
            for field, rules in schema.items():
                if rules.get('required', False) and field not in data:
                    errors[field] = 'Este campo es requerido'
                    continue
                
                if field not in data:
                    continue
                
                value = data[field]
                
                expected_type = rules.get('type')
                if expected_type:
                    type_valid = False
                    if expected_type == 'string':
                        type_valid = isinstance(value, str)
                    elif expected_type == 'integer':
                        type_valid = isinstance(value, int) and not isinstance(value, bool)
                    elif expected_type == 'boolean':
                        type_valid = isinstance(value, bool)
                    elif expected_type == 'list':
                        type_valid = isinstance(value, list)
                    elif expected_type == 'dict':
                        type_valid = isinstance(value, dict)
                    
                    if not type_valid:
                        errors[field] = f'Se esperaba un tipo {expected_type}'
                        continue
                
                if 'minlength' in rules and isinstance(value, str):
                    if len(value) < rules['minlength']:
                        errors[field] = f'Debe tener al menos {rules["minlength"]} caracteres'
                
                if 'min' in rules and isinstance(value, (int, float)):
                    if value < rules['min']:
                        errors[field] = f'El valor mínimo permitido es {rules["min"]}'
                
                if 'regex' in rules and isinstance(value, str):
                    if not re.match(rules['regex'], value):
                        errors[field] = 'Formato inválido'
                
                if 'allowed' in rules:
                    if value not in rules['allowed']:
                        errors[field] = f'Valor no permitido. Opciones: {", ".join(rules["allowed"])}'
            
            if errors:
                return jsonify({
                    'message': 'Error de validación',
                    'errors': errors
                }), 400
            
            return f(*args, **kwargs)
        return wrapper
    return decorator

def api_key_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-KEY')
        if not api_key or api_key != current_app.config['API_KEY']:
            return jsonify({'message': 'API key inválida o faltante'}), 401
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """
    Decorador para requerir rol de administrador.
    Mantenido por compatibilidad con código existente.
    """
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        if not user or user.tipo != 'admin':
            return jsonify({'message': 'Acceso denegado: se requiere rol de administrador'}), 403
        return f(*args, **kwargs)
    return decorated_function

def required_roles(*roles):
    """
    Decorador para verificar múltiples roles.
    Uso: @required_roles('admin', 'profesional', 'cliente')
    
    Args:
        *roles: Roles permitidos para acceder al endpoint
    """
    def decorator(f):
        @wraps(f)
        @jwt_required()
        def decorated_function(*args, **kwargs):
            current_user_id = get_jwt_identity()
            user = User.query.get(current_user_id)
            
            if not user:
                return jsonify({'message': 'Usuario no encontrado'}), 404
                
            # Verificar si el usuario tiene alguno de los roles requeridos
            if user.tipo not in roles:
                allowed_roles = ", ".join([f"'{r}'" for r in roles])
                return jsonify({
                    'message': f'Acceso denegado: se requiere uno de estos roles: {allowed_roles}',
                    'required_roles': list(roles),
                    'current_role': user.tipo
                }), 403
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def roles_from_jwt_required(*roles):
    """
    Versión alternativa que verifica roles desde los JWT claims.
    Requiere que los tokens JWT incluyan un claim 'roles'.
    
    Uso: @roles_from_jwt_required('admin', 'editor')
    """
    def decorator(f):
        @wraps(f)
        @jwt_required()
        def decorated_function(*args, **kwargs):
            claims = get_jwt()
            user_roles = claims.get('roles', [])
            
            if not any(role in user_roles for role in roles):
                allowed_roles = ", ".join([f"'{r}'" for r in roles])
                return jsonify({
                    'message': f'Acceso denegado: se requiere uno de estos roles en el token JWT: {allowed_roles}',
                    'required_roles': list(roles),
                    'current_roles': user_roles
                }), 403
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator