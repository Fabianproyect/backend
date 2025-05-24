from werkzeug.security import generate_password_hash
from app.extensions import db
from app.models import User
from datetime import datetime

class AuthService:
    @staticmethod
    def create_user(
        username,
        email,
        password,
        tipo='cliente',  # Valor por defecto
        nombre_completo=None,
        edad=None,
        ciudad=None,
        telefono=None
    ):
        # Validaciones básicas
        if User.query.filter_by(username=username).first():
            raise ValueError('El nombre de usuario ya está en uso')
        if User.query.filter_by(email=email).first():
            raise ValueError('El email ya está registrado')
        if edad and edad < 13:
            raise ValueError('Debes tener al menos 13 años para registrarte')
        
        # Crear nuevo usuario
        new_user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            tipo=tipo,
            nombre_completo=nombre_completo,
            edad=edad,
            ciudad=ciudad,
            telefono=telefono,
            fecha_registro=datetime.utcnow(),
            activo=True
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        return new_user

    # ... (otros métodos existentes)