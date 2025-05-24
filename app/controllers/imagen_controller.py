from flask import Blueprint, send_from_directory
import os

bp = Blueprint('imagen', __name__, url_prefix='/api')

# Configura la ruta a tu carpeta de imágenes (ajusta según tu estructura)
IMG_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'app', 'img')

@bp.route('/imagen/<nombre_imagen>')
def servir_imagen(nombre_imagen):
    """Endpoint para servir imágenes desde el servidor"""
    try:
        return send_from_directory(IMG_FOLDER, nombre_imagen)
    except FileNotFoundError:
        return {"success": False, "message": "Imagen no encontrada"}, 404