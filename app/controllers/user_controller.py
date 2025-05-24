from flask import Blueprint, jsonify, request, current_app, send_from_directory
from flask_jwt_extended import get_jwt_identity
from ..models.user import User
from ..extensions import db
import os
import time
from werkzeug.utils import secure_filename

bp = Blueprint('user', __name__, url_prefix='/api/users')

def allowed_file(filename):
    """Verifica si la extensión del archivo es permitida"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'jpg', 'jpeg', 'png'}

# Endpoint público - Listar usuarios
@bp.route('/', methods=['GET'])
def obtener_usuarios():
    try:
        # Solo usuarios no eliminados
        usuarios = User.query.filter_by(eliminado=False, activo=True).all()
        return jsonify([usuario.to_public_dict() for usuario in usuarios]), 200
    except Exception as e:
        current_app.logger.error(f"Error al obtener usuarios: {str(e)}")
        return jsonify({"mensaje": "Error al obtener usuarios"}), 500
    
@bp.route('/profesionales', methods=['GET'])
def obtener_profesionales():
    try:
        from app.models.profesional import Profesional
        
        profesionales = User.query.filter_by(
            tipo='profesional',
            activo=True,
            eliminado=False
        ).options(
            db.joinedload(User.profesional)
        ).all()

        profesionales_data = []
        for user in profesionales:
            if user.profesional:
                prof_data = {
                    'id': user.id,
                    'username': user.username,
                    'nombre_completo': user.nombre_completo,
                    'email': user.email,
                    'genero': user.genero or user.profesional.genero,
                    'edad': user.edad,
                    'ciudad': user.ciudad,
                    'telefono': user.telefono or user.profesional.telefono,
                    'foto_perfil': user.get_foto_url(),
                    'fecha_registro': user.fecha_registro.isoformat() if user.fecha_registro else None,
                    'especialidad': user.profesional.especialidad,
                    'descripcion': user.profesional.descripcion,
                    'experiencia': user.profesional.experiencia,
                    'calificacion_promedio': float(user.profesional.calificacion_promedio) if user.profesional.calificacion_promedio else 0.0,
                    'nombre': user.profesional.nombre,
                    'apellido': user.profesional.apellido
                }
                profesionales_data.append(prof_data)

        return jsonify(profesionales_data), 200
    except Exception as e:
        current_app.logger.error(f"Error al obtener profesionales: {str(e)}")
        return jsonify({"mensaje": "Error al obtener profesionales"}), 500

# Endpoint público - Obtener usuario específico (versión única)
@bp.route('/<int:usuario_id>', methods=['GET'])
def obtener_usuario(usuario_id):
    try:
        usuario = User.query.filter_by(id=usuario_id, eliminado=False, activo=True).first()
        if not usuario:
            return jsonify({"mensaje": "Usuario no encontrado"}), 404
        return jsonify(usuario.to_public_dict()), 200
    except Exception as e:
        current_app.logger.error(f"Error al obtener usuario {usuario_id}: {str(e)}")
        return jsonify({"mensaje": "Error al obtener usuario"}), 500

# Endpoint público - Obtener usuario actual
@bp.route('/yo', methods=['GET'])
def obtener_usuario_actual():
    try:
        # Este endpoint ya no tiene sentido sin autenticación
        return jsonify({"mensaje": "Este endpoint requiere autenticación"}), 401
    except Exception as e:
        current_app.logger.error(f"Error en endpoint /yo: {str(e)}")
        return jsonify({"mensaje": "Error en la solicitud"}), 500

# Endpoint público - Actualizar usuario
@bp.route('/<int:usuario_id>/upload-photo', methods=['POST'])
def subir_foto(usuario_id):
    try:
        # Verificación de que se envió un archivo
        if 'foto' not in request.files:
            return jsonify({"mensaje": "No se proporcionó archivo"}), 400

        archivo = request.files['foto']
        
        if archivo.filename == '':
            return jsonify({"mensaje": "Nombre de archivo vacío"}), 400

        extension = os.path.splitext(archivo.filename)[1].lower()
        if extension not in {'.jpg', '.jpeg', '.png'}:
            return jsonify({
                "mensaje": "Formato de archivo no permitido",
                "formatos_permitidos": ['jpg', 'jpeg', 'png']
            }), 400

        # Validar tamaño
        max_size = 5 * 1024 * 1024
        archivo.seek(0, os.SEEK_END)
        file_size = archivo.tell()
        archivo.seek(0)
        if file_size > max_size:
            return jsonify({
                "mensaje": f"El archivo es demasiado grande (máx. {max_size/1024/1024}MB)",
                "tamaño_actual": f"{file_size/1024/1024:.2f}MB"
            }), 400

        # Generar nombre seguro
        nombre_archivo = f"user_{usuario_id}_{int(time.time())}{extension}"
        nombre_archivo = secure_filename(nombre_archivo)

        # Obtener ruta de uploads desde la configuración
        upload_folder = current_app.config['UPLOAD_FOLDER']
        os.makedirs(upload_folder, exist_ok=True)
        ruta_archivo = os.path.join(upload_folder, nombre_archivo)

        # Guardar archivo
        archivo.save(ruta_archivo)

        # Actualizar base de datos
        usuario = User.query.get_or_404(usuario_id)
        
        # Eliminar foto anterior si existe
        if usuario.foto_perfil:
            try:
                foto_anterior = os.path.join(upload_folder, usuario.foto_perfil)
                if os.path.exists(foto_anterior):
                    os.remove(foto_anterior)
            except Exception as e:
                current_app.logger.error(f"Error al eliminar foto anterior: {str(e)}")

        usuario.foto_perfil = nombre_archivo
        db.session.commit()

        return jsonify({
            "mensaje": "Foto subida correctamente",
            "nombre_archivo": nombre_archivo,
            "foto_url": f"/api/users/{usuario_id}/photo"
        }), 200

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error al subir foto: {str(e)}")
        return jsonify({
            "mensaje": "Error al subir foto",
            "error": str(e)
        }), 500

@bp.route('/<int:usuario_id>/photo', methods=['GET'])
def obtener_foto(usuario_id):
    try:
        usuario = User.query.filter_by(id=usuario_id, eliminado=False, activo=True).first()
        
        if not usuario:
            return jsonify({"mensaje": "Usuario no encontrado"}), 404
            
        upload_folder = current_app.config['UPLOAD_FOLDER']
        default_image = os.path.join(upload_folder, 'default.jpg')
        
        # Si no tiene foto asignada o el archivo no existe, usar default.jpg
        if not usuario.foto_perfil or not os.path.exists(os.path.join(upload_folder, usuario.foto_perfil)):
            if os.path.exists(default_image):
                return send_from_directory(upload_folder, 'default.jpg')
            return jsonify({"mensaje": "No se encontró foto de perfil"}), 404
            
        foto_path = os.path.join(upload_folder, usuario.foto_perfil)
        
        return send_from_directory(upload_folder, usuario.foto_perfil)
        
    except Exception as e:
        current_app.logger.error(f"Error al obtener foto: {str(e)}")
        # Intentar devolver la imagen por defecto si hay error
        if os.path.exists(default_image):
            return send_from_directory(upload_folder, 'default.jpg')
        return jsonify({"mensaje": "Error interno al obtener foto"}), 500

@bp.route('/<int:usuario_id>', methods=['DELETE'])
def eliminar_usuario(usuario_id):
    try:
        # Buscamos el usuario que no esté ya eliminado
        usuario = User.query.filter_by(id=usuario_id, eliminado=False).first()
        
        if not usuario:
            return jsonify({"mensaje": "Usuario no encontrado o ya eliminado"}), 404
        
        # Realizamos el eliminado suave
        usuario.activo = False  # Lo marcamos como inactivo
        usuario.eliminado = True  # Lo marcamos como eliminado
        db.session.commit()
        
        return jsonify({
            "mensaje": "Usuario marcado como eliminado exitosamente",
            "usuario_id": usuario_id,
            "eliminado": True
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error al eliminar usuario {usuario_id}: {str(e)}")
        return jsonify({
            "mensaje": "Error al eliminar usuario",
            "error": str(e)
        }), 500