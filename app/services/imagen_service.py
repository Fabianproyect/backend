from app.extensions import db
from app.models import ImagenProfesional, CategoriaImagen

class ImagenService:
    @staticmethod
    def get_imagenes_profesional(profesional_id):
        return ImagenProfesional.query.filter_by(
            profesional_id=profesional_id, 
            eliminado=False
        ).all()

    @staticmethod
    def soft_delete_imagen(imagen_id):
        imagen = ImagenProfesional.query.get_or_404(imagen_id)
        imagen.eliminado = True
        db.session.commit()
        return imagen

    @staticmethod
    def count_by_categoria():
        return db.session.query(
            CategoriaImagen.nombre,
            db.func.count(ImagenProfesional.id)
        ).join(
            ImagenProfesional,
            CategoriaImagen.id == ImagenProfesional.categoria_id
        ).filter(
            CategoriaImagen.eliminado == False,
            ImagenProfesional.eliminado == False
        ).group_by(CategoriaImagen.id).all()