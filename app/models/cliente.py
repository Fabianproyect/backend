from app.extensions import db
from datetime import datetime

class Cliente(db.Model):
    __tablename__ = 'clientes'
    
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id', ondelete='CASCADE'), primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    fecha_nacimiento = db.Column(db.Date)
    telefono = db.Column(db.String(20))
    
    preferencias = db.Column(db.Text)
    creado_en = db.Column(db.DateTime, server_default=db.func.now())
    actualizado_en = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())
    eliminado = db.Column(db.Boolean, default=False)

    # Relaciones
    usuario = db.relationship('User', back_populates='cliente')
    notas = db.relationship('NotaCliente', back_populates='cliente', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'usuario_id': self.usuario_id,
            'nombre': self.nombre,
            'apellido': self.apellido,
            'fecha_nacimiento': self.fecha_nacimiento.isoformat() if self.fecha_nacimiento else None,
            'telefono': self.telefono,
            'preferencias': self.preferencias,
            'creado_en': self.creado_en.isoformat() if self.creado_en else None,
            'actualizado_en': self.actualizado_en.isoformat() if self.actualizado_en else None
        }