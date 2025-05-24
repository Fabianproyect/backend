from flask import Blueprint, jsonify
from app import db
from sqlalchemy import text

bp = Blueprint('portafolio', __name__, url_prefix='/api/portafolio')

@bp.route('/publico', methods=['GET'])
def obtener_portafolios_publicos():
    """Endpoint para obtener portafolios públicos de profesionales"""
    try:
        # Consulta SQL adaptada para devolver diccionarios
        sql_query = text("""
        SELECT 
            p.usuario_id,
            p.nombre,
            p.apellido,
            p.especialidad,
            p.descripcion,
            p.experiencia,
            p.calificacion_promedio,
            p.genero,
            u.id,
            u.nombre_completo,
            u.username,
            u.email,
            u.ciudad,
            u.telefono,
            u.foto_perfil,
            u.fecha_registro,
            ip.id as imagen_id,
            ip.titulo,
            ip.descripcion as imagen_descripcion,
            CONCAT('/api/images/', ip.id) as imagen_url,
            (SELECT COUNT(*) FROM interacciones WHERE profesional_id = p.usuario_id AND tipo = 'visualizacion') as trabajos_realizados,
            (SELECT COUNT(DISTINCT cliente_id) FROM interacciones WHERE profesional_id = p.usuario_id AND tipo = 'contacto') as clientes_atendidos
        FROM 
            profesionales p
        JOIN 
            usuarios u ON p.usuario_id = u.id
        LEFT JOIN 
            imagenes_profesionales ip ON ip.profesional_id = p.usuario_id
        WHERE 
            u.activo = 1 AND u.eliminado = 0 AND p.eliminado = 0
        """)
        
        # Ejecutar consulta con return_as_dict=True
        result = db.session.execute(sql_query).mappings()
        profesionales = {}
        
        for row in result:
            usuario_id = row['usuario_id']
            
            if usuario_id not in profesionales:
                profesionales[usuario_id] = {
                    'usuario_id': usuario_id,
                    'nombre': row['nombre'],
                    'apellido': row['apellido'],
                    'especialidad': row['especialidad'],
                    'descripcion': row['descripcion'],
                    'experiencia': row['experiencia'],
                    'calificacion_promedio': float(row['calificacion_promedio']) if row['calificacion_promedio'] else None,
                    'genero': row['genero'],
                    'usuario': {
                        'id': row['id'],
                        'nombre_completo': row['nombre_completo'],
                        'username': row['username'],
                        'email': row['email'],
                        'ciudad': row['ciudad'],
                        'telefono': row['telefono'],
                        'foto_perfil': row['foto_perfil'],
                        'fecha_registro': row['fecha_registro'].isoformat() if row['fecha_registro'] else None
                    },
                    'portafolio': [],
                    'estadisticas': {
                        'trabajos_realizados': row['trabajos_realizados'] or 0,
                        'clientes_atendidos': row['clientes_atendidos'] or 0
                    }
                }
            
            if row['imagen_id']:
                profesionales[usuario_id]['portafolio'].append({
                    'id': row['imagen_id'],
                    'titulo': row['titulo'],
                    'descripcion': row['imagen_descripcion'],
                    'imagen_url': row['imagen_url']
                })
        
        return jsonify({
            'success': True,
            'data': list(profesionales.values())
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al obtener portafolios públicos: {str(e)}'
        }), 500
        
@bp.route('/<int:usuario_id>', methods=['GET'])
def obtener_portafolio_usuario(usuario_id):
    """Endpoint para obtener el portafolio completo de un profesional específico"""
    try:
        # Consulta SQL para obtener los datos del profesional
        sql_query = text("""
        SELECT 
            p.usuario_id,
            p.nombre,
            p.apellido,
            p.especialidad,
            p.descripcion,
            p.experiencia,
            p.calificacion_promedio,
            p.genero,
            u.id,
            u.nombre_completo,
            u.username,
            u.email,
            u.ciudad,
            u.telefono,
            u.foto_perfil,
            u.fecha_registro,
            ip.id as imagen_id,
            ip.titulo,
            ip.descripcion as imagen_descripcion,
            CONCAT('/api/images/', ip.id) as imagen_url,
            ip.fecha_subida,
            (SELECT COUNT(*) FROM interacciones WHERE profesional_id = p.usuario_id AND tipo = 'visualizacion') as trabajos_realizados,
            (SELECT COUNT(DISTINCT cliente_id) FROM interacciones WHERE profesional_id = p.usuario_id AND tipo = 'contacto') as clientes_atendidos,
            (SELECT COUNT(*) FROM interacciones WHERE profesional_id = p.usuario_id AND tipo = 'favorito') as favoritos
        FROM 
            profesionales p
        JOIN 
            usuarios u ON p.usuario_id = u.id
        LEFT JOIN 
            imagenes_profesionales ip ON ip.profesional_id = p.usuario_id
        WHERE 
            p.usuario_id = :usuario_id AND u.activo = 1 AND u.eliminado = 0 AND p.eliminado = 0
        ORDER BY
            ip.fecha_subida DESC
        """)
        
        # Ejecutar consulta
        result = db.session.execute(sql_query, {'usuario_id': usuario_id}).mappings()
        rows = list(result)
        
        if not rows:
            return jsonify({
                'success': False,
                'message': 'Profesional no encontrado o inactivo'
            }), 404
        
        # Estructurar los datos
        profesional = {
            'usuario_id': rows[0]['usuario_id'],
            'nombre': rows[0]['nombre'],
            'apellido': rows[0]['apellido'],
            'especialidad': rows[0]['especialidad'],
            'descripcion': rows[0]['descripcion'],
            'experiencia': rows[0]['experiencia'],
            'calificacion_promedio': float(rows[0]['calificacion_promedio']) if rows[0]['calificacion_promedio'] else None,
            'genero': rows[0]['genero'],
            'usuario': {
                'id': rows[0]['id'],
                'nombre_completo': rows[0]['nombre_completo'],
                'username': rows[0]['username'],
                'email': rows[0]['email'],
                'ciudad': rows[0]['ciudad'],
                'telefono': rows[0]['telefono'],
                'foto_perfil': rows[0]['foto_perfil'],
                'fecha_registro': rows[0]['fecha_registro'].isoformat() if rows[0]['fecha_registro'] else None
            },
            'portafolio': [],
            'estadisticas': {
                'trabajos_realizados': rows[0]['trabajos_realizados'] or 0,
                'clientes_atendidos': rows[0]['clientes_atendidos'] or 0,
                'favoritos': rows[0]['favoritos'] or 0
            }
        }
        
        # Agregar imágenes del portafolio
        for row in rows:
            if row['imagen_id']:
                profesional['portafolio'].append({
                    'id': row['imagen_id'],
                    'titulo': row['titulo'],
                    'descripcion': row['imagen_descripcion'],
                    'imagen_url': row['imagen_url'],
                    'fecha_subida': row['fecha_subida'].isoformat() if row['fecha_subida'] else None
                })
        
        return jsonify({
            'success': True,
            'data': profesional
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al obtener el portafolio: {str(e)}'
        }), 500
        
@bp.route('/<int:usuario_id>', methods=['PUT'])
def actualizar_portafolio(usuario_id):
    """Endpoint para actualizar el portafolio de un profesional"""
    try:
        # Obtener datos del request
        datos_actualizacion = request.get_json()
        
        if not datos_actualizacion:
            return jsonify({
                'success': False,
                'message': 'No se proporcionaron datos para actualizar'
            }), 400
        
        # Verificar que el usuario existe y es profesional
        profesional = db.session.execute(
            text("SELECT 1 FROM profesionales WHERE usuario_id = :usuario_id AND eliminado = 0"),
            {'usuario_id': usuario_id}
        ).fetchone()
        
        if not profesional:
            return jsonify({
                'success': False,
                'message': 'Profesional no encontrado o inactivo'
            }), 404
        
        # Construir la consulta de actualización dinámica
        campos_permitidos = {
            'nombre', 'apellido', 'especialidad', 
            'descripcion', 'experiencia', 'genero'
        }
        
        set_clauses = []
        params = {'usuario_id': usuario_id}
        
        for campo, valor in datos_actualizacion.items():
            if campo in campos_permitidos:
                set_clauses.append(f"{campo} = :{campo}")
                params[campo] = valor
        
        if not set_clauses:
            return jsonify({
                'success': False,
                'message': 'No se proporcionaron campos válidos para actualizar'
            }), 400
        
        # Actualizar el portafolio
        update_query = text(f"""
            UPDATE portafolios
            SET {', '.join(set_clauses)}, actualizado_en = NOW()
            WHERE usuario_id = :usuario_id
        """)
        
        db.session.execute(update_query, params)
        db.session.commit()
        
        # Obtener el portafolio actualizado para devolverlo
        portafolio_actualizado = db.session.execute(
            text("""
                SELECT * FROM portafolios 
                WHERE usuario_id = :usuario_id
            """),
            {'usuario_id': usuario_id}
        ).mappings().first()
        
        return jsonify({
            'success': True,
            'message': 'Portafolio actualizado exitosamente',
            'data': dict(portafolio_actualizado) if portafolio_actualizado else None
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error al actualizar el portafolio: {str(e)}'
        }), 500