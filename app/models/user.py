from app.extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(db.Model):
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    tipo = db.Column(db.Enum('cliente', 'profesional', name='tipo_usuario'), nullable=False)
    nombre_completo = db.Column(db.String(100))
    genero = db.Column(db.String(20))
    edad = db.Column(db.Integer)
    ciudad = db.Column(db.String(100))
    telefono = db.Column(db.String(20))
    fecha_registro = db.Column(db.DateTime, server_default=db.func.now())
    ultimo_login = db.Column(db.DateTime)
    activo = db.Column(db.Boolean, default=True)
    creado_en = db.Column(db.DateTime, server_default=db.func.now())
    actualizado_en = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())
    eliminado = db.Column(db.Boolean, default=False)
    foto_perfil = db.Column(db.String(255), nullable=True)  # ÚNICO lugar donde se almacena la foto de perfil
    
    # Relaciones
    cliente = db.relationship('Cliente', back_populates='usuario', uselist=False, cascade='all, delete-orphan')
    profesional = db.relationship('Profesional', back_populates='usuario', uselist=False, cascade='all, delete-orphan')
    refresh_tokens = db.relationship('RefreshToken', back_populates='usuario', cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        """Retorna todos los datos del usuario (para uso interno/privado)"""
        data = {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'tipo': self.tipo,
            'nombre_completo': self.nombre_completo,
            'genero': self.genero,
            'edad': self.edad,
            'ciudad': self.ciudad,
            'telefono': self.telefono,
            'foto_perfil': self.get_foto_url(),  # La foto siempre viene de usuarios.foto_perfil
            'activo': self.activo,
            'fecha_registro': self.fecha_registro.isoformat() if self.fecha_registro else None,
            'ultimo_login': self.ultimo_login.isoformat() if self.ultimo_login else None,
            'creado_en': self.creado_en.isoformat() if self.creado_en else None,
            'actualizado_en': self.actualizado_en.isoformat() if self.actualizado_en else None
        }
        
        # Agregar datos específicos según el tipo de usuario
        if self.tipo == 'profesional' and self.profesional:
            data.update({
                'especialidad': self.profesional.especialidad,
                'descripcion': self.profesional.descripcion,
                'experiencia': self.profesional.experiencia,
                'calificacion_promedio': float(self.profesional.calificacion_promedio) if self.profesional.calificacion_promedio else 0.0,
                # NOTA: No incluir foto_perfil aquí, ya viene del usuario
            })
        elif self.tipo == 'cliente' and self.cliente:
            data.update({
                'fecha_nacimiento': self.cliente.fecha_nacimiento.isoformat() if self.cliente.fecha_nacimiento else None,
                'preferencias': self.cliente.preferencias
                # NOTA: No incluir foto_perfil aquí, ya viene del usuario
            })
            
        return data

    def to_public_dict(self):
        """Retorna solo los datos públicos del usuario"""
        data = {
            'id': self.id,
            'username': self.username,
            'tipo': self.tipo,
            'nombre_completo': self.nombre_completo,
            'ciudad': self.ciudad,
            'foto_perfil': self.get_foto_url(),  # La foto siempre viene de usuarios.foto_perfil
            'fecha_registro': self.fecha_registro.isoformat() if self.fecha_registro else None
        }
        
        # Agregar datos públicos específicos para profesionales
        if self.tipo == 'profesional' and self.profesional:
            data.update({
                'especialidad': self.profesional.especialidad,
                'calificacion_promedio': float(self.profesional.calificacion_promedio) if self.profesional.calificacion_promedio else 0.0
            })
            
        return data

    def to_profile_dict(self):
        """Retorna datos extendidos para el perfil propio"""
        data = self.to_public_dict()
        data.update({
            'genero': self.genero,
            'edad': self.edad,
            'telefono': self.telefono,
            'email': self.email
        })
        
        # Agregar datos específicos según el tipo de usuario
        if self.tipo == 'profesional' and self.profesional:
            data.update({
                'especialidad': self.profesional.especialidad,
                'descripcion': self.profesional.descripcion,
                'experiencia': self.profesional.experiencia,
                'calificacion_promedio': float(self.profesional.calificacion_promedio) if self.profesional.calificacion_promedio else 0.0
            })
        elif self.tipo == 'cliente' and self.cliente:
            data.update({
                'fecha_nacimiento': self.cliente.fecha_nacimiento.isoformat() if self.cliente.fecha_nacimiento else None,
                'preferencias': self.cliente.preferencias
            })
            
        return data

    def get_foto_url(self):
        """Genera la URL completa para la foto de perfil (siempre desde usuarios.foto_perfil)"""
        if not self.foto_perfil:
            return None
        return f"/api/users/{self.id}/photo"

    def update_profile_picture(self, filename):
        """Actualiza la foto de perfil (solo en usuarios.foto_perfil)"""
        self.foto_perfil = filename
        db.session.commit()

    def update_last_login(self):
        """Actualiza la fecha del último login"""
        self.ultimo_login = datetime.utcnow()
        db.session.commit()