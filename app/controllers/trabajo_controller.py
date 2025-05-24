from flask import Blueprint, request, jsonify, current_app
import os
import json
from datetime import datetime
from uuid import uuid4

bp = Blueprint('trabajo', __name__, url_prefix='/api/trabajos')

# Configuración de rutas
TRABAJOS_JSON_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'trabajos.json')

def ensure_trabajos_file():
    """Asegura que el archivo JSON y su directorio existan con estructura inicial"""
    try:
        # Crear directorio si no existe
        os.makedirs(os.path.dirname(TRABAJOS_JSON_PATH), exist_ok=True)
        
        # Crear archivo con estructura inicial si no existe
        if not os.path.exists(TRABAJOS_JSON_PATH):
            initial_data = {
                "trabajos": [],
                "metadata": {
                    "creado_en": datetime.now().isoformat(),
                    "ultima_actualizacion": datetime.now().isoformat(),
                    "total_trabajos": 0,
                    "total_activos": 0
                }
            }
            with open(TRABAJOS_JSON_PATH, 'w', encoding='utf-8') as f:
                json.dump(initial_data, f, indent=2, ensure_ascii=False)
            current_app.logger.info(f"Archivo trabajos.json creado en: {TRABAJOS_JSON_PATH}")
    except Exception as e:
        current_app.logger.error(f"Error al crear archivo trabajos.json: {str(e)}")
        raise

def read_trabajos():
    """Lee todos los trabajos del archivo JSON, creándolo si no existe"""
    try:
        ensure_trabajos_file()
        with open(TRABAJOS_JSON_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
            # Validar estructura básica
            if 'trabajos' not in data:
                data['trabajos'] = []
            if 'metadata' not in data:
                data['metadata'] = {
                    "creado_en": datetime.now().isoformat(),
                    "ultima_actualizacion": datetime.now().isoformat(),
                    "total_trabajos": len(data['trabajos']),
                    "total_activos": len([t for t in data['trabajos'] if t.get('estado') == 'activo'])
                }
                
            return data
    except Exception as e:
        current_app.logger.error(f"Error al leer trabajos.json: {str(e)}")
        return {"trabajos": [], "metadata": {
            "creado_en": datetime.now().isoformat(),
            "ultima_actualizacion": datetime.now().isoformat(),
            "total_trabajos": 0,
            "total_activos": 0
        }}

def write_trabajos(data):
    """Escribe los trabajos en el archivo JSON con manejo de errores"""
    try:
        ensure_trabajos_file()
        
        # Actualizar metadatos
        if 'metadata' not in data:
            data['metadata'] = {}
        
        data['metadata']['ultima_actualizacion'] = datetime.now().isoformat()
        data['metadata']['total_trabajos'] = len(data.get('trabajos', []))
        data['metadata']['total_activos'] = len([t for t in data.get('trabajos', []) if t.get('estado') == 'activo'])
        
        with open(TRABAJOS_JSON_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        current_app.logger.error(f"Error al escribir en trabajos.json: {str(e)}")
        raise

@bp.route('/', methods=['GET'])
def obtener_todos():
    """Obtener todos los trabajos (públicos)"""
    try:
        data = read_trabajos()
        trabajos_activos = [t for t in data['trabajos'] if t.get('estado') == 'activo']
        
        return jsonify({
            'success': True,
            'data': trabajos_activos,
            'count': len(trabajos_activos),
            'metadata': data.get('metadata', {})
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al obtener trabajos: {str(e)}'
        }), 500

@bp.route('/usuario/<int:usuario_id>', methods=['GET'])
def obtener_por_usuario(usuario_id):
    """Obtener trabajos de un usuario específico (cliente o profesional)"""
    try:
        data = read_trabajos()
        
        # Filtrar trabajos donde el usuario es cliente o profesional
        trabajos_usuario = [
            t for t in data['trabajos'] 
            if (t.get('cliente_id') == usuario_id or t.get('profesional_id') == usuario_id)
            and t.get('estado') != 'eliminado'
        ]
        
        return jsonify({
            'success': True,
            'data': trabajos_usuario,
            'count': len(trabajos_usuario)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al obtener trabajos del usuario: {str(e)}'
        }), 500

@bp.route('/', methods=['POST'])
def crear_trabajo():
    """Crear un nuevo trabajo relacionando cliente y profesional"""
    try:
        trabajo_data = request.get_json()
        if not trabajo_data:
            return jsonify({
                'success': False,
                'message': 'No se proporcionaron datos'
            }), 400
        
        # Validación de campos requeridos
        required_fields = ['titulo', 'descripcion', 'cliente_id', 'profesional_id']
        for field in required_fields:
            if field not in trabajo_data:
                return jsonify({
                    'success': False,
                    'message': f'Falta el campo requerido: {field}'
                }), 400
        
        data = read_trabajos()
        
        nuevo_trabajo = {
            'id': str(uuid4()),
            'cliente_id': trabajo_data['cliente_id'],
            'profesional_id': trabajo_data['profesional_id'],
            'fecha_creacion': datetime.now().isoformat(),
            'fecha_actualizacion': datetime.now().isoformat(),
            'estado': 'activo',
            'titulo': trabajo_data['titulo'],
            'descripcion': trabajo_data['descripcion'],
            'categoria': trabajo_data.get('categoria', 'general'),
            'calificacion': None,
            'comentario_cliente': None,
            'comentario_profesional': None
        }
        
        data['trabajos'].append(nuevo_trabajo)
        write_trabajos(data)
        
        return jsonify({
            'success': True,
            'message': 'Trabajo creado exitosamente',
            'data': nuevo_trabajo
        }), 201
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al crear trabajo: {str(e)}'
        }), 500

@bp.route('/<string:trabajo_id>', methods=['PUT'])
def actualizar_trabajo(trabajo_id):
    """Actualizar un trabajo existente"""
    try:
        trabajo_data = request.get_json()
        if not trabajo_data:
            return jsonify({
                'success': False,
                'message': 'No se proporcionaron datos'
            }), 400
        
        data = read_trabajos()
        trabajo = next((t for t in data['trabajos'] if t['id'] == trabajo_id), None)
        
        if not trabajo:
            return jsonify({
                'success': False,
                'message': 'Trabajo no encontrado'
            }), 404
        
        # Campos permitidos para actualización
        campos_permitidos = [
            'titulo', 'descripcion', 'categoria', 
            'estado', 'calificacion', 
            'comentario_cliente', 'comentario_profesional'
        ]
        
        for campo in campos_permitidos:
            if campo in trabajo_data:
                trabajo[campo] = trabajo_data[campo]
        
        trabajo['fecha_actualizacion'] = datetime.now().isoformat()
        write_trabajos(data)
        
        return jsonify({
            'success': True,
            'message': 'Trabajo actualizado exitosamente',
            'data': trabajo
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al actualizar trabajo: {str(e)}'
        }), 500

@bp.route('/<string:trabajo_id>', methods=['DELETE'])
def eliminar_trabajo(trabajo_id):
    """Eliminar un trabajo (borrado lógico)"""
    try:
        data = read_trabajos()
        trabajo = next((t for t in data['trabajos'] if t['id'] == trabajo_id), None)
        
        if not trabajo:
            return jsonify({
                'success': False,
                'message': 'Trabajo no encontrado'
            }), 404
        
        # Borrado lógico
        trabajo['estado'] = 'eliminado'
        trabajo['fecha_actualizacion'] = datetime.now().isoformat()
        write_trabajos(data)
        
        return jsonify({
            'success': True,
            'message': 'Trabajo marcado como eliminado'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al eliminar trabajo: {str(e)}'
        }), 500

@bp.route('/profesional/<int:profesional_id>', methods=['GET'])
def obtener_por_profesional(profesional_id):
    """Obtener trabajos de un profesional específico"""
    try:
        data = read_trabajos()
        trabajos_profesional = [
            t for t in data['trabajos'] 
            if t.get('profesional_id') == profesional_id 
            and t.get('estado') != 'eliminado'
        ]
        
        return jsonify({
            'success': True,
            'data': trabajos_profesional,
            'count': len(trabajos_profesional)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al obtener trabajos del profesional: {str(e)}'
        }), 500