from app.extensions import db

class Profesional(db.Model):
    __tablename__ = 'profesionales'
    
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id', ondelete='CASCADE'), primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    especialidad = db.Column(db.String(100))  # Almacena la rama
    descripcion = db.Column(db.Text)
    experiencia = db.Column(db.Text)
    telefono = db.Column(db.String(20))
    genero = db.Column(db.String(20), nullable=False)
    calificacion_promedio = db.Column(db.Numeric(3, 2), default=0.00)
    creado_en = db.Column(db.DateTime, server_default=db.func.now())
    actualizado_en = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())
    eliminado = db.Column(db.Boolean, default=False)

    # Relaciones
    usuario = db.relationship('User', back_populates='profesional')
    imagenes = db.relationship('ImagenProfesional', back_populates='profesional', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'usuario_id': self.usuario_id,
            'nombre': self.nombre,
            'apellido': self.apellido,
            'especialidad': self.especialidad,
            'descripcion': self.descripcion,
            'experiencia': self.experiencia,
            'telefono': self.telefono,
            'genero': self.genero,
            'calificacion_promedio': float(self.calificacion_promedio) if self.calificacion_promedio else None,
            'creado_en': self.creado_en.isoformat() if self.creado_en else None,
            'actualizado_en': self.actualizado_en.isoformat() if self.actualizado_en else None,
            'eliminado': self.eliminado
        }