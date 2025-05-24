from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from app.utils.decorators import validate_json
from app.models.user import User
from app.models.profesional import Profesional
from app import db

bp = Blueprint('profesional', __name__, url_prefix='/api/profesionales')

@bp.route('/registro', methods=['POST'])
@validate_json({
    'username': {'type': 'string', 'required': True, 'minlength': 3},
    'email': {'type': 'string', 'required': True, 'regex': r'^[^@]+@[^@]+\.[^@]+'},
    'password': {'type': 'string', 'required': True, 'minlength': 8},
    'rama': {
        'type': 'string', 
        'required': True, 
        'allowed': ['tatuador', 'barbero', 'estilista', 'perforador']
    },
    'nombre_completo': {'type': 'string', 'required': True},
    'telefono': {'type': 'string', 'required': True},
    'ciudad': {'type': 'string', 'required': False},
    'edad': {'type': 'integer', 'required': False, 'min': 13},
    'genero': {
        'type': 'string',
        'required': True,
        'allowed': ['masculino', 'femenino', 'otro', 'prefiero_no_decir']
    },
    'descripcion': {'type': 'string', 'required': False},
    'experiencia': {'type': 'string', 'required': False}
})
def registro_profesional():
    data = request.get_json()
    
    try:
        # Verificar si usuario o email ya existen
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'message': 'El nombre de usuario ya está en uso'}), 400
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'message': 'El correo electrónico ya está registrado'}), 400

        # Dividir nombre_completo
        partes_nombre = data['nombre_completo'].split(' ', 1)
        nombre = partes_nombre[0]
        apellido = partes_nombre[1] if len(partes_nombre) > 1 else ""

        # Crear usuario
        nuevo_usuario = User(
            username=data['username'],
            email=data['email'],
            tipo='profesional',
            nombre_completo=data['nombre_completo'],
            edad=data.get('edad'),
            ciudad=data.get('ciudad'),
            telefono=data['telefono'],
            genero=data['genero'],
            activo=True
        )
        nuevo_usuario.set_password(data['password'])
        db.session.add(nuevo_usuario)
        db.session.flush()

        # Crear profesional
        nuevo_profesional = Profesional(
            usuario_id=nuevo_usuario.id,
            nombre=nombre,
            apellido=apellido,
            especialidad=data['rama'],
            telefono=data['telefono'],
            genero=data['genero'],
            descripcion=data.get('descripcion'),
            experiencia=data.get('experiencia')
        )
        db.session.add(nuevo_profesional)
        db.session.commit()

        # Generar token JWT
        access_token = create_access_token(identity=nuevo_usuario.id)
        
        return jsonify({
            'message': 'Profesional registrado exitosamente',
            'access_token': access_token,
            'usuario': nuevo_usuario.to_dict(),
            'profesional': nuevo_profesional.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        print(f"Error en registro profesional: {str(e)}")
        return jsonify({'message': 'Error en el servidor'}), 500