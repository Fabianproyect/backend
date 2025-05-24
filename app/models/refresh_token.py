from app.extensions import db

class RefreshToken(db.Model):
    __tablename__ = 'refresh_tokens'
    
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    token = db.Column(db.String(255), nullable=False)
    fecha_expiracion = db.Column(db.DateTime, nullable=False)
    revocado = db.Column(db.Boolean, default=False)
    creado_en = db.Column(db.DateTime, server_default=db.func.now())
    actualizado_en = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())
    eliminado = db.Column(db.Boolean, default=False)

    usuario = db.relationship('User', back_populates='refresh_tokens')

    def to_dict(self):
        return {
            'id': self.id,
            'usuario_id': self.usuario_id,
            'fecha_expiracion': self.fecha_expiracion.isoformat() if self.fecha_expiracion else None,
            'revocado': self.revocado
        }