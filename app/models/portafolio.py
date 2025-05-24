from app.extensions import db
from datetime import datetime

class Portafolio(db.Model):
    __tablename__ = 'portafolios'
    
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, nullable=False)
    nombre = db.Column(db.String(100))
    apellido = db.Column(db.String(100))
    especialidad = db.Column(db.String(100))
    descripcion_profesional = db.Column(db.Text)
    experiencia = db.Column(db.Text)
    calificacion_promedio = db.Column(db.Numeric(3, 2), default=0.00)
    genero = db.Column(db.String(20))
    
    # Datos de portafolio
    titulo_trabajo = db.Column(db.String(100))
    descripcion_trabajo = db.Column(db.Text)
    imagen_url = db.Column(db.String(255))
    categoria = db.Column(db.String(50))
    
    # Datos de usuario
    nombre_completo = db.Column(db.String(100))
    username = db.Column(db.String(50))
    email = db.Column(db.String(100))
    ciudad = db.Column(db.String(100))
    telefono = db.Column(db.String(20))
    foto_perfil = db.Column(db.String(255))
    fecha_registro = db.Column(db.DateTime)
    
    # Estadísticas
    trabajos_realizados = db.Column(db.Integer, default=0)
    clientes_atendidos = db.Column(db.Integer, default=0)
    
    # Metadata
    creado_en = db.Column(db.DateTime, default=datetime.utcnow)
    actualizado_en = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    eliminado = db.Column(db.Boolean, default=False)
    
    def to_full_dict(self):
        return {
            'usuario_id': self.usuario_id,
            'nombre': self.nombre,
            'apellido': self.apellido,
            'especialidad': self.especialidad,
            'descripcion': self.descripcion_profesional,
            'experiencia': self.experiencia,
            'calificacion_promedio': float(self.calificacion_promedio) if self.calificacion_promedio else None,
            'genero': self.genero,
            'usuario': {
                'id': self.usuario_id,
                'nombre_completo': self.nombre_completo,
                'username': self.username,
                'email': self.email,
                'ciudad': self.ciudad,
                'telefono': self.telefono,
                'foto_perfil': self.foto_perfil,
                'fecha_registro': self.fecha_registro.isoformat() if self.fecha_registro else None
            },
            'portafolio': [{
                'id': self.id,
                'titulo': self.titulo_trabajo,
                'descripcion': self.descripcion_trabajo,
                'imagen_url': self.imagen_url
            }],
            'estadisticas': {
                'trabajos_realizados': self.trabajos_realizados,
                'clientes_atendidos': self.clientes_atendidos
            }
        }