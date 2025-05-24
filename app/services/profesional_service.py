from werkzeug.security import generate_password_hash
from app.extensions import db
from app.models import User, Profesional
from datetime import datetime

class ProfesionalService:
    @staticmethod
    def registrar_profesional(
        username,
        email,
        password,
        rama,  # tatuador, barbero, estilista, perforador
        nombre_completo,
        telefono,
        ciudad=None,
        edad=None,
        descripcion="",
        experiencia=""
    ):
        """
        Registra un nuevo profesional en el sistema
        
        Args:
            username: Nombre de usuario único
            email: Correo electrónico
            password: Contraseña
            rama: Rama profesional (tatuador, barbero, estilista, perforador)
            nombre_completo: Nombre completo (se separará en nombre y apellido)
            telefono: Número de teléfono
            ciudad: Ciudad de residencia (opcional)
            edad: Edad (opcional)
            descripcion: Descripción del profesional (opcional)
            experiencia: Experiencia del profesional (opcional)
            
        Returns:
            Objeto Profesional registrado
            
        Raises:
            ValueError: Si hay errores de validación
        """
        # Validar rama profesional
        ramas_validas = ['tatuador', 'barbero', 'estilista', 'perforador']
        if rama not in ramas_validas:
            raise ValueError('Rama profesional no válida')

        # Verificar si el usuario ya existe
        if User.query.filter_by(username=username).first():
            raise ValueError('El nombre de usuario ya está en uso')
        if User.query.filter_by(email=email).first():
            raise ValueError('El email ya está registrado')

        # Separar nombre completo en nombre y apellido
        partes_nombre = nombre_completo.split(' ', 1)
        nombre = partes_nombre[0]
        apellido = partes_nombre[1] if len(partes_nombre) > 1 else ""

        # Crear usuario
        usuario = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            tipo='profesional',
            nombre_completo=nombre_completo,
            telefono=telefono,
            ciudad=ciudad,
            edad=edad,
            activo=True
        )
        
        db.session.add(usuario)
        db.session.flush()  # Para obtener el ID del usuario
        
        # Crear profesional (usando especialidad para la rama)
        profesional = Profesional(
            usuario_id=usuario.id,
            nombre=nombre,
            apellido=apellido,
            especialidad=rama,  # Almacenamos la rama en especialidad
            descripcion=descripcion,
            experiencia=experiencia,
            telefono=telefono
        )
        
        db.session.add(profesional)
        db.session.commit()
        
        return profesional