from app.extensions import db

class ImagenProfesional(db.Model):
    __tablename__ = 'imagenes_profesionales'
    
    id = db.Column(db.Integer, primary_key=True)
    profesional_id = db.Column(db.Integer, db.ForeignKey('profesionales.usuario_id'), nullable=False)
    categoria_id = db.Column(db.Integer, db.ForeignKey('categorias_imagenes.id'), nullable=False)
    url_imagen = db.Column(db.String(255), nullable=False)
    titulo = db.Column(db.String(100))
    descripcion = db.Column(db.Text)
    fecha_subida = db.Column(db.DateTime, server_default=db.func.now())
    privada = db.Column(db.Boolean, default=False)
    creado_en = db.Column(db.DateTime, server_default=db.func.now())
    actualizado_en = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())
    eliminado = db.Column(db.Boolean, default=False)

    # Relaciones
    profesional = db.relationship('Profesional', back_populates='imagenes')
    categoria = db.relationship('CategoriaImagen')

    def to_dict(self):
        return {
            'id': self.id,
            'profesional_id': self.profesional_id,
            'categoria_id': self.categoria_id,
            'url_imagen': self.url_imagen,
            'titulo': self.titulo,
            'fecha_subida': self.fecha_subida.isoformat() if self.fecha_subida else None
        }