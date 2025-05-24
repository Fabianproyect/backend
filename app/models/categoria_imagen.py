from app.extensions import db

class CategoriaImagen(db.Model):
    __tablename__ = 'categorias_imagenes'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    descripcion = db.Column(db.Text)
    padre_id = db.Column(db.Integer, db.ForeignKey('categorias_imagenes.id'))
    creado_en = db.Column(db.DateTime, server_default=db.func.now())
    actualizado_en = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())
    eliminado = db.Column(db.Boolean, default=False)

    # Relación con sí misma para jerarquía
    subcategorias = db.relationship('CategoriaImagen')