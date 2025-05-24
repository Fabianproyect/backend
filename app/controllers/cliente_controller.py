from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token
from app.utils.decorators import validate_json, required_roles
from app.models.user import User
from app.models.cliente import Cliente
from app import db
from datetime import datetime

bp = Blueprint('cliente', __name__, url_prefix='/api/clientes')

@bp.route('/registro', methods=['POST'])
@validate_json({
    'username': {'type': 'string', 'required': True, 'minlength': 3},
    'email': {'type': 'string', 'required': True, 'regex': r'^[^@]+@[^@]+\.[^@]+'},
    'password': {'type': 'string', 'required': True, 'minlength': 8},
    'nombre_completo': {'type': 'string', 'required': True},
    'telefono': {'type': 'string', 'required': True},
    'fecha_nacimiento': {'type': 'string', 'required': False, 'regex': r'^\d{4}-\d{2}-\d{2}$'},
    'ciudad': {'type': 'string', 'required': False},
    'edad': {'type': 'integer', 'required': False, 'min': 13}
})
def registro_cliente():
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
            tipo='cliente',
            nombre_completo=data['nombre_completo'],
            edad=data.get('edad'),
            ciudad=data.get('ciudad'),
            telefono=data['telefono'],
            activo=True
        )
        nuevo_usuario.set_password(data['password'])
        db.session.add(nuevo_usuario)
        db.session.flush()

        # Crear cliente
        nuevo_cliente = Cliente(
            usuario_id=nuevo_usuario.id,
            nombre=nombre,
            apellido=apellido,
            fecha_nacimiento=datetime.strptime(data['fecha_nacimiento'], '%Y-%m-%d').date() if 'fecha_nacimiento' in data else None,
            telefono=data['telefono']
        )
        db.session.add(nuevo_cliente)
        db.session.commit()

        # Generar token JWT
        access_token = create_access_token(identity=nuevo_usuario.id)
        
        return jsonify({
            'message': 'Cliente registrado exitosamente',
            'access_token': access_token,
            'usuario': nuevo_usuario.to_dict(),
            'cliente': nuevo_cliente.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        print(f"Error en registro cliente: {str(e)}")
        return jsonify({'message': 'Error en el servidor'}), 500

@bp.route('/<int:cliente_id>', methods=['GET'])
@jwt_required()
def obtener_cliente(cliente_id):
    try:
        # Verificar si el usuario solicitante es el mismo cliente o un profesional
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        cliente = Cliente.query.get(cliente_id)
        if not cliente or cliente.usuario.eliminado:
            return jsonify({'message': 'Cliente no encontrado'}), 404
        
        # Solo permitir acceso al propio cliente o a un profesional
        if current_user.tipo != 'admin' and current_user_id != cliente_id:
            return jsonify({'message': 'No autorizado'}), 403

        return jsonify({
            'cliente': cliente.to_dict(),
            'usuario': cliente.usuario.to_dict()
        })

    except Exception as e:
        print(f"Error al obtener cliente: {str(e)}")
        return jsonify({'message': 'Error en el servidor'}), 500

@bp.route('/<int:cliente_id>', methods=['PUT'])
@jwt_required()
@validate_json({
    'email': {'type': 'string', 'required': False, 'regex': r'^[^@]+@[^@]+\.[^@]+'},
    'nombre_completo': {'type': 'string', 'required': False},
    'telefono': {'type': 'string', 'required': False},
    'fecha_nacimiento': {'type': 'string', 'required': False, 'regex': r'^\d{4}-\d{2}-\d{2}$'},
    'ciudad': {'type': 'string', 'required': False},
    'edad': {'type': 'integer', 'required': False, 'min': 13},
    'foto_perfil': {'type': 'string', 'required': False},
    'preferencias': {'type': 'string', 'required': False}
})
def actualizar_cliente(cliente_id):
    data = request.get_json()
    
    try:
        # Verificar permisos
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        cliente = Cliente.query.get(cliente_id)
        if not cliente or cliente.usuario.eliminado:
            return jsonify({'message': 'Cliente no encontrado'}), 404
        
        # Solo permitir actualización al propio cliente o a un admin
        if current_user.tipo != 'admin' and current_user_id != cliente_id:
            return jsonify({'message': 'No autorizado'}), 403

        # Actualizar datos de usuario
        if 'email' in data:
            # Verificar si el nuevo email ya existe
            if User.query.filter(User.id != cliente_id, User.email == data['email']).first():
                return jsonify({'message': 'El correo electrónico ya está en uso'}), 400
            cliente.usuario.email = data['email']
        
        if 'nombre_completo' in data:
            cliente.usuario.nombre_completo = data['nombre_completo']
            # Actualizar también nombre y apellido en cliente
            partes_nombre = data['nombre_completo'].split(' ', 1)
            cliente.nombre = partes_nombre[0]
            cliente.apellido = partes_nombre[1] if len(partes_nombre) > 1 else ""
        
        if 'telefono' in data:
            cliente.usuario.telefono = data['telefono']
            cliente.telefono = data['telefono']
        
        if 'ciudad' in data:
            cliente.usuario.ciudad = data['ciudad']
        
        if 'edad' in data:
            cliente.usuario.edad = data['edad']

        # Actualizar datos específicos de cliente
        if 'fecha_nacimiento' in data:
            cliente.fecha_nacimiento = datetime.strptime(data['fecha_nacimiento'], '%Y-%m-%d').date()
        
        if 'preferencias' in data:
            cliente.preferencias = data['preferencias']

        cliente.usuario.actualizado_en = datetime.utcnow()
        db.session.commit()

        return jsonify({
            'message': 'Cliente actualizado exitosamente',
            'cliente': cliente.to_dict(),
            'usuario': cliente.usuario.to_dict()
        })

    except Exception as e:
        db.session.rollback()
        print(f"Error al actualizar cliente: {str(e)}")
        return jsonify({'message': 'Error en el servidor'}), 500

@bp.route('/<int:cliente_id>', methods=['DELETE'])
@jwt_required()
@required_roles(['admin'])
def eliminar_cliente(cliente_id):
    try:
        cliente = Cliente.query.get(cliente_id)
        if not cliente:
            return jsonify({'message': 'Cliente no encontrado'}), 404

        # Eliminación lógica
        cliente.usuario.eliminado = True
        cliente.eliminado = True
        cliente.usuario.activo = False
        cliente.usuario.actualizado_en = datetime.utcnow()
        
        db.session.commit()

        return jsonify({'message': 'Cliente eliminado exitosamente'})

    except Exception as e:
        db.session.rollback()
        print(f"Error al eliminar cliente: {str(e)}")
        return jsonify({'message': 'Error en el servidor'}), 500