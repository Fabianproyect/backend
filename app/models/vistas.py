from app.extensions import db

class VistaProfesionalesConImagenes(db.Model):
    __tablename__ = 'vista_profesionales_con_imagenes'
    __table_args__ = {'info': dict(is_view=True)}
    
    usuario_id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    apellido = db.Column(db.String(100))
    total_imagenes = db.Column(db.Integer)
    
    @classmethod
    def get_all(cls):
        return db.session.query(cls).all()